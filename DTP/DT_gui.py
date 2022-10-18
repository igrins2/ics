# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

@author: hilee
"""

import sys
from ui_DTP import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Data Taking Package 0.1")
        

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    app = QApplication(sys.argv)
        
    dt = MainWindow()
    dt.show()
        
    app.exec()