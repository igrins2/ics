# -*- coding: utf-8 -*-

"""
Created on Oct 26, 2022

Modified on , 2022

@author: hilee
"""

import os, sys
import time as ti
import logging

import threading
from MsgMiddleware import *
import SetConfig as sc

# define
MAIN = "MAIN"
LOGGER = "logger"

SEND_LOGGER = "SendLogger"
EXIT_LOGGER = "ExitLogger"

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3

class LOG():

    def __init__(self, work_dir, iam):
        
        self.iam = LOGGER
        
        # load ini file
        cfg = sc.LoadConfig(work_dir + "/Config/IGRINS.ini")
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self._logger_ex = cfg.get(MAIN, "_logger_exchange")     
        self._logger_q = cfg.get(MAIN, "_logger_routing_key")
        
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
        
        self.consumer = None
        self.connect_to_server_q()
        
        
    def __del__(self):
        print("Closing %s" % self.iam)
        
        for th in threading.enumerate():
            print(th.name + " exit.")
            
        #self.consumer.stop_consumer()
        self.consumer.__del__()
    

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
        
    
    #-------------------------------
    def connect_to_server_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self._logger_ex, "direct")      
        self.consumer.connect_to_server()
        self.consumer.define_consumer(self._logger_q, self.callback)
        
        th = threading.Thread(target=self.consumer.start_consumer)
        th.start()
        
        #th = threading.Thread(target=self.consumer.define_consumer, args=(self._logger_q, self.callback))
        #th.start()
            
            
    def callback(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split(" ")
        
        msg = ""
        for i in range(3, len(param)):
            msg += param[i] + " "

        if param[0] == SEND_LOGGER:
            self.logwrite(param[1], int(param[2]), msg)      
            
        elif param[0] == EXIT_LOGGER:
            self.logwrite(param[1], int(param[2]), msg)
            self.__del__()
            

if __name__ == "__main__":
   
    log = LOG("/home/ics/IGRINS", "Main")
    
    '''
    log.send(DEBUG, "debug test")
    log.send(INFO, "info test")
    log.send(WARNING, "warning test")
    log.send(ERROR, "error test")
    #log.send(LOG_CRITICAL, "critical test")
    '''

    #log.__del__()
