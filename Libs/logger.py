# -*- coding: utf-8 -*-

"""
Created on Oct 26, 2022

Modified on , 2022

@author: hilee
"""

import os
import time as ti
import logging

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3

class LOG():

    def __init__(self, work_dir, iam):
        
        #self.work_dir = work_dir

        thatday = ti.strftime("%04Y%02m%02d.log", ti.localtime())
        path = "%s/Log/%s/" % (work_dir, iam)
        self.createFolder(path)

        self.logger = logging.getLogger("postprocessor")  
        self.logger.propagate = False
        self.logger.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s: %(message)s')
        Handler = logging.StreamHandler()
        Handler.setFormatter(formatter)

        formatter2 = logging.Formatter('%(asctime)s: %(message)s')
        fileHandler = logging.FileHandler(path + thatday)
        fileHandler.setLevel(logging.ERROR)
        fileHandler.setFormatter(formatter)
        
        self.logger.addHandler(Handler)
        self.logger.addHandler(fileHandler)
    

    def createFolder(self, dir):
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
        except OSError:
            print("Error: Creating directory. " + dir)
        
    
    def send(self, level, message):        
        if level > 0:
            self.logger.critical(message)
        else:
            self.logger.warning(message)
            
            
    def logwrite(self, iam, level, message):
        level_name = ""
        if level == DEBUG:
            level_name = "DEBUG"
        elif level == INFO:
            level_name = "INFO"
        elif level == WARNING:
            level_name = "WARNING"
        elif level == ERROR:
            level_name = "ERROR"
        
        msg = "[%s:%s] %s" % (iam, level_name, message)
        self.send(level, msg)
                      
            


if __name__ == "__main__":
    
    log = LOG("/home/ics/IGRINS")
    
    log.send(DEBUG, "debug test")
    log.send(INFO, "info test")
    log.send(WARNING, "warning test")
    log.send(ERROR, "error test")
    #log.send(LOG_CRITICAL, "critical test")

