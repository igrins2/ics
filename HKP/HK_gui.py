# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on Dec 29, 2022

@author: hilee
"""

import asyncio
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

import smtplib
from email.mime.text import MIMEText
import datetime

from Libs.hk_field_definition import hk_entries_to_dict
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import subprocess

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
    
    def __init__(self, autostart=False):
        super().__init__()
        
        self.iam = HK     
        
        self.log = LOG(WORKING_DIR + "IGRINS", "HKP")    
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        self.setWindowTitle("Housekeeping Package 0.3")
        
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
        self.sub_hk_ex = self.cfg.get(MAIN, "sub_hk_exchange")
        self.sub_hk_q = self.cfg.get(MAIN, "sub_hk_routing_key")
                
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
        self.alert_email = self.cfg.get(HK, "hk-alert-email")
        
        self.tb_Monitor.setColumnWidth(0, self.tb_Monitor.width()/32 * 11)
        self.tb_Monitor.setColumnWidth(1, self.tb_Monitor.width()/32 * 7)
        self.tb_Monitor.setColumnWidth(2, self.tb_Monitor.width()/32 * 7)
        self.tb_Monitor.setColumnWidth(3, self.tb_Monitor.width()/32 * 7)
                
        self.timestamp_alert = None
        
        # check Periodic Button pressed or not
        self.periodicbtn = NOT_PRESSED
    
        self.power_status = [OFF for _ in range(PDU_IDX)]
                    
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
                
        self.producer = [None for _ in range(SERV_CONNECT_CNT)]
        self.consumer = [None for _ in range(SERV_CONNECT_CNT)]
        
        self.uploade_start = 0
        self.uploade_status = False
        self.uploader_monitor()
                
        self.sending_email_mode = False
        self.bt_start.setText("email sending: On")
        self.QWidgetBtnColor(self.bt_start, "black", "white")
               
        self.connect_to_server_main_ex()
        self.connect_to_server_gui_q()
        
        self.connect_to_server_hk_ex()
        self.connect_to_server_sub_q()
        
        #for monitoring
        self.timer_sendsts = QTimer(self)
        self.timer_sendsts.setInterval(3600*1000)
        self.timer_sendsts.timeout.connect(self.send_sts)
             
        self.on_startup(True, True)
        

        
    def closeEvent(self, event: QCloseEvent) -> None:
        
        self.periodicbtn = PRESSED
        self.Periodic()
        
        ti.sleep(2)
        
        self.log.send(self.iam, INFO, "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, INFO, "This may take several seconds waiting for threads to close")
            
        for idx in range(PDU_IDX):
            if self.power_status[idx] == ON:
                self.power_onoff(idx+1)               
                            
        for th in threading.enumerate():
            self.log.send(self.iam, DEBUG, th.name + " exit.")
                    
        self.log.send(self.iam, INFO, "Closed!")        
                                
        for i in range(SERV_CONNECT_CNT):
            if i == ENG_TOOLS:
                msg = "%s %s" % (EXIT, HK)
                self.producer[ENG_TOOLS].send_message(MAIN, self.hk_main_q, msg)
            
            if self.producer[i] != None:
                self.producer[i].__del__()
                
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
        
        self.bt_pwr_onoff1.clicked.connect(lambda: self.power_onoff(1))
        self.bt_pwr_onoff2.clicked.connect(lambda: self.power_onoff(2))
        self.bt_pwr_onoff3.clicked.connect(lambda: self.power_onoff(3))
        self.bt_pwr_onoff4.clicked.connect(lambda: self.power_onoff(4))
        self.bt_pwr_onoff5.clicked.connect(lambda: self.power_onoff(5))
        self.bt_pwr_onoff6.clicked.connect(lambda: self.power_onoff(6))
        self.bt_pwr_onoff7.clicked.connect(lambda: self.power_onoff(7))
        self.bt_pwr_onoff8.clicked.connect(lambda: self.power_onoff(8))       
        
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
        
        self.bt_pause.clicked.connect(self.Periodic)
        
        btn_txt = "Send Alert (T_%s>%d)" % (self.alert_label, self.alert_temperature)
        self.chk_alert.setText(btn_txt)
        self.chk_alert.clicked.connect(self.toggle_alert)
        self.chk_alert.setEnabled(False)
        
        # for monitoring: sending email
        self.bt_start.clicked.connect(self.sending_email)

        self.bt_com_tc1.clicked.connect(lambda: self.manual_command(1))
        self.bt_com_tc2.clicked.connect(lambda: self.manual_command(2))
        self.bt_com_tc3.clicked.connect(lambda: self.manual_command(3))
        self.bt_com_tm.clicked.connect(lambda: self.manual_command(4))
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
        self.producer[ENG_TOOLS].send_message(MAIN, self.hk_main_q, msg)
    
         
    #-------------------------------
    # main -> hk 
    def connect_to_server_gui_q(self):
        # RabbitMQ connect
        self.consumer[ENG_TOOLS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.main_hk_ex)      
        self.consumer[ENG_TOOLS].connect_to_server()
        self.consumer[ENG_TOOLS].define_consumer(self.main_hk_q, self.callback_main)       
        
        th = threading.Thread(target=self.consumer[ENG_TOOLS].start_consumer)
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
            self.producer[ENG_TOOLS].send_message(MAIN, self.hk_main_q, msg)
        
        
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
        self.consumer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.sub_hk_ex)      
        self.consumer[HK_SUB].connect_to_server()
        self.consumer[HK_SUB].define_consumer(self.sub_hk_q, self.callback_sub)       
        
        th = threading.Thread(target=self.consumer[HK_SUB].start_consumer)
        th.daemon = True
        th.start()
        
                
    #-------------------------------
    # rev <- sub 
    def callback_sub(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        if len(cmd) < 50:
            self.log.send(self.iam, INFO, msg)

        param = cmd.split()
                
        if param[0] == CMD_REQ_TEMP:
            self.LoggingFun()

        elif param[0] == HK_REQ_UPLOAD_STS:
            self.uploade_status = True
        
        connected = True
        if param[0] == HK_REQ_COM_STS:
            connected = bool(int(param[2]))
            if connected is False:
                self.set_alert_status_on()   

        if param[1] == self.com_list[TMC1]:
            self.tempctrl_monitor(connected, TMC1)
            
        elif param[1] == self.com_list[TMC2]:
            self.tempctrl_monitor(connected, TMC2*2)
            
        elif param[1] == self.com_list[TMC3]:
            self.tempctrl_monitor(connected, TMC3*2)
            
        elif param[1] == self.com_list[TM]:
            self.temp_monitor(connected)
            
        elif param[1] == self.com_list[VM]:
            self.vacuum_monitor(connected)
            
        elif param[1] == self.com_list[PDU]:
            self.pdu_monitor(connected)                
            
        if param[0] == HK_REQ_GETSETPOINT:      
            if param[1] == self.com_list[TMC1]:
                self.set_point[0] = self.judge_value(param[2])
                self.monitor[0][1].setText(self.set_point[0])
                self.set_point[1] = self.judge_value(param[3])
                self.monitor[1][1].setText(self.set_point[1])
            elif param[1] == self.com_list[TMC2]:
                self.set_point[2] = self.judge_value(param[2])
                self.monitor[2][1].setText(self.set_point[2])
                self.set_point[3] = self.judge_value(param[3])
                self.monitor[3][1].setText(self.set_point[3])
            elif param[1] == self.com_list[TMC3]:
                self.set_point[4] = self.judge_value(param[2])
                self.monitor[5][1].setText(self.set_point[4])
                
            self.save_setpoint(self.set_point)
            #self.log.send(self.iam, DEBUG, self.set_point)
            
        elif param[0] == HK_REQ_GETVALUE:    
            # from TMC
            if param[1] == self.com_list[TMC1]:
                value = self.judge_value(param[2])
                self.dtvalue[label_list[0]] = self.GetValuefromTempCtrl(TMC1_A, 0, value, 1.0)
                value = self.judge_value(param[3])
                self.dtvalue[label_list[1]] = self.GetValuefromTempCtrl(TMC1_B, 1, value, 0.1)
                
                heat = self.judge_value(param[4])
                self.heatlabel[label_list[0]] = self.GetHeatValuefromTempCtrl(TMC1_A, heat)
                heat = self.judge_value(param[5])
                self.heatlabel[label_list[1]] = self.GetHeatValuefromTempCtrl(TMC1_B, heat)
                
            elif param[1] == self.com_list[TMC2]:
                value = self.judge_value(param[2])
                self.dtvalue[label_list[2]] = self.GetValuefromTempCtrl(TMC2_A, 2, value, 0.1)
                value = self.judge_value(param[3])
                self.dtvalue[label_list[3]] = self.GetValuefromTempCtrl(TMC2_B, 3, value, 0.1)
            
                heat = self.judge_value(param[4])
                self.heatlabel[label_list[2]] = self.GetHeatValuefromTempCtrl(TMC2_A, heat)
                heat = self.judge_value(param[5])
                self.heatlabel[label_list[3]] = self.GetHeatValuefromTempCtrl(TMC2_B, heat)
                    
            elif param[1] == self.com_list[TMC3]:  
                if param[2] == DEFAULT_VALUE:
                    state = "warm"
                else:
                    state = "normal"     

                value = self.judge_value(param[2])
                self.QShowValue(TMC3_A, 0, value, state)
                
                self.dtvalue[label_list[4]] = value
                value = self.judge_value(param[3])
                self.dtvalue[label_list[5]] = self.GetValuefromTempCtrl(TMC3_B, 4, value, 0.1)
            
                heat = self.judge_value(param[4])
                self.heatlabel[label_list[5]] = self.GetHeatValuefromTempCtrl(TMC3_B, heat)       

            # from TM
            elif param[1] == self.com_list[TM]:
                # for all
                for i in range(TM_CNT):
                    if param[2+i] == DEFAULT_VALUE:
                        state = "warm"
                    else:
                        state = "normal"
                    value = self.judge_value(param[2+i])
                    self.QShowValue(TM_1+i, 0, value, state)
                    self.dtvalue[label_list[TM_1+i]] = value
                    
            # from VM
            elif param[1] == self.com_list[VM]:
                if len(param[2]) > 10 or param[2] == DEFAULT_VALUE:
                    value = DEFAULT_VALUE
                    state = "warm"
                else:
                    value = param[2]
                    state = "normal"
                self.QShowValueVM(value, state)
                self.dpvalue = value                     
                
        # from PDU
        elif param[0] == HK_REQ_PWR_STS:
            for i in range(PDU_IDX):
                self.power_status[i] = param[i+3]    
                if self.power_status[i] == ON:
                    self.QWidgetLabelColor(self.pdulist[i], "red")
                    self.bt_pwr_onoff[i].setText(OFF)
                    self.QWidgetBtnColor(self.bt_pwr_onoff[i], "white", "green")
                else:
                    self.QWidgetLabelColor(self.pdulist[i], "gray")
                    self.bt_pwr_onoff[i].setText(ON)
                    self.QWidgetBtnColor(self.bt_pwr_onoff[i], "black", "white")                  
                
        elif param[0] == HK_REQ_MANUAL_CMD:
            result = "[%s:%s] %s" % (param[1], param[2], param[3])
            self.e_recv.setText(result)
                      
        
        
    #-------------------------------
    # com sts monitoring
    
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
        
    
    def GetHeatValuefromTempCtrl(self, port, heat): 
        value = self.judge_value(heat)
        self.monitor[port][2].setText(value)
        return heat
    
    
    def GetValuefromTempCtrl(self, port, idx, value, limit): 
        state = "warm"
        if abs(float(self.set_point[idx])-float(value)) >= limit or value == DEFAULT_VALUE:
            state = "warm"   
        else:
            state = "normal"
        value = self.judge_value(value)
        self.QShowValue(port, 0, value, state)
        return value               

    
    def judge_value(self, input):
        if input != DEFAULT_VALUE:
            value = "%.2f" % float(input)
        else:
            value = input

        return value


    #-----------------------------
    # button
    def power_onoff(self, idx):
        if self.power_status[idx-1] == ON:
            msg = "%s %s %s %d %s" % (HK_REQ_PWR_ONOFF, self.com_list[PDU], HK, idx, OFF)
        else:
            msg = "%s %s %s %d %s" % (HK_REQ_PWR_ONOFF, self.com_list[PDU], HK, idx, ON)
        self.producer[HK_SUB].send_message(self.com_list[PDU], self.hk_sub_q, msg) 
        
        

    def manual_command(self, idx):
        if idx == 4:
            target = "tm"
        else:
            target = "tmc%d" % idx
        msg = "%s %s %s" % (HK_REQ_MANUAL_CMD, target, self.e_sendto.text())
        self.producer[HK_SUB].send_message(target, self.hk_sub_q, msg)
        
        
    def toggle_alert(self):
        if self.chk_alert.isChecked():
            self.timestamp_alert = None
        else:
            self.set_alert_status_off()


    def sending_email(self):
        if self.sending_email_mode:
            self.bt_start.setText("email sending: On")
            self.QWidgetBtnColor(self.bt_start, "black", "white")
                    
            self.set_alert_status_off()
            self.send_sts(2)
        
            self.timer_sendsts.stop()
            self.log.send(self.iam, DEBUG, "Monitoring Stop!!!")
            
            self.sending_email_mode = False
            
        else:
            self.bt_start.setText("email sending: Off")
            self.QWidgetBtnColor(self.bt_start, "white", "green")
        
            self.send_sts(0)
        
            self.timer_sendsts.start()
            self.log.send(self.iam, DEBUG, "Monitoring On...")
            
            self.sending_email_mode = True
            
    #-----------------------------
    # strat process
       
    def on_startup(self, periodic=True, send_alert=True):
                            
        self.get_pwr_sts()
            
        for idx in range(PDU_IDX):
            if idx < 2:
                if self.power_status[idx] == OFF:
                    self.power_onoff(idx+1)
            else:
                if self.power_status[idx] == ON:
                    self.power_onoff(idx+1)
                    
        if periodic:
            self.Periodic()
            if send_alert:
                self.chk_alert.toggle()
         
        
    def Periodic(self):
        if self.periodicbtn == PRESSED:
            self.producer[HK_SUB].send_message("", self.hk_sub_q, HK_STOP_MONITORING)

            self.periodicbtn = NOT_PRESSED
            self.bt_pause.setText("Periodic Monitoring")
            self.QWidgetBtnColor(self.bt_pause, "black", "white")
            
            self.log.send(self.iam, INFO, "Periodic Monitoring paused")

            if self.chk_alert.isChecked():
                self.chk_alert.toggle()
            self.chk_alert.setEnabled(False)
            
            self.set_alert_status_off()
            
            self.log.send(self.iam, INFO, "[cancel] " + str(datetime.datetime.now()))
            
        elif self.periodicbtn == NOT_PRESSED:   
            self.get_setpoint()
               
            self.producer[HK_SUB].send_message("", self.hk_sub_q, HK_START_MONITORING)
                  
            self.periodicbtn = PRESSED
            self.bt_pause.setText("Pause")
            self.QWidgetBtnColor(self.bt_pause, "white", "green")
            
            self.log.send(self.iam, INFO, "Periodic Monitoring started")
            
            self.chk_alert.setEnabled(True)
            
            self.PeriodicFunc()
            
            self.uploade_start = ti.time()
            #print("Logging start:", self.uploade_start)
            
            
    def PeriodicFunc(self):
        
        if self.periodicbtn == PRESSED:
            self.ost=ti.time()
            
            self.get_pwr_sts()

            self.GetValue()
            
            self.st=ti.time()
            if (self.st-self.ost)>=float(self.Period)+0.00005 :
                self.tsh=(self.st-self.ost)-float(self.Period)
            else :
                self.tsh=0.00000
            self.ost=self.st
    
            _t = int((float(self.Period)-(ti.time()-self.st)-self.tsh)*1000)
            timer = QTimer(self)
            if _t > 0:
                timer.singleShot(_t, self.PeriodicFunc)
            else:
                self.log.send(self.iam, ERROR, "periodic is being called with negative time({}). Using default of 10s".format(_t))
                timer.singleShot(_t, self.PeriodicFunc)        
        
            
    def GetValue(self):
        
        with futures.ThreadPoolExecutor() as executor:
            try:
                executor.submit(self.get_value_fromTMC())
                executor.submit(self.get_value_fromTM())
                executor.submit(self.get_value_fromVM())
                
            except RuntimeError as e:
                self.log.send(self.iam, ERROR, e)
            except Exception as e:
                self.log.send(self.iam, ERROR, e)
                    
        timer = QTimer(self)
        timer.singleShot(2000, self.LoggingFun)

        self.send_alert_if_needed()
               
        
    def get_setpoint(self):        
        # bench, Grating, SVC, Detector K, Detector H 
        for i in range(3):  
            msg = "%s %s" % (HK_REQ_GETSETPOINT, self.com_list[i])
            self.producer[HK_SUB].send_message(self.com_list[i], self.hk_sub_q, msg)
        
                    
    def get_value_fromTMC(self):
        for i in range(3):
            msg = "%s %s" % (HK_REQ_GETVALUE, self.com_list[i])
            self.producer[HK_SUB].send_message(self.com_list[i], self.hk_sub_q, msg) 

    
    def get_value_fromTM(self):
        msg = "%s %s 0" % (HK_REQ_GETVALUE, self.com_list[TM])
        self.producer[HK_SUB].send_message(self.com_list[TM], self.hk_sub_q, msg) 
            
            
    def get_value_fromVM(self):
        msg = "%s %s" % (HK_REQ_GETVALUE, self.com_list[VM])
        self.producer[HK_SUB].send_message(self.com_list[VM], self.hk_sub_q, msg) 
        
    
    def get_pwr_sts(self):
        msg = "%s %s %s" % (HK_REQ_PWR_STS, self.com_list[PDU], HK)
        self.producer[HK_SUB].send_message(self.com_list[PDU], self.hk_sub_q, msg) 
        
        
    def LoggingFun(self):     
        if self.bt_pause.text == "Periodic Monitoring":
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
            msg = "%s %s %s" % (HK_REQ_UPLOAD_DB, self.com_list[UPLOADER], str_log)
            self.producer[HK_SUB].send_message(self.com_list[UPLOADER], self.hk_sub_q, msg)
            
            self.uploade_start = ti.time()
        
        # update log_time with Z0
        log_date, log_time = updated_datetime.split()
        hk_dict = hk_entries_to_dict(log_date, log_time, hk_entries)
        hk_dict.update(self.dtvalue_from_label.as_dict())

        threading.Timer(3, self.uploader_monitor).start()
              
        
        
        
    def send_alert_if_needed(self):
        if not self.chk_alert.isChecked():
            return 

        if self.check_temperature_danger():
            if (self.timestamp_alert is None) or \
               (ti.time() - self.timestamp_alert > 1800.):
                try:
                    self.send_alert()
                    pass
                except Exception:
                    import traceback
                    traceback.print_exc()
                else:
                    self.timestamp_alert = ti.time()

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
        
        
    def send_alert(self):

        self.log.send(self.iam, WARNING, "sending alerts! REAL")

        to = self.alert_email

        title = "Warning : IGRINS2 needs YOU!"

        label = self.alert_label
        temp = self.alert_temperature

        msg = "Please check temperatures of IGRINS2!\n {} > {}".format(label, temp)
        
        self.log.send(self.iam, WARNING, "sending alerts")

        self.send_gmail(to, title, msg)
        self.log.send(self.iam, WARNING, "email was sent to")

        self.log.send(self.iam, WARNING, "slacker message was sent")
        
        
    def send_gmail(self, email_to, email_title, email_content):
        
        email_from = "gemini.igrins2@gmail.com"  #temp!!!!
        #email_to = "leehyein.julien@gmail.com"
        #email_subject = "Email Test."
        #email_content = "Sending an email test."
  
        msg = MIMEText(email_content)
        msg["From"] = email_from
        msg["To"] = email_to
        msg["Subject"] = email_title
    
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login("gemini.igrins2@gmail.com", "ketnbccnjnkrbdrn")   #temp!!!!
        smtp.sendmail(email_from, email_to, msg.as_string())

        smtp.quit()
        
        
    def set_alert_status_on(self):
        
        timer = QTimer(self)
        def _f():
            if not self.chk_alert.isChecked():
                return
            
            clr = next(self.iter_color)
            bg = next(self.iter_bgcolor)
            self.alert_status.setText("ALERT")
            self.QWidgetLabelColor(self.alert_status, clr, bg)
            
            timer.singleShot(1000, _f)
        timer.singleShot(0, _f)
                 
        
    def set_alert_status_off(self):
        self.alert_status.setText("Okay")
        self.QWidgetLabelColor(self.alert_status, "black", "white") 
    
        
    def send_sts(self, option=1):
        self.log.send(self.iam, INFO, "sending status...")
        to = self.alert_email
        title = "[IG2] Dewar status"
        
        #label = ["pressure", "bench", "bench heat", "coldhead01", "coldhead02", "charcoalBox"]

        #temp = [self.dpvalue, self.dtvalue_from_label["bench"], self.heatlabel["tmc1-a"], 
        #        self.dtvalue_from_label["coldhead01"], self.dtvalue_from_label["coldhead02"],
        #        self.dtvalue_from_label["charcoalBox"]]
        label = ["grating", "grating - tc"]
        temp = [self.dtvalue_from_label["grating"], self.heatlabel["tmc1-b"]]
        
        msg = ""
        if option == 0:
            msg += "monitoring start...\n"
        for i in range(2):

            msg += "%s: %s\n" % (label[i], temp[i])
        if option == 2:
            msg += "monitoring stop!!!\n"
            
        
        self.send_gmail(to, title, msg)
        self.log.send(self.iam, INFO, "email was sent to")
        
        
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
          
    
        
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    
    app = QApplication(sys.argv)
        
    hk = MainWindow()
    hk.show()
        
    app.exec()
    

