# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on Dec 29, 2022

@author: hilee
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_HKP import *
from HK_def import *

from concurrent import futures
import threading
from itertools import cycle

from Libs.hk_field_definition import hk_entries_to_dict
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *


import time as ti

label_list = ["tmc1-a",
              "tmc1-b",
              "tmc2-a",
              "tmc2-b",
              "tmc3-a",
              "tmc3-b",
              "tm-1",
              "tm-2",
              "tm-3",
              "tm-4",
              "tm-5",
              "tm-6",
              "tm-7",
              "tm-8"]
class DtvalueFromLabel:
    def __init__(self, key_to_label, values_dict):
        self._key_to_label = key_to_label
        self._label_to_key = dict((v, k) for (k, v) in list(key_to_label.items()))
        self._values_dict = values_dict

    def __getitem__(self, label):
        k = self._label_to_key.get(label, None)
        return self._values_dict.get(k, DEFAULT_VALUE)

    def as_dict(self):
        return dict((l, float(self._values_dict.get(k, DEFAULT_VALUE)))
                    for l, k in list(self._label_to_key.items()) if l)
            
class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.iam = HK     
        
        self.log = LOG(WORKING_DIR + "IGRINS", "HKP")    
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        self.setWindowTitle("Housekeeping Package 1.0")
        
        # load ini file
        self.ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(self.ini_file)
              
        self.ics_ip_addr = self.cfg.get(MAIN, "ip_addr")
        self.ics_id = self.cfg.get(MAIN, "id")
        self.ics_pwd = self.cfg.get(MAIN, "pwd")
        
        self.hk_main_ex = self.cfg.get(MAIN, 'gui_main_exchange')     
        self.hk_main_q = self.cfg.get(MAIN, 'gui_main_routing_key')
        self.main_hk_ex = self.cfg.get(MAIN, 'main_gui_exchange')
        self.main_hk_q = self.cfg.get(MAIN, 'main_gui_routing_key')
        
        self.hk_sub_ex = self.cfg.get(MAIN, "hk_sub_exchange")     
        self.hk_sub_q = self.cfg.get(MAIN, "hk_sub_routing_key")
                
        self.comport = []
        self.com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "uploader"]
        for name in self.com_list:
            if name != self.com_list[UPLOADER]:
                self.comport.append(self.cfg.get(HK, name + "-port"))
        
        self.power_list = self.cfg.get(HK,'pdu-list').split(',')
        tmp_lst = self.cfg.get(HK,'temp-descriptions').split(',')
        self.temp_list = [s.strip() for s in tmp_lst]
        
        self.Period = int(self.cfg.get(HK,'hk-monitor-intv'))
        
        self.logpath=self.cfg.get(HK,'hk-log-location')
        
        self.alert_label = self.cfg.get(HK, "hk-alert-label")  
        self.alert_temperature = int(self.cfg.get(HK, "hk-alert-temperature"))
        
        self.tb_Monitor.setColumnWidth(0, self.tb_Monitor.width()/32 * 11)
        self.tb_Monitor.setColumnWidth(1, self.tb_Monitor.width()/32 * 7)
        self.tb_Monitor.setColumnWidth(2, self.tb_Monitor.width()/32 * 7)
        self.tb_Monitor.setColumnWidth(3, self.tb_Monitor.width()/32 * 7)
                            
        self.power_status = [OFF for _ in range(PDU_IDX)]
        self.com_status = [True for _ in range(COM_CNT-1)]
                    
        self.init_events()   
        self.show_info()
               
        self.iter_color = cycle(["white", "black"]) 
        self.iter_bgcolor = cycle(["red", "white"])
         
        self.key_to_label = {}
        for k in label_list:
            self.key_to_label[k] = self.cfg.get(HK, k)
            
        self.dtvalue = dict()
        self.dtvalue_from_label = DtvalueFromLabel(self.key_to_label, self.dtvalue)
        
        self.set_point = ["-999" for _ in range(5)]   #set point
        
        self.dpvalue = DEFAULT_VALUE
        for key in self.key_to_label:
            self.dtvalue[key] = DEFAULT_VALUE
        
        self.heatlabel = dict() #heat value
        for i in range(6):
            if i != 4:
                self.heatlabel[label_list[i]] = DEFAULT_VALUE
                                
        # 0 - ENG_TOOLS, 1 - HK_SUB
        self.producer = [None, None]
        
        self.param = ""
        
        self.alert_toggling = False
        self.monitoring_ready = False
        
        self.uploade_start = 0
        self.uploade_status = False
        self.uploader_monitor()
                               
        self.connect_to_server_main_ex()
        self.connect_to_server_gui_q()
        
        self.connect_to_server_hk_ex()
        self.connect_to_server_sub_q()
                     
        self.startup()
        
        self.data_processing()        

        
    def closeEvent(self, event: QCloseEvent) -> None:

        self.producer[HK_SUB].send_message(self.hk_sub_q, HK_STOP_MONITORING)
        self.monitoring_ready = False
        ti.sleep(2)
        
        self.log.send(self.iam, DEBUG, "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, DEBUG, "This may take several seconds waiting for threads to close")
                            
        pwr_list = [OFF, OFF, OFF, OFF, OFF, OFF, OFF, OFF]
        self.power_onoff(pwr_list)
        ti.sleep(5)        
                                    
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")       
                                
        msg = "%s %s" % (EXIT, HK)
        self.producer[ENG_TOOLS].send_message(self.hk_main_q, msg)
        
        for i in range(2):
            if self.producer[i] != None:
                self.producer[i].__del__()
        self.producer[HK_SUB] = None

        self.log.send(self.iam, DEBUG, "Closed!") 
                
        return super().closeEvent(event)
    
    
    def init_events(self):
       
        # init PDU
        self.pdulist = [self.sts_pdu1, self.sts_pdu2, self.sts_pdu3, self.sts_pdu4,
                        self.sts_pdu5, self.sts_pdu6, self.sts_pdu7, self.sts_pdu8] 
        
        for i in range(PDU_IDX):
            self.tb_pdu.item(i, 1).setText(self.power_list[i])
            
        self.bt_pwr_onoff = [self.bt_pwr_onoff1, self.bt_pwr_onoff2, self.bt_pwr_onoff3, 
                             self.bt_pwr_onoff4, self.bt_pwr_onoff5, self.bt_pwr_onoff6, 
                             self.bt_pwr_onoff7, self.bt_pwr_onoff8]
        for i in range(PDU_IDX):
            self.QWidgetBtnColor(self.bt_pwr_onoff[i], "black", "white")
        
        self.bt_pwr_onoff1.clicked.connect(lambda: self.power_onoff_index(1))
        self.bt_pwr_onoff2.clicked.connect(lambda: self.power_onoff_index(2))
        self.bt_pwr_onoff3.clicked.connect(lambda: self.power_onoff_index(3))
        self.bt_pwr_onoff4.clicked.connect(lambda: self.power_onoff_index(4))
        self.bt_pwr_onoff5.clicked.connect(lambda: self.power_onoff_index(5))
        self.bt_pwr_onoff6.clicked.connect(lambda: self.power_onoff_index(6))
        self.bt_pwr_onoff7.clicked.connect(lambda: self.power_onoff_index(7))
        self.bt_pwr_onoff8.clicked.connect(lambda: self.power_onoff_index(8))       
        
        self.chk_manual_test.clicked.connect(self.Periodic)
        self.chk_manual_test.setChecked(False)
        
        self.manaul_test(False)
        
        self.e_vacuum.setText("")
        
        # init TMonitor        
        self.monitor = [[] for _ in range(14)]
        for i in range(14):
            name = ""
            if i < 6:
                name = "%s (C)" % self.temp_list[i]
            else:
                name = "%s (M)" % self.temp_list[i]
            self.tb_Monitor.item(i, 0).setText(name)
        
        for i in range(3):
            self.monitor[0].append(self.tb_Monitor.item(0, i+1))
            self.monitor[1].append(self.tb_Monitor.item(1, i+1))
            self.monitor[2].append(self.tb_Monitor.item(2, i+1))
            self.monitor[3].append(self.tb_Monitor.item(3, i+1))
            self.monitor[5].append(self.tb_Monitor.item(5, i+1))
            
        self.monitor[4].append(self.tb_Monitor.item(4, 1)) 
        
        for i in range(TM_CNT):
            self.monitor[TM_1+i].append(self.tb_Monitor.item(TM_1+i, 1))
            
        self.monlist = [self.sts_monitor1, self.sts_monitor2, self.sts_monitor3, self.sts_monitor4,
                        self.sts_monitor5, self.sts_monitor6, self.sts_monitor7, self.sts_monitor8,
                        self.sts_monitor9, self.sts_monitor10, self.sts_monitor11, self.sts_monitor12,
                        self.sts_monitor13, self.sts_monitor14] 
                
        btn_txt = "Send Alert (T_%s>%d)" % (self.alert_label, self.alert_temperature)
        self.chk_alert.setText(btn_txt)
        self.chk_alert.setChecked(True)
        self.chk_alert.clicked.connect(self.toggle_alert)
        
        self.bt_com_tc1.clicked.connect(lambda: self.manual_command(TMC1))
        self.bt_com_tc2.clicked.connect(lambda: self.manual_command(TMC2))
        self.bt_com_tc3.clicked.connect(lambda: self.manual_command(TMC3))
        self.bt_com_tm.clicked.connect(lambda: self.manual_command(TM))
        self.bt_com_tc1.setText("TC1")
        self.bt_com_tc2.setText("TC2")
        self.bt_com_tc3.setText("TC3")
        
        
    def show_info(self):
        
        updated_datetime = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
        self.sts_updated.setText(updated_datetime)
        
        interval_sec = "Interval : %d s" % self.Period
        self.sts_interval.setText(interval_sec)
        
        self.QWidgetLabelColor(self.sts_pdu_on, "red")
        self.QWidgetLabelColor(self.sts_pdu_off, "gray")
        
        self.QWidgetLabelColor(self.sts_monitor_ok, "green")
        self.QWidgetLabelColor(self.sts_monitor_error, "gray")
        
    
    #-------------------------------
    # hk -> main
    def connect_to_server_main_ex(self):
        # RabbitMQ connect  
        self.producer[ENG_TOOLS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_main_ex)      
        self.producer[ENG_TOOLS].connect_to_server()
        self.producer[ENG_TOOLS].define_producer()
        
        msg = "%s %s" % (ALIVE, HK)
        self.producer[ENG_TOOLS].send_message(self.hk_main_q, msg)
    
         
    #-------------------------------
    # main -> hk 
    def connect_to_server_gui_q(self):
        # RabbitMQ connect
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.main_hk_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.main_hk_q, self.callback_main)       
        
        th = threading.Thread(target=consumer.start_consumer)
        th.daemon = True
        th.start()
        
       
    #-------------------------------
    # rev <- main        
    def callback_main(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
                
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        if param[0] == ALIVE:
            msg = "%s %s" % (ALIVE, HK)
            self.producer[ENG_TOOLS].send_message(self.hk_main_q, msg)
        
        
    #-------------------------------
    # hk -> sub    
    def connect_to_server_hk_ex(self):
        # RabbitMQ connect  
        self.producer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex)      
        self.producer[HK_SUB].connect_to_server()
        self.producer[HK_SUB].define_producer()
    
         
    #-------------------------------
    # sub -> hk
    def connect_to_server_sub_q(self):
        # RabbitMQ connect
        sub_hk_ex = [self.com_list[i]+'.ex' for i in range(COM_CNT-1)]
        consumer = [None for _ in range(COM_CNT-1)]
        for idx in range(COM_CNT-1):
            consumer[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_hk_ex[idx])      
            consumer[idx].connect_to_server()
            
        consumer[TMC1].define_consumer(self.com_list[TMC1]+'.q', self.callback_tmc1)       
        consumer[TMC2].define_consumer(self.com_list[TMC2]+'.q', self.callback_tmc2)
        consumer[TMC3].define_consumer(self.com_list[TMC3]+'.q', self.callback_tmc3)
        consumer[TM].define_consumer(self.com_list[TM]+'.q', self.callback_tm)
        consumer[VM].define_consumer(self.com_list[VM]+'.q', self.callback_vm)
        consumer[PDU].define_consumer(self.com_list[PDU]+'.q', self.callback_pdu)
        consumer[UPLOADER].define_consumer(self.com_list[UPLOADER]+'.q', self.callback_uploader)      
        
        for idx in range(COM_CNT-1):
            th = threading.Thread(target=consumer[idx].start_consumer)
            th.daemon = True
            th.start()
            
        self.producer[HK_SUB].send_message(self.hk_sub_q, HK_REQ_COM_STS)
        
                
    #-------------------------------
    # rev <- sub 
    def callback_tmc1(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        self.param = param[0]
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TMC1] = bool(int(param[1]))            
            self.check_ready()
            
        elif param[0] == HK_REQ_GETSETPOINT:
            self.set_point[0] = self.judge_value(param[1])
            self.set_point[1] = self.judge_value(param[2])
            self.save_setpoint(self.set_point)
        
        elif param[0] == HK_REQ_GETVALUE:
            self.dtvalue[label_list[0]] = self.judge_value(param[1])
            self.dtvalue[label_list[1]] = self.judge_value(param[2])
            self.heatlabel[label_list[0]] = self.judge_value(param[3])
            self.heatlabel[label_list[1]] = self.judge_value(param[4])
            
        elif param[0] == HK_REQ_MANUAL_CMD:
            res = "[TC1] %s" % param[1]
            self.e_recv.setText(res)
            
            
            
    def callback_tmc2(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        self.param = param[0]
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TMC2] = bool(int(param[1]))            
            self.check_ready()
        
        elif param[0] == HK_REQ_GETSETPOINT:
            self.set_point[2] = self.judge_value(param[1])
            self.set_point[3] = self.judge_value(param[2])
            self.save_setpoint(self.set_point)
            
        elif param[0] == HK_REQ_GETVALUE:
            self.dtvalue[label_list[2]] = self.judge_value(param[1])
            self.dtvalue[label_list[3]] = self.judge_value(param[2])
            self.heatlabel[label_list[2]] = self.judge_value(param[3])
            self.heatlabel[label_list[3]] = self.judge_value(param[4])
            
        elif param[0] == HK_REQ_MANUAL_CMD:
            res = "[TC2] %s" % param[1]
            self.e_recv.setText(res)
            
        
    def callback_tmc3(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        self.param = param[0]
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TMC3] = bool(int(param[1]))            
            self.check_ready()
            
        elif param[0] == HK_REQ_GETSETPOINT:
            self.set_point[4] = self.judge_value(param[1])
            self.save_setpoint(self.set_point)
        
        elif param[0] == HK_REQ_GETVALUE:
            self.dtvalue[label_list[4]] = self.judge_value(param[1])
            self.dtvalue[label_list[5]] = self.judge_value(param[2])
            self.heatlabel[label_list[5]] = self.judge_value(param[3])
            
        elif param[0] == HK_REQ_MANUAL_CMD:
            res = "[TC3] %s" % param[1]
            self.e_recv.setText(res)
                    
    
    def callback_tm(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        self.param = param[0]
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TM] = bool(int(param[1]))            
            self.check_ready()
        
        elif param[0] == HK_REQ_GETVALUE:
            for i in range(TM_CNT):
                self.dtvalue[label_list[TM_1+i]] = self.judge_value(param[i+1])
                
        elif param[0] == HK_REQ_MANUAL_CMD:
            res = "[TM] %s" % param[1]
            self.e_recv.setText(res)
                
    
    def callback_vm(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        if len(cmd) < 80:
            self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        self.param = param[0]
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[VM] = bool(int(param[1]))            
            self.check_ready()
            
        elif param[0] == HK_REQ_GETVALUE:
            if len(param[1]) > 10 or param[1] == DEFAULT_VALUE:
                self.dpvalue = DEFAULT_VALUE
            else:
                self.dpvalue = param[1]
            
            
    def callback_pdu(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        self.param = param[0]
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[PDU] = bool(int(param[1]))            
            self.check_ready()
            
        elif param[0] == HK_REQ_PWR_STS:
            for i in range(PDU_IDX):
                self.power_status[i] = param[i+1]
            
            
    def callback_uploader(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        self.param = param[0]
        if param[0] == HK_REQ_UPLOAD_STS:
            self.uploade_status = True     
        
    #-------------------------------
    # com sts monitoring
    
    def check_ready(self):
        for i in range(COM_CNT-1):
            if not self.com_status[i]:
                break
        if i == 6:
            self.monitoring_ready = True
            msg = "%s GOOD" % HK_STATUS
            self.producer[ENG_TOOLS].send_message(self.hk_main_q, msg)
            
    
    def uploader_monitor(self):
        clr = "gray"
        if self.uploade_status:
            clr = "green"
        self.QWidgetLabelColor(self.sts_uploading_sts, clr) 
        
        
    def tempctrl_monitor(self, con, idx):
        clr = "gray"
        if con:
            clr = "green"
        self.QWidgetLabelColor(self.monlist[idx], clr)
        self.QWidgetLabelColor(self.monlist[idx+1], clr)
            
            
    def temp_monitor(self, con):
        clr = "gray"
        if con:
            clr = "green"
        for i in range(TM_CNT):
            self.QWidgetLabelColor(self.monlist[TM_1+i], clr)
                
        
    def vacuum_monitor(self, con):
        clr = "gray"
        if con:
            clr = "green"
        self.QWidgetLabelColor(self.sts_vacuum, clr)
        
        
    def pdu_monitor(self, con):
        clr = "gray"
        if con:
            clr = "red"
        self.QWidgetLabelColor(self.sts_pdu, clr) 
        
       
        
    #-------------------------------
    # control and show 
    def save_setpoint(self, setp):
        for i, v in enumerate(setp):
            key = "setp%d" % (i+1)
            self.cfg.set(HK, key, v)
        
        sc.SaveConfig(self.cfg, self.ini_file)   #IGRINS.ini
        
        
    def GetValuefromTempCtrl(self, port, idx, value, limit): 
        state = "warm"
        if abs(float(self.set_point[idx])-float(value)) >= limit or value == DEFAULT_VALUE:
            state = "warm"   
        else:
            state = "normal"
        self.QShowValue(port, 0, value, state)

    
    def judge_value(self, input):
        if input != DEFAULT_VALUE:
            value = "%.2f" % float(input)
        else:
            value = input

        return value


    #-----------------------------
    # button
    def power_onoff_index(self, idx):
        if self.power_status[idx-1]:
            msg = "%s %d %s" % (HK_REQ_PWR_ONOFF_IDX, idx, OFF)
        else:
            msg = "%s %d %s" % (HK_REQ_PWR_ONOFF_IDX, idx, ON)
        self.producer[HK_SUB].send_message(self.hk_sub_q, msg)         
        

    def manual_command(self, idx):
        msg = "%s %s %s" % (HK_REQ_MANUAL_CMD, self.com_list[idx], self.e_sendto.text())
        self.producer[HK_SUB].send_message(self.hk_sub_q, msg)
        
        
    def toggle_alert(self):
        if not self.chk_alert.isChecked():
            self.set_alert_status_off()
            
            
    def manaul_test(self, status):
        self.e_sendto.setEnabled(status)
        self.e_recv.setEnabled(status)
        self.bt_com_tc1.setEnabled(status)
        self.bt_com_tc2.setEnabled(status)
        self.bt_com_tc3.setEnabled(status)
        self.bt_com_tm.setEnabled(status)

            
    #-----------------------------
    # strat process
       
    def startup(self):
        if not self.monitoring_ready:
            threading.Timer(1, self.startup).start()
            return  
                            
        self.producer[HK_SUB].send_message(self.hk_sub_q, HK_REQ_PWR_STS)
            
        pwr_list = [ON, ON, OFF, OFF, OFF, OFF, OFF, OFF]
        self.power_onoff(pwr_list)
                    
        self.Periodic()
         
        
    def Periodic(self):
        if self.chk_manual_test.isChecked():
            self.manaul_test(True)
            self.monitoring_ready = False
            
            self.producer[HK_SUB].send_message(self.hk_sub_q, HK_STOP_MONITORING)
            
            self.log.send(self.iam, INFO, "Periodic Monitoring paused")
            self.set_alert_status_off()
            
        else:   
            self.manaul_test(False)
            self.monitoring_ready = True
            
            self.producer[HK_SUB].send_message(self.hk_sub_q, HK_REQ_GETSETPOINT)
            ti.sleep(1)
            self.producer[HK_SUB].send_message(self.hk_sub_q, HK_START_MONITORING)
                              
            self.log.send(self.iam, INFO, "Periodic Monitoring started")
            self.st_time = ti.time()
            
            self.get_value()
            self.PeriodicFunc()
            
            self.uploade_start = ti.time()
            
            
    def PeriodicFunc(self):
        if not self.monitoring_ready:
            return
        
        if self.producer[HK_SUB] == None:
            return
        
        _t = ti.time() - self.st_time
        if _t < self.Period:
            threading.Timer(0.5, self.PeriodicFunc).start()
            return

        self.st_time = ti.time()
        self.get_value()
        self.st = ti.time()            
    
        threading.Timer(0.5, self.PeriodicFunc).start()
        self.log.send(self.iam, INFO, "PeriodicFunc")

        threading.Timer(2, self.LoggingFun).start()          
                
                    
    def get_value(self):
        self.producer[HK_SUB].send_message(self.hk_sub_q, HK_REQ_GETVALUE) 
        
        self.send_alert_if_needed()
        
    
    def power_onoff(self, args):
        pwr_list = ""
        for i in range(PDU_IDX):
            pwr_list += args[i] + " "
        msg = "%s %s" % (HK_REQ_PWR_ONOFF, pwr_list)
        self.producer[HK_SUB].send_message(self.hk_sub_q, msg)

        
    def LoggingFun(self):     
        if self.chk_manual_test.isChecked():
            return

        fname = ti.strftime("%Y%m%d", ti.localtime())+".log"
        f_p_name = self.logpath+fname
        if os.path.isfile(f_p_name):
            file=open(f_p_name,'a+')
        else:
            file=open(f_p_name,'w')

        hk_entries = [self.dpvalue,
                      self.dtvalue_from_label["bench"],     self.heatlabel["tmc1-a"],
                      self.dtvalue_from_label["grating"],   self.heatlabel["tmc1-b"],
                      self.dtvalue_from_label["detS"],      self.heatlabel["tmc2-a"],
                      self.dtvalue_from_label["detK"],      self.heatlabel["tmc2-b"],
                      self.dtvalue_from_label["camH"],    
                      self.dtvalue_from_label["detH"],      self.heatlabel["tmc3-b"],
                      self.dtvalue_from_label["benchcenter"],    
                      self.dtvalue_from_label["coldhead01"],
                      self.dtvalue_from_label["coldhead02"],    
                      self.dtvalue_from_label["coldstop"],    
                      self.dtvalue_from_label["charcoalBox"],
                      self.dtvalue_from_label["camK"],    
                      self.dtvalue_from_label["shieldtop"],  
                      self.dtvalue_from_label["air"]]  

        if self.chk_alert.isChecked():
            alert_status = "On(T>%d)" % self.alert_temperature
        else:
            alert_status = "Off"

        hk_entries.append(alert_status)

        # hk_entries to string
        updated_datetime = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
        self.sts_updated.setText(updated_datetime)

        str_log1 = "\t".join([updated_datetime] + list(map(str, hk_entries))) + "\n"    #by hilee
        file.write(str_log1)
        file.close()

        upload = ti.time() - self.uploade_start
        #print("Logging time:", upload)
        if upload >= LOGGING_INTERVAL:
            self.uploade_status = False
            
            str_log = "    ".join([updated_datetime] + list(map(str, hk_entries)))     
            msg = "%s %s" % (HK_REQ_UPLOAD_DB, str_log)
            self.producer[HK_SUB].send_message(self.hk_sub_q, msg)
            
            self.uploade_start = ti.time()
        
        # update log_time with Z0
        log_date, log_time = updated_datetime.split()
        hk_dict = hk_entries_to_dict(log_date, log_time, hk_entries)
        hk_dict.update(self.dtvalue_from_label.as_dict())

        threading.Timer(1, self.uploader_monitor).start()
              
        
    def send_alert_if_needed(self):
        if not self.chk_alert.isChecked():
            return 

        if self.check_temperature_danger():
            if not self.alert_toggling:
                self.alert_toggling = True
                self.set_alert_status_on()
        else:
            self.set_alert_status_off()
            
            
    def check_temperature_danger(self):
        # temperature of cold head #2
        label = self.alert_label
        temp = self.alert_temperature
        
        if float(self.dtvalue_from_label[label]) > temp:
            return True
        else:
            return False
        
        
    def set_alert_status_on(self):
        
        if not self.chk_alert.isChecked():
            return
        
        clr = next(self.iter_color)
        bg = next(self.iter_bgcolor)
        self.alert_status.setText("ALERT")
        self.QWidgetLabelColor(self.alert_status, clr, bg)
        
        msg = "%s ERROR" % HK_STATUS
        self.producer[ENG_TOOLS].send_message(self.hk_main_q, msg)
        
        threading.Timer(1, self.set_alert_status_on).start()
                             
        
    def set_alert_status_off(self):
        self.alert_toggling = False
        self.alert_status.setText("Okay")
        self.QWidgetLabelColor(self.alert_status, "black", "white") 
        
        msg = "%s GOOD" % HK_STATUS
        self.producer[ENG_TOOLS].send_message(self.hk_main_q, msg)

        
    #----------------------
    # about gui set
    def QShowValue(self, row, col, text, state):
        #monitor = self.tb_Monitor.item(row, col)
        if state == "warm":
            self.monitor[row][col].setForeground(QColor("red"))
        else:
            self.monitor[row][col].setForeground(QColor("black"))
        #monitor.setText(text)
        self.monitor[row][col].setText(text)
            

    def QShowValueVM(self, text, state):
        if state == "warm":
            self.QWidgetEditColor(self.e_vacuum, "white", "red")
        else:
            self.QWidgetEditColor(self.e_vacuum, "black", "white")
        self.e_vacuum.setText(text)
        
        
    def QWidgetEditColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QLineEdit {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QLineEdit {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
        
        
    def QWidgetLabelColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QLabel {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QLabel {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
            
            
    def QWidgetBtnColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QPushButton {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QPushButton {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
            
    
    def data_processing(self):
        if not self.monitoring_ready:
            threading.Timer(1, self.data_processing).start()
            return
                    
        if self.param == HK_REQ_COM_STS:                        
            for idx in range(COM_CNT-1):
                if not self.com_status[idx]:
                    if not self.alert_toggling:
                        self.alert_toggling = True
                        self.set_alert_status_on()
                    break 
            self.param = ""
            
        self.tempctrl_monitor(self.com_status[TMC1], TMC1)               
        self.tempctrl_monitor(self.com_status[TMC2], TMC2*2)
        self.tempctrl_monitor(self.com_status[TMC3], TMC3*2)
        self.temp_monitor(self.com_status[TM])
        self.vacuum_monitor(self.com_status[VM])
        self.pdu_monitor(self.com_status[PDU])                
        
        self.monitor[0][1].setText(self.set_point[0])
        self.monitor[1][1].setText(self.set_point[1])       
        self.monitor[2][1].setText(self.set_point[2])
        self.monitor[3][1].setText(self.set_point[3])
        self.monitor[5][1].setText(self.set_point[4])
                        
        # from TMC
        self.GetValuefromTempCtrl(TMC1_A, 0, self.dtvalue[label_list[0]], 1.0)
        self.GetValuefromTempCtrl(TMC1_B, 1, self.dtvalue[label_list[1]], 0.1)
        self.monitor[TMC1_A][2].setText(self.heatlabel[label_list[0]])
        self.monitor[TMC1_B][2].setText(self.heatlabel[label_list[1]])
            
        self.GetValuefromTempCtrl(TMC2_A, 2, self.dtvalue[label_list[2]], 0.1)
        self.GetValuefromTempCtrl(TMC2_B, 3, self.dtvalue[label_list[3]], 0.1)
        self.monitor[TMC2_A][2].setText(self.heatlabel[label_list[2]])
        self.monitor[TMC2_B][2].setText(self.heatlabel[label_list[3]])
                
        if self.dtvalue[label_list[4]] == DEFAULT_VALUE:
            state = "warm"
        else:
            state = "normal"     
        self.QShowValue(TMC3_A, 0, self.dtvalue[label_list[4]], state)
        self.GetValuefromTempCtrl(TMC3_B, 4, self.dtvalue[label_list[5]], 0.1)
        self.monitor[TMC3_B][2].setText(self.heatlabel[label_list[5]])

        # from TM
        # for all
        for i in range(TM_CNT):
            if self.dtvalue[label_list[TM_1+i]] == DEFAULT_VALUE:
                state = "warm"
            else:
                state = "normal"
            self.QShowValue(TM_1+i, 0, self.dtvalue[label_list[TM_1+i]], state)
                
        # from VM
        if self.dpvalue == DEFAULT_VALUE:
            state = "warm"
        else:
            state = "normal"
        self.QShowValueVM(self.dpvalue, state)
            
        # from PDU
        for i in range(PDU_IDX):
            if self.power_status[i] == ON:
                self.QWidgetLabelColor(self.pdulist[i], "red")
                self.bt_pwr_onoff[i].setText(OFF)
                self.QWidgetBtnColor(self.bt_pwr_onoff[i], "white", "green")
            else:
                self.QWidgetLabelColor(self.pdulist[i], "gray")
                self.bt_pwr_onoff[i].setText(ON)
                self.QWidgetBtnColor(self.bt_pwr_onoff[i], "black", "white")                 
                
        threading.Timer(1, self.data_processing).start()
            
          
    
        
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
        
    hk = MainWindow()
    hk.show()
        
    app.exec()
    

