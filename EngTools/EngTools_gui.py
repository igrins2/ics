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

import subprocess
from EngTools_def import *

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("EngTools 0.1")
        
        self.workdir = os.getcwd()
        print(self.workdir)
        
        self.init_events()
        
        self.proc = [None for _ in range(4)]
        
        
    def closeEvent(self, *args, **kwargs):
        
        for i in range(4):
            if self.proc[i] != None:
                self.proc[i].terminate()
                print(self.proc[i].pid, "exit")
                    
        return QMainWindow.closeEvent(self, *args, **kwargs)
        
        
    def init_events(self):
        self.bt_runHKP.clicked.connect(self.runHKP)
        self.bt_runMACIE.clicked.connect(self.runMACIE)
        self.bt_runSCP.clicked.connect(self.runSCP)
        self.bt_runDTP.clicked.connect(self.runDTP)
        
        
    def connect_to_server(self):
        '''
        connect to RabbitMQ server
        '''
        pass
    
    
    def runHKP(self):
        self.proc[HKP] = subprocess.Popen(['python', self.workdir + '/ics/HKP/HK_gui.py'])
        
        
    def runMACIE(self):
        self.proc[MACIE] = subprocess.Popen(['python', self.workdir + '/ics/MACIE/macie_gui.py'])
    
    
    def runSCP(self):        
        self.proc[SCP] = subprocess.Popen(['python', self.workdir + '/ics/SCP/SC_gui.py'])
                   
    
    def runDTP(self):
        self.proc[DTP] = subprocess.Popen(['python', self.workdir + '/ics/DTP/DT_gui.py'])
    
    
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