# -*- coding: utf-8 -*-

"""
Created on July 7, 2022

Modified on 

@author: hilee
"""

import sys
from ui_macie import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("MACIE control 0.1")
        
        
        
    def closeEvent(self, *args, **kwargs):
        
        print("Closing %s : " % sys.argv[0])
        
        return QMainWindow.closeEvent(self, *args, **kwargs)
        
        
        
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    
    app = QApplication(sys.argv)
        
    macie = MainWindow()
    macie.show()
        
    app.exec_()
