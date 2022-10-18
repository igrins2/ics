# -*- coding: utf-8 -*-

"""
Created on Dec 8, 2021

@author: hilee
"""

from PySide2.QtWidgets import *
import sys
import HK_gui
import unittest

class CustomTests(unittest.TestCase):
    
    def test_runs(self):
        app = QApplication(sys.argv)
        hk = HK_gui.MainWindow()
        app.exec_()
        

if __name__ == "__main__":
    unittest.main()
        
        
