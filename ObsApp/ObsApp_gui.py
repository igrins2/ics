# -*- coding: utf-8 -*-

"""
Created on Oct 21, 2022

Modified on , 2022

@author: hilee
"""

import sys, os
from ui_ObsApp import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("ObsApp 0.1")
        
        
        
        
    def closeEvent(self, *args, **kwargs):
        
        
        return QMainWindow.closeEvent(self, *args, **kwargs)
        
        
 
    

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    app = QApplication(sys.argv)
        
    ETs = MainWindow()
    ETs.show()
        
    app.exec()