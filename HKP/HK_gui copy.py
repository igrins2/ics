# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on May 3, 2022

@author: hilee
"""

from asyncio import as_completed
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_HKP import *
from HK_core import *
from HK_def import *

from HK_gui_mp import ManualHeat

from concurrent import futures
import threading

import json

import smtplib
from email.mime.text import MIMEText
import datetime
from itertools import cycle

from Libs.hk_field_definition import hk_entries_to_dict

import copy

class DtvalueFromLabel:
    def __init__(self, key_to_label, values_dict):
        self._key_to_label = key_to_label
        self._label_to_key = dict((v, k) for (k, v) in list(key_to_label.items()))
        self._values_dict = values_dict

    def __getitem__(self, label):
        k = self._label_to_key.get(label, None)
        return self._values_dict.get(k, "-999")

    def as_dict(self):
        return dict((l, float(self._values_dict.get(k, "-999")))
                    for l, k in list(self._label_to_key.items()) if l)
        

    
class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Housekeeping Package [IGOS2 0.2]")
        
        self.tb_Monitor.setColumnWidth(0, self.tb_Monitor.width()/32 * 8)
        self.tb_Monitor.setColumnWidth(1, self.tb_Monitor.width()/32 * 7)
        self.tb_Monitor.setColumnWidth(2, self.tb_Monitor.width()/32 * 7)
        self.tb_Monitor.setColumnWidth(3, self.tb_Monitor.width()/32 * 10)
        
        self.hk = HK(True)
        
        self.timestamp_alert = None
        
        # check Periodic Button pressed or not
        self.periodicbtn = NOT_PRESSED
        
        # connect to device
        for i in range(COM_CNT):
            self.hk.connect_to_component(i)
            
        # PDU init
        if self.hk.comStatus[PDU] == True:
            self.hk.initPDU()
            self.hk.change_power(1, ON)
            self.hk.change_power(2, ON)
        
            idx = 2
            while idx < PDU_IDX:
                self.hk.change_power(idx+1, OFF)
                idx += 1
        self.PDUStatus()
            
        self.VMonitor()
        self.TMonitor()    
        self.init_events()   
        self.Status()
        
        self.start_time = time.time()
        
        #self.timer = QTimer(self)
        #self.timer.setInterval(self.hk.Period*1000)
        #self.timer.timeout.connect(self.PeriodicFunc)
        
        #self.timer_alert = QTimer(self)
        #self.timer_alert.setInterval(1000)
        #self.timer_alert.timeout.connect(self.set_alert_status_on)
               
        #for test
        self.timer_sendsts = QTimer(self)
        self.timer_sendsts.setInterval(3600*1000)
        self.timer_sendsts.timeout.connect(self.SendSts)
            
        self.iter_color = cycle(["white", "black"]) 
        self.iter_bgcolor = cycle(["red", "white"])
        
        self.dtvalue = dict()
        self.dtvalue_from_label = DtvalueFromLabel(self.hk.key_to_label, self.dtvalue)
        
        self.SETP = ["" for _ in range(5)]   #set point
        
        self.dpvalue = "-999"
        for key in self.hk.key_to_label:
            self.dtvalue[key] = "-999"
        
        self.heatlabel = dict() #heat value
        self.heatlabel["tmc1-a"] = "-999"
        self.heatlabel["tmc1-b"] = "-999"
        self.heatlabel["tmc2-a"] = "-999"
        self.heatlabel["tmc2-b"] = "-999"
        self.heatlabel["tmc3-b"] = "-999"
        
        '''
        self.heatlabel_manual = dict()    #manual set heating value
        self.heatlabel_manual["tmc1-a"] = "-999"
        self.heatlabel_manual["tmc1-b"] = "-999"
        self.heatlabel_manual["tmc2-a"] = "-999"
        self.heatlabel_manual["tmc2-b"] = "-999"
        self.heatlabel_manual["tmc3-b"] = "-999"
        '''
        
        self.comStatus_prev = copy.copy(self.hk.comStatus)
        
        #if autostart:
        self.on_startup(True, True)
        #else:
        #    self.on_startup(False, False)
            
        
    def closeEvent(self, *args, **kwargs):
        
        self.hk.logwrite(BOTH, "Closing %s : " % sys.argv[0])
        self.hk.logwrite(BOTH, "This may take several seconds waiting for threads to close.")
        
        for i in range(COM_CNT):
            try:           
                if self.hk.comSocket[i] != None:
                    if i == PDU:
                        for idx in range(PDU_IDX):
                            self.hk.change_power(idx+1, OFF)
                            idx += 1
                        #cmd = 'LO\r'
                        #self.hk.comSocket[i].send(cmd.encode())
                    self.hk.close_component(i)
            except:
                log = "Error when start closing %s ..." % self.hk.comList[i]
                self.hk.logwrite(BOTH, log)
                    
        # DTP close
        
        # etc connection exit!!!   
        #self.timer.stop()
        #self.timer_alert.stop()
        
        return QMainWindow.closeEvent(self, *args, **kwargs)
        
         
    
    def PDUStatus(self):
        # PDU status
        if self.hk.comStatus[PDU]:
            self.QWidgetLabelColor(self.sts_pdu, "red")
        else:
            self.QWidgetLabelColor(self.sts_pdu, "gray")

        self.pdulist = [self.sts_pdu1, self.sts_pdu2, self.sts_pdu3, self.sts_pdu4,
                        self.sts_pdu5, self.sts_pdu6, self.sts_pdu7, self.sts_pdu8]            
        for i in range(PDU_IDX):
            if self.hk.pow_flag[i] == "ON":
                self.QWidgetLabelColor(self.pdulist[i], "red")
            else:
                self.QWidgetLabelColor(self.pdulist[i], "gray")
                
            self.tb_pdu.item(i, 1).setText(self.hk.POWERSTR[i])
                
    
    def VMonitor(self):
        if self.hk.comStatus[VMC]:
            self.QWidgetLabelColor(self.sts_vacuum, "green")
        else:
            self.QWidgetLabelColor(self.sts_vacuum, "gray")
        self.e_vacuum.setText("")
        
        
    def TMonitor(self):
        
        self.monitor = [[] for _ in range(14)]
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
        monlist_sts = [False for _ in range(14)]
        #self.bt_manualHeat = [self.bt_manualHeat1, self.bt_manualHeat2, self.bt_manualHeat3, self.bt_manualHeat4, self.bt_manualHeat5]
        
        idx = 0   
        for i in range(3):  #TMC1, 2, 3
            if self.hk.comStatus[i]:
                monlist_sts[idx] = True
                monlist_sts[idx+1] = True
            idx += 2
            
        if self.hk.comStatus[TM]:
            for i in range(TM_CNT):
                monlist_sts[6+i] = True  
                
        for i in range(len(self.monlist)):
            if monlist_sts[i]:
                self.QWidgetLabelColor(self.monlist[i], "green")
            else:
                self.QWidgetLabelColor(self.monlist[i], "gray")
            
            self.tb_Monitor.item(i, 0).setText(self.hk.TEMPTEMPERATURE[i])
        
        self.alert_status.setText("Okay")
        self.QWidgetLabelColor(self.alert_status, "black", "white")
        
               
    
    def init_events(self):
        #self.tb_Monitor.cellChanged.connect(self.checkBoxState)
        
        self.bt_pause.clicked.connect(self.Periodic)
        
        btn_txt = "Send Alert (T_%s>%d)" % (self.hk.alert_label, self.hk.alert_temperature)
        self.chk_alert.setText(btn_txt)
        self.chk_alert.clicked.connect(self.toggle_alert)
        self.chk_alert.setEnabled(False)
        
        #for monitoring test: sending email
        self.bt_start.clicked.connect(self.test_start)
        self.bt_stop.clicked.connect(self.test_stop)
        self.bt_stop.setEnabled(False)
        
        self.bt_start.setHidden(False)
        self.bt_stop.setHidden(False)
        
        '''
        self.bt_com_vm.setEnabled(False)
        self.bt_com_tc1.setEnabled(False)
        self.bt_com_tc2.setEnabled(False)
        self.bt_com_tc3.setEnabled(False)
        self.bt_com_tm.setEnabled(False)
        '''
        
        self.bt_com_vm.setHidden(True)
        self.bt_com_tc1.setHidden(True)
        self.bt_com_tc2.setHidden(True)
        self.bt_com_tc3.setHidden(True)
        self.bt_com_tm.setHidden(True)

        #for i in range(5):
        #    self.bt_manualHeat[i].clicked.connect(lambda: self.manualHeat(i))
        self.bt_manualHeat1.clicked.connect(lambda: self.manualHeat(0))
        self.bt_manualHeat2.clicked.connect(lambda: self.manualHeat(1))
        self.bt_manualHeat3.clicked.connect(lambda: self.manualHeat(2))
        self.bt_manualHeat4.clicked.connect(lambda: self.manualHeat(3))
        self.bt_manualHeat5.clicked.connect(lambda: self.manualHeat(4))
        
    '''    
    def checkBoxState(self):
        for idx in range(4):
            if self.monitor[idx][2].checkState():
                self.bt_manualHeat[idx].setHidden(False) 
            elsmanualf.bt_manualHeat[4].setHidden(True)
    '''        
        
    def toggle_alert(self):
        if self.chk_alert.isChecked():
            self.timestamp_alert = None
        else:
            self.set_alert_status_off()
            
            
    def manualHeat(self, idx):
        mp = ManualHeat(self.hk)
        
        heat_list = ["tmc1-a", "tmc1-b", "tmc2-a", "tmc2-b", "tmc3-b"]
        
        res = self.hk.get_heating_power_manual(int(idx/2), (idx%2)+1)
        mp.setTitile(idx, heat_list[idx], res)
        mp.showModal()
              
        
    def Status(self):
        #for i in range(4):
        #    self.bt_manualHeat[i].setHidden(self.monitor[i][2].checkState())
        #self.bt_manualHeat[4].setHidden(self.monitor[5][2].checkState())
        
        updated_datetime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.sts_updated.setText(updated_datetime)
        
        interval_sec = "Interval : %d s" % self.hk.Period
        self.sts_interval.setText(interval_sec)
        
        self.QWidgetLabelColor(self.sts_pdu_on, "red")
        self.QWidgetLabelColor(self.sts_pdu_off, "gray")
        
        self.QWidgetLabelColor(self.sts_monitor_ok, "green")
        self.QWidgetLabelColor(self.sts_monitor_error, "gray")
        
       
       
    def on_startup(self, periodic=True, send_alert=True):
        if periodic:
            self.Periodic()
            if send_alert:
                self.chk_alert.toggle()
         
        
    def Periodic(self):
        if self.periodicbtn == PRESSED:
            self.periodicbtn = NOT_PRESSED
            self.bt_pause.setText("Periodic Monitoring")
            self.hk.logwrite(BOTH, "Periodic Monitoring Button is clicked")

            if self.chk_alert.isChecked():
                self.chk_alert.toggle()
            self.chk_alert.setEnabled(False)
            
           #self.timer.stop()
            self.set_alert_status_off()
            
            self.hk.logwrite(BOTH, "[cancel] " + str(datetime.datetime.now()))
            
            
        elif self.periodicbtn == NOT_PRESSED:            
            self.periodicbtn = PRESSED
            self.bt_pause.setText("Pause")
            self.get_setpoint()
            self.hk.logwrite(BOTH, "Pause Button is clicked")
            
            self.chk_alert.setEnabled(True)
            
            self.PeriodicFunc()
            
            timer = QTimer(self)
            timer.singleShot(1000*60, self.req_PDUStatus)
            #self.timer.start()
            
            
    def req_PDUStatus(self):
                   
        self.hk.power_status("DN0\r")
        self.PDUStatus()
        
        timer = QTimer(self)
        timer.singleShot(1000*60, self.req_PDUStatus)  
    
    
    def test_start(self):
        self.bt_start.setEnabled(False)
        self.bt_stop.setEnabled(True)
        
        self.SendSts(0)
        
        self.timer_sendsts.start()
        self.hk.logwrite(BOTH, "[test] Monitoring Start...")
        
        
    
    def test_stop(self):
        self.bt_start.setEnabled(True)
        self.bt_stop.setEnabled(False)
        
        self.set_alert_status_off()
        self.SendSts(2)
        
        self.timer_sendsts.stop()
        self.hk.logwrite(BOTH, "[test] Monitoring Stop!!!")
        
        
    def SendSts(self, option=1):
        self.hk.logwrite(BOTH, "sending status...")
        to = self.hk.alert_email
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
        self.hk.logwrite(BOTH, "email was sent to")
        
        
            
    
    def get_setpoint(self):        
        #with ThreadPoolExecutor(max_workers=5) as executor:
            #bench, Grating, SVC, Detector K, Detector H 
        setp_list = [TMC1, TMC1, TMC2, TMC2, TMC3]  
        setp_port = [1, 2, 1, 2, 2]
            
        for i in range(len(setp_list)):  
            
            self.SETP[i] = "Empty"
            if self.hk.comStatus[setp_list[i]] == False:
                continue
            
            result = self.hk.get_setpoint_fromTMC(setp_list[i], setp_port[i])
            if result != None:
                self.SETP[i] = " %8.3f" % float(result)
            
            if i == 4:
                self.monitor[5][1].setText(self.SETP[i])
            else:
                self.monitor[i][1].setText(self.SETP[i])  
                
        self.hk.save_setpoint(self.SETP)
      
        self.hk.logwrite(CMDLINE, self.SETP)
        
    
    def QWidgetLabelColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QLabel {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QLabel {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
            
    
    def QShowValue(self, row, col, text, state):
        #monitor = self.tb_Monitor.item(row, col)
        if state == "warm":
            self.monitor[row][col].setForeground(QColor("red"))
        else:
            self.monitor[row][col].setForeground(QColor("black"))
        #monitor.setText(text)
        self.monitor[row][col].setText(text)
            
            
    def get_value_fromTMC1(self):
        #print("Start: get_value_fromTMC1")
        
        label_a = "tmc1-a"
        label_b = "tmc1-b"
        
        self.dtvalue[label_a] = "-999" 
        self.dtvalue[label_b] = "-999" 
        
        self.heatlabel[label_a] = "-999"
        self.heatlabel[label_b] = "-999"
        
        #self.heatlabel_manual[label_a] = "-999"
        #self.heatlabel_manual[label_b] = "-999"       
             
        if self.hk.comStatus[TMC1]:
            # bench monitoring
            try:
                result = self.hk.get_value_fromTMC(TMC1, "A")
                self.dtvalue[label_a] = self.GetValuefromTempCtrl(TMC1_A, 0, result, 1.0)
            except:
                self.QShowValue(TMC1_A, 0, "Err2", "warm")    
                
            # bench heating / manual heating
            try:
                heat = self.hk.get_heating_power(TMC1, 1)
                #heat_m = self.hk.get_heating_power_manual(TMC1, 1)
                self.heatlabel[label_a] = self.GetHeatValuefromTempCtrl(TMC1_A, heat)
            except:
                self.monitor[TMC1_A][2].setText("Err2")
                                
            # Grating monitoring
            try:
                result = self.hk.get_value_fromTMC(TMC1, "B")
                self.dtvalue[label_b] = self.GetValuefromTempCtrl(TMC1_B, 1, result, 0.1)
            except:
                self.QShowValue(TMC1_B, 0, "Err2", "warm")    
                
            # Grating heating / manual heating
            try:
                heat = self.hk.get_heating_power(TMC1, 2)
                #heat_m = self.hk.get_heating_power_manual(TMC1, 2)
                self.heatlabel[label_b] = self.GetHeatValuefromTempCtrl(TMC1_B, heat)
            except:
                self.monitor[TMC1_B][2].setText("Err2")
                    
        else:
            self.QShowValue(TMC1_A, 0, "Err3", "warm")
            self.QShowValue(TMC1_B, 0, "Err3", "warm")   
        
            self.monitor[TMC1_A][2].setText("Err3")
            self.monitor[TMC1_B][2].setText("Err3")
        
        #print("End: get_value_fromTMC1") 
        
        
    def get_value_fromTMC2(self): 
        #print("Start: get_value_fromTMC2")
           
        label_a = "tmc2-a"
        label_b = "tmc2-b"
        
        self.dtvalue[label_a] = "-999" 
        self.dtvalue[label_b] = "-999" 
        
        self.heatlabel[label_a] = "-999"
        self.heatlabel[label_b] = "-999"
        
        #self.heatlabel_manual[label_a] = "-999"
        #self.heatlabel_manual[label_b] = "-999" 
        
        if self.hk.comStatus[TMC2]:
            # SVC monitoring
            try:
                result = self.hk.get_value_fromTMC(TMC2, "A")
                self.dtvalue[label_a] = self.GetValuefromTempCtrl(TMC2_A, 2, result, 0.1)
            except:
                self.QShowValue(TMC2_A, 0, "Err2", "warm")    
                
            # SVC heating / manual heating
            try:
                heat = self.hk.get_heating_power(TMC2, 1)
                #heat_m = self.hk.get_heating_power_manual(TMC2, 1)
                self.heatlabel[label_a] = self.GetHeatValuefromTempCtrl(TMC2_A, heat)
            except:
                self.monitor[TMC2_A][2].setText("Err2")
                
            # Detector K monitoring
            try:
                result = self.hk.get_value_fromTMC(TMC2, "B")
                self.dtvalue[label_b] = self.GetValuefromTempCtrl(TMC2_B, 3, result, 0.1)
            except:
                self.QShowValue(TMC2_B, 0, "Err2", "warm")    
                
            # Detector K heating / manual heating
            try:
                heat = self.hk.get_heating_power(TMC2, 2)
                #heat_m = self.hk.get_heating_power_manual(TMC2, 2)
                self.heatlabel[label_b] = self.GetHeatValuefromTempCtrl(TMC2_B, heat)
            except:
                self.monitor[TMC2_B][2].setText("Err2")
                    
        else:
            self.QShowValue(TMC2_A, 0, "Err3", "warm")
            self.QShowValue(TMC2_B, 0, "Err3", "warm")   
        
            self.monitor[TMC2_A][2].setText("Err3")
            self.monitor[TMC2_B][2].setText("Err3")
            
        #print("End: get_value_fromTMC2")
            
          
    def get_value_fromTMC3(self):    
        #print("Start: get_value_fromTMC3")
          
        label_a = "tmc3-a"
        label_b = "tmc3-b"
        
        self.dtvalue[label_a] = "-999" 
        self.dtvalue[label_b] = "-999" 
        
        self.heatlabel[label_b] = "-999"
        
        #self.heatlabel_manual[label_b] = "-999" 
        
        if self.hk.comStatus[TMC3]:
            # Camera H monitoring
            try:
                result = self.hk.get_value_fromTMC(TMC3, "A")
                if result != None:
                    self.QShowValue(TMC3_A, 0, str(float(result)), "normal")
                    self.dtvalue[label_a] = " %8.3f" % float(result)
                else:
                    self.QShowValue(TMC3_A, 0, "Err1", "warm")
            except:
                self.QShowValue(TMC3_A, 0, "Err2", "warm")    
                
            # Detector H monitoring
            try:
                result = self.hk.get_value_fromTMC(TMC3, "B")
                self.dtvalue[label_b] = self.GetValuefromTempCtrl(TMC3_B, 4, result, 0.1)
            except:
                self.QShowValue(TMC3_B, 0, "Err2", "warm")    
                
            # Detector H heating / manual heating
            try:
                heat = self.hk.get_heating_power(TMC3, 2)
                #heat_m = self.hk.get_heating_power_manual(TMC3, 2)
                self.heatlabel[label_b] = self.GetHeatValuefromTempCtrl(TMC3_B, heat)
            except:
                self.monitor[TMC3_B][2].setText("Err2")
                    
        else:
            self.QShowValue(TMC3_A, 0, "Err3", "warm")
            self.QShowValue(TMC3_B, 0, "Err3", "warm")   
        
            self.monitor[TMC3_B][2].setText("Err3")
            
        #print("End: get_value_fromTMC3")
            
            
    
    def GetValuefromTempCtrl(self, port, idx, result, limit): 
        value = "-999"
        if result != None:
            if abs(float(self.SETP[idx])-float(result)) >= limit:
                state = "warm"   
            else:
                state = "normal"
            self.QShowValue(port, 0, str(float(result)), state)
            value = " %8.3f" % float(result)
        else:
            self.QShowValue(port, 0, "Err1", "warm")
        return value
        
    '''   
    def GetHeatValuefromTempCtrl(self, port, heat, heat_manual): 
        value1, value2 = "-999", "-999"
        if heat != None and heat_manual != None:
            str = "%.3f (%.3f)" % (float(heat), float(heat_manual))
            self.monitor[port][2].setText(str)
            value1 = " %8.3f" % float(heat)
            value2 = " %8.3f" % float(heat_manual)
        else:
            self.monitor[port][2].setText("Err1")
        return value1, value2
    '''
    
    def GetHeatValuefromTempCtrl(self, port, heat): 
        value  = "-999"
        if heat != None:
            self.monitor[port][2].setText(str(float(heat)))
            value = " %8.3f" % float(heat)
        else:
            self.monitor[port][2].setText("Err1")
        return value
           
    
    def get_value_fromTM(self):
        #print("Start: get_value_fromTM")
        
        label = ["" for _ in range(TM_CNT)]            
        tm = 0
        for key in self.hk.key_to_label:
            if key.find("tm-") < 0:
                continue
            label[tm] = key
            self.dtvalue[key] = "-999"
            tm += 1
        
        #20220511
        if self.hk.comStatus[TM]:
            try:
                all = self.hk.get_value_fromTM(0)
                if all != None:
                    result = all.split(',')
                    for i in range(TM_CNT):
                        self.QShowValue(TM_1+i, 0, str(float(result[i])), "normal")
                        self.dtvalue[label[i]] = " %8.3f" % float(result[i])
                else:
                    for i in range(TM_CNT):
                        self.QShowValue(TM_1+i, 0, "Err1", "warm")
            except:
                for i in range(TM_CNT):
                    self.QShowValue(TM_1+i, 0, "Err2", "warm")
            '''
            for i in range(TM_CNT):
                try:
                    result = self.hk.get_value_fromTM(i+1)
                    if result != None:
                        self.QShowValue(TM_1+i, 0, str(float(result)), "normal")
                        self.dtvalue[label[i]] = " %8.3f" % float(result)
                    else:
                        self.QShowValue(TM_1+i, 0, "Err1", "warm")
                except:
                    self.QShowValue(TM_1+i, 0, "Err2", "warm")   
            '''
        else:
            for i in range(TM_CNT):
                self.QShowValue(TM_1+i, 0, "Err3", "warm")
        
        #print("End: get_value_fromTM")    
        
    
    def get_value_fromVM(self):
        #print("Start: get_value_fromVM")
        self.dpvalue = "-999"
        if self.hk.comStatus[VMC]:
            try:
                result = self.hk.get_value_fromVM()
                if result != None:
                    self.dpvalue = result
                    self.QShowValueVM(self.dpvalue, "normal")
                else:   
                    self.QShowValueVM("ERR1", "warm")
            except:   
                self.QShowValueVM("ERR2", "warm")
        else:
            self.QShowValueVM("ERR3", "warm")
            
        #print("End: get_value_fromVM")
    
            
    def QShowValueVM(self, text, state):
        if state == "warm":
            self.QWidgetLabelColor(self.e_vacuum, "red")
        else:
            self.QWidgetLabelColor(self.e_vacuum, "black")
        self.e_vacuum.setText(text)
        
          
       
    def PeriodicFunc(self):
        
        if self.periodicbtn == PRESSED:
            self.ost=time.time()
    
            self.GetValue()
            self.st=time.time()
            if (self.st-self.ost)>=float(self.hk.Period)+0.00005 :
                self.tsh=(self.st-self.ost)-float(self.hk.Period)
            else :
                self.tsh=0.00000
            self.ost=self.st
    
            _t = int((float(self.hk.Period)-(time.time()-self.st)-self.tsh)*1000)
            timer = QTimer(self)
            if _t > 0:
                timer.singleShot(_t, self.PeriodicFunc)
            else:
                self.hk.logwrite(BOTH, "periodic is being called with negative time({}). Using default of 10s".format(_t))
                timer.singleShot(_t, self.PeriodicFunc)        
        
       
                    
    def GetValue(self):
        #print("Start: GetValue")
        
        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            try: 
                if self.hk.comStatus[TMC1]:
                    executor.submit(self.get_value_fromTMC1())
                if self.hk.comStatus[TMC2]:
                    executor.submit(self.get_value_fromTMC2())
                if self.hk.comStatus[TMC3]:
                    executor.submit(self.get_value_fromTMC3())
                if self.hk.comStatus[TM]:
                    executor.submit(self.get_value_fromTM())
                if self.hk.comStatus[VMC]:
                    executor.submit(self.get_value_fromVM())
                   
            except RuntimeError as e:
                self.hk.logwrite(BOTH, e)
            except Exception as e:
                self.hk.logwrite(BOTH, e)
            
        timer = QTimer(self)
        timer.singleShot(2000, self.LoggingFun)

        self.send_alert_if_needed()
        
        self.change_comStatus()        
                      
        #print("End: GetValue")
        
    
    def LoggingFun(self):     
        #print("Start: LoggingFun") 
        fname = strftime("%Y%m%d", localtime())+".log"
        f_p_name = self.hk.logpath+fname
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
            alert_status = "On(T>%d)" % self.hk.alert_temperature
        else:
            alert_status = "Off"

        hk_entries.append(alert_status)

        # hk_entries to string
        updated_datetime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.sts_updated.setText(updated_datetime)

        str_log1 = "\t".join([updated_datetime] + list(map(str, hk_entries))) + "\n"    #by hilee
        file.write(str_log1)

        str_log = "    ".join([updated_datetime] + list(map(str, hk_entries))) + "\n"    #by hilee      
        twrite = open(self.hk.webpath + 'tempweb.dat', 'w')
        twrite.write(str_log)
        twrite.close()

        file.close()

        # update log_time with Z0
        log_date, log_time = updated_datetime.split()
        
        hk_dict = hk_entries_to_dict(log_date, log_time, hk_entries)
                
        hk_dict.update(self.dtvalue_from_label.as_dict())
        ###
        #send...
        #print("End: LoggingFun")
        
            
    def send_alert_if_needed(self):
        if not self.chk_alert.isChecked():
            return 

        if self.check_temperature_danger():
            if (self.timestamp_alert is None) or \
               (time.time() - self.timestamp_alert > 1800.):
                try:
                    self.send_alert()
                    pass
                except Exception:
                    import traceback
                    traceback.print_exc()
                else:
                    self.timestamp_alert = time.time()

                self.set_alert_status_on()
        else:
            self.set_alert_status_off()
    
    
    def check_temperature_danger(self):
        # temperature of cold head #2
        label = self.hk.alert_label
        temp = self.hk.alert_temperature
        
        if float(self.dtvalue_from_label[label]) > temp:
            return True
        else:
            return False
        
        
    def send_alert(self):

        self.hk.logwrite(BOTH, "sending alerts! REAL")

        to = self.hk.alert_email

        title = "Warning : IGRINS2 needs YOU!"

        label = self.hk.alert_label
        temp = self.hk.alert_temperature

        msg = "Please check temperatures of IGRINS2!\n {} > {}".format(label, temp)
        
        self.hk.logwrite(BOTH, "sending alerts")

        self.send_gmail(to, title, msg)
        self.hk.logwrite(BOTH, "email was sent to")

        self.hk.logwrite(BOTH, "slacker message was sent")
        
    
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
        #self.timer_alert.stop()
        self.alert_status.setText("Okay")
        self.QWidgetLabelColor(self.alert_status, "black", "white") 
        
        
    def change_comStatus(self):
        for i in range(3):
            if self.comStatus_prev[i] != self.hk.comStatus[i]: 
                if self.hk.comStatus[i] == True:
                    self.QWidgetLabelColor(self.monlist[2*i], "green")
                    self.QWidgetLabelColor(self.monlist[2*i + 1], "green")
                else:
                    self.QWidgetLabelColor(self.monlist[2*i], "gray")
                    self.QWidgetLabelColor(self.monlist[2*i + 1], "gray")
        
        if self.comStatus_prev[TM] != self.hk.comStatus[TM]:        
            if self.hk.comStatus[TM] == True:
                for idx in range(8):
                    self.QWidgetLabelColor(self.monlist[2*TM + idx], "green")
            else:
                for idx in range(8):
                    self.QWidgetLabelColor(self.monlist[2*TM + idx], "gray")
        
        if self.comStatus_prev[VMC] != self.hk.comStatus[VMC]:    
            if self.hk.comStatus[VMC] == True:
                self.QWidgetLabelColor(self.sts_vacuum, "green")
            else:
                self.QWidgetLabelColor(self.sts_vacuum, "gray")
                
        if self.comStatus_prev[PDU] != self.hk.comStatus[PDU]:
            if self.hk.comStatus[PDU] == True:
                self.QWidgetLabelColor(self.sts_pdu, "red")
            else:
                self.QWidgetLabelColor(self.sts_pdu, "gray")
                
        #print(self.comStatus_prev, self.hk.comStatus)
        self.comStatus_prev = copy.copy(self.hk.comStatus)

            
        
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    
    app = QApplication(sys.argv)
        
    hk = MainWindow()
    hk.show()
        
    app.exec()
    

