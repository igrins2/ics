# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Jun 28, 2022

@author: hilee
"""

import os
from SC_def import *
import time
from time import localtime, strftime

import Libs.SetConfig as sc
import Libs.hk_field_definition as test
import Libs.ics_server as serv
class SC():
    def __init__(self, gui=False):
        
        self.gui = gui
                
        #--------------------------------------------
        # load ini file
        cfg = sc.LoadConfig("/home/ics/IGRINS/Config/IGRINS.ini")
        
        # ICS
        self.mainlogpath = cfg.get(MAIN, "main-log-location")
        
        self.logwrite(BOTH, "start SCP!!!")
        
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')

        # exchange - queue
        self.ics_ex = cfg.get(TITLE, 'ics_exchange')
        self.ics_q = cfg.get(TITLE, 'ics_routing_key')

        self.dcs_ex = cfg.get(TITLE, 'dcss_exchange')
        self.dcs_q = cfg.get(TITLE, 'dcss_routing_key')
        
        self.fits_path = cfg.get(TITLE, 'fits_path')
        #--------------------------------------------
        
        self.connect_to_server()
        
        
    def connect_to_server(self):
        # RabbitMQ connect
        self.serv = ICS_SERVER(self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ics_ex, self.ics_q, "direct", self.dcs_ex, self.dcs_q)
        self.connection, self.channel = self.serv.connect_to_server(TITLE)
        
        # RabbitMQ: define producer
        self.serv.define_producer(self.channel, TITLE)
        
        
    def send_message(self, message):
        self.serv.send_message(self.channel, TITLE, TARGET, message)
        
        
    def initialize2(self):
        self.send_message(CMD_INITIALIZE2)
    
    def downloadMCD(self):
        pass
    
    def set_detector(self):
        pass
    
    def set_fsmode(self, mode):
        pass
    
    def set_win_param(self, x1, x2, y1, y2):
        pass
    
    def set_fs_param(self, p1, p2, p3, fowler_time, p5):
        pass
    
        
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
        