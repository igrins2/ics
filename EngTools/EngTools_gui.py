# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Oct 20, 2022

@author: hilee
"""

import sys, os
from ui_EngTools import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import time as ti
import subprocess
from EngTools_def import *

import Libs.SetConfig as sc
from  Libs.logger import *

dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"

MAIN = "MAIN"
HK = "HK"
COM_CNT = 9

TMC3 = 2
TM = 3
VM = 4
PDU = 5
LT = 6
UT = 7
UPLOADER = 8

SERV_CONNECT_CNT = 4 #hk, dt

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        
        self.iam = "EngTools"
        
        self.log = LOG(WORKING_DIR + "/IGRINS", MAIN)  
        self.log.send(self.iam, "INFO", "start")
        
        self.setupUi(self)
        self.setWindowTitle("EngTools 0.2")
                
        self.init_events()
            
        # ---------------------------------------------------------------
        # start subprocess - temp ctrl, monitor, pdu, uploader
        # load ini file
        ini_file = WORKING_DIR + "/IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        self.proc_sub = [None for _ in range(COM_CNT)]
        
        comport = []
        com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "lt", "ut", "uploader"]
        for name in com_list:
            if name != com_list[UPLOADER]:
                comport.append(cfg.get(HK, name + "-port"))
        
        for i in range(COM_CNT-1):
            if i <= TMC3:
                cmd = "%sworkspace/ics/HKP/temp_ctrl.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i]])
            
            elif i == TM or i == VM:
                cmd = "%sworkspace/ics/HKP/monitor.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i]])
            elif i == PDU:
                cmd = "%sworkspace/ics/HKP/pdu.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd])
            else:
                cmd = "%sworkspace/ics/HKP/motor.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, com_list[i], comport[i]])                
        
        cmd = "%sworkspace/ics/HKP/uploader.py" % WORKING_DIR
        self.proc_sub[UPLOADER] = subprocess.Popen(['python', cmd])
        
        self.proc = [None for _ in range(SERV_CONNECT_CNT)]
        
        
    def closeEvent(self, *args, **kwargs):
        
        for i in range(SERV_CONNECT_CNT):
            if self.proc[i] != None:
                self.proc[i].terminate()
                self.log.send(self.iam, "INFO", str(self.proc[i].pid) + " exit")
                
        for i in range(COM_CNT):
            if self.proc_sub[i] != None:
                self.proc_sub[i].terminate()
                                                
        return QMainWindow.closeEvent(self, *args, **kwargs)
        
        
    def init_events(self):
        self.bt_runHKP.clicked.connect(self.runHKP)
        self.bt_runDTP.clicked.connect(self.runDTP)
        
        
    def connect_to_server(self):
        '''
        connect to RabbitMQ server
        '''
        pass
    
    
    def runHKP(self):
        self.proc[HKP] = subprocess.Popen(['python', WORKING_DIR + 'workspace/ics/HKP/HK_gui.py'])
        
           
    def runDTP(self):
        self.proc[DTP] = subprocess.Popen(['python', WORKING_DIR + 'workspace/ics/DTP/DT_gui.py'])
    
    
    def send_to_GMP(self):
        pass
    
    
    def send_to_TCS(self):
        pass    
    
    

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    app = QApplication(sys.argv)
        
    ETs = MainWindow()
    ETs.show()
        
    app.exec()