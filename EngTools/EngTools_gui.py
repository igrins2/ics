# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Dec 14, 2022

@author: hilee
"""

import sys
from ui_EngTools import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import time as ti
import subprocess

from Libs.MsgMiddleware import *
from EngTools_def import *

import Libs.SetConfig as sc
from  Libs.logger import *


class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        
        self.iam = "EngTools"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        self.setWindowTitle("EngTools 0.2")
                
        self.init_events()
        
        #self.radio_real.setChecked(True)
        #self.simulation = False
            
        # ---------------------------------------------------------------
        # start subprocess - temp ctrl, monitor, pdu, uploader
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(ini_file)
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.main_gui_ex = self.cfg.get(MAIN, 'main_gui_exchange')
        self.main_gui_q = self.cfg.get(MAIN, 'main_gui_routing_key')
        self.gui_main_ex = self.cfg.get(MAIN, 'gui_main_exchange')     
        self.gui_main_q = self.cfg.get(MAIN, 'gui_main_routing_key')
        
        self.proc_sub = [None for _ in range(COM_CNT)]
        
        self.proc_simul = None
        
        self.proc = [None for _ in range(SERV_CONNECT_CNT)]
        
        self.producer = None
        self.consumer = None
        
        self.bt_runHKP.setEnabled(False)
        self.bt_runDTP.setEnabled(False)
        
        self.connect_to_server_main_ex()
        self.connect_to_server_gui_q()
                
        
    def closeEvent(self, event: QCloseEvent) -> None:
        
        for i in range(COM_CNT):
            if self.proc_sub[i] != None:
                print(self.proc_sub[i].pid)
                #ti.sleep(20)
                self.proc_sub[i].terminate()
                self.log.send(self.iam, INFO, str(self.proc_sub[i].pid) + " exit")
        
        for i in range(SERV_CONNECT_CNT):
            if self.proc[i] != None:
                print(self.proc[i].pid)
                #ti.sleep(20)
                self.proc[i].terminate()
                self.log.send(self.iam, INFO, str(self.proc[i].pid) + " exit")
                
        if self.proc_simul != None:
            print(self.proc_simul.pid)
            #ti.sleep(20)
            self.proc_simul.terminate()
            self.log.send(self.iam, INFO, str(self.proc_simul.pid) + " exit")
                
        for th in threading.enumerate():
            self.log.send(self.iam, DEBUG, th.name + " exit.")
                    
        if self.producer != None:
            self.producer.__del__()
                                                                
        return super().closeEvent(event)
        
        
    def init_events(self):
        self.radio_inst_simul.clicked.connect(self.set_mode)
        self.radio_real.clicked.connect(self.set_mode)
        
        self.bt_runHKP.clicked.connect(self.run_HKP)
        self.bt_runDTP.clicked.connect(self.run_DTP)
        
        
    def start_sub_system(self):
        
        simul_mode = str(self.simulation)
        
        comport = []
        com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "lt", "ut", "uploader"]
        for name in com_list:
            if name != com_list[UPLOADER]:
                comport.append(self.cfg.get(HK, name + "-port"))
    
        for i in range(COM_CNT-1):
            if self.proc_sub[i] != None:
                continue
                
            if i <= TMC3:
                cmd = "%sworkspace/ics/HKP/temp_ctrl.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i], simul_mode])
            elif i == TM or i == VM:
                cmd = "%sworkspace/ics/HKP/monitor.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i], simul_mode])
            elif i == PDU:
                cmd = "%sworkspace/ics/HKP/pdu.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, simul_mode])
            else:
                cmd = "%sworkspace/ics/HKP/motor.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, com_list[i], comport[i], simul_mode])                
                        
        if self.proc_sub[UPLOADER] == None:
            cmd = "%sworkspace/ics/HKP/uploader.py" % WORKING_DIR
            self.proc_sub[UPLOADER] = subprocess.Popen(['python', cmd, simul_mode])        
        
        
    #-------------------------------
    # dt -> sub: use hk ex
    def connect_to_server_main_ex(self):
        # RabbitMQ connect  
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.main_gui_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
    
         
    #-------------------------------
    # sub -> dt: use hk q
    def connect_to_server_gui_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.gui_main_ex)      
        self.consumer.connect_to_server()
        self.consumer.define_consumer(self.gui_main_q, self.callback_gui)       
        
        th = threading.Thread(target=self.consumer.start_consumer)
        th.daemon = True
        th.start()
        
        
    #-------------------------------
    # rev <- sub        
    def callback_gui(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
                
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        if param[0] == ALIVE:
            if param[1] == HK:
                self.bt_runHKP.setEnabled(False)
            elif param[1] == DT:
                self.bt_runDTP.setEnabled(False)
            
                msg = "%s %s %d" % (TEST_MODE, DT, self.simulation)
                self.producer.send_message(DT, self.main_gui_q, msg)

        elif param[0] == EXIT:        
            if param[1] == HK:
                self.bt_runHKP.setEnabled(True)
                self.proc[HKP] = None
                
            elif param[1] == DT:
                self.bt_runDTP.setEnabled(True)     
                self.proc[DTP] = None
                
            self.radio_inst_simul.setEnabled(True)
            self.radio_real.setEnabled(True)   
    
    
    def set_mode(self):                    
        
        for i in range(COM_CNT):
            if self.proc_sub[i] != None:
                if self.proc_sub[i].poll() == None:
                    #print(self.proc_sub[i].pid)
                    #ti.sleep(20)
                    #self.proc_sub[i].terminate()
                    self.proc_sub[i].kill()
                    self.proc_sub[i] = None
        
        if self.radio_inst_simul.isChecked():
            self.simulation = True
            
            if self.proc_simul == None:
                cmd = "%sworkspace/ics/igos2_simul/run_hk_simulator.py" % WORKING_DIR
                self.proc_simul = subprocess.Popen(["python", cmd])
            
        elif self.radio_real.isChecked():
            self.simulation = False
            
            if self.proc_simul != None:
                if self.proc_simul.poll() == None:
                    #print(self.proc_simul.pid)
                    #ti.sleep(20)
                    #self.proc_simul.terminate()
                    self.proc_simul.kill()
                    self.proc_simul = None
                
        self.start_sub_system()
        
        self.bt_runHKP.setEnabled(True)
        self.bt_runDTP.setEnabled(True)   
        
        msg = "%s %s %d" % (TEST_MODE, DT, self.simulation)
        self.producer.send_message(DT, self.main_gui_q, msg)  
        
        
    def run_HKP(self):
            
        if self.proc[HKP] == None:
            self.proc[HKP] = subprocess.Popen(['python', WORKING_DIR + 'workspace/ics/HKP/HK_gui.py'])
        
        self.radio_inst_simul.setEnabled(False)
        self.radio_real.setEnabled(False)
        
           
    def run_DTP(self):
        
        if self.proc[DTP] == None:
            self.proc[DTP] = subprocess.Popen(['python', WORKING_DIR + 'workspace/ics/DTP/DT_gui.py'])
        
        self.radio_inst_simul.setEnabled(False)
        self.radio_real.setEnabled(False)
        
        msg = "%s %s %d" % (TEST_MODE, DT, self.simulation)
        self.producer.send_message(DT, self.main_gui_q, msg)     
        
    
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
    