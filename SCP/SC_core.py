# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Jun 28, 2022

@author: hilee
"""

import os
from SCP.SC_def import *
import time
from time import localtime, strftime

class SC():
    def __init__(self, gui=False):
        
        self.gui = gui
        print("start SCP!!!")
        
        
    def logwrite(self, option, event):
        '''
        Function that write to file for Logging
        event : Logging Sentence
        option :  LOGGING(1) - Write to File
                  CMDLINE(2) - Write to Command Line
                  BOTH(3) - Wrte to File and Command Line
        '''
        if option == CMDLINE:
            print(event)
        else:
            fname = strftime("%Y%m%d", localtime())+".log"
            f_p_name = self.mainlogpath+fname
            if os.path.isfile(f_p_name):
                file=open(f_p_name,'a+')
            else:
                file=open(f_p_name,'w')
            
            if option == LOGGING:
                file.write(strftime("[%Y-%m-%d %H:%M:%S]", localtime()) + ": " + event + "\n")
                file.close()
        
            elif option == BOTH:
                file.write(strftime("[%Y-%m-%d %H:%M:%S]", localtime()) + ": " + event + "\n")
                file.close()
                print(event)
        