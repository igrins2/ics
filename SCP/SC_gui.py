# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Jun 28, 2022

@author: hilee
"""

import sys
from ui_SCP import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Slit Camera Package 0.1")
        
        
        
    def closeEvent(self, *args, **kwargs):
        
        print("Closing %s : " % sys.argv[0])
        
        return QMainWindow.closeEvent(self, *args, **kwargs)
        
        
        
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    
    app = QApplication(sys.argv)
        
    sc = MainWindow()
    sc.show()
        
    app.exec_()