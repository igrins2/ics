# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

@author: hilee
"""

import sys
from ui_EngineeringTools import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Engineering Tools 0.1")
        
        
    def connect_to_server(self):
        '''
        connect to RabbitMQ server
        '''
        pass
    
    
    def runHKP(self):
        pass
    
    def runSCP(self):
        pass
    
    def runDTP(self):
        pass
    
    
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