# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Nov 10, 2022

@author: hilee
"""

import os, sys
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from SC_def import *
import time
from time import localtime, strftime

import Libs.SetConfig as sc
import Libs.rabbitmq_server as serv
from Libs.logger import *

import threading

class SC():
    def __init__(self):
    
        self.log = LOG(WORKING_DIR + "IGRINS", IAM)        
        self.iam = "core"
        self.log.logwrite(self.iam, INFO, "start")
                        
        #--------------------------------------------
        # load ini file
        cfg = sc.LoadConfig(WORKING_DIR + "IGRINS/Config/IGRINS.ini")
        
        # ICS
        #self.mainlogpath = cfg.get(MAIN, "main-log-location")
                
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')
        
        self.main_sc_ex = cfg.get(MAIN, 'main_sc_exchange')     
        self.main_sc_q = cfg.get(MAIN, 'main_sc_routing_key')
        self.sc_main_ex = cfg.get(MAIN, 'sc_main_exchange')
        self.sc_main_q = cfg.get(MAIN, 'sc_main_routing_key')

        # exchange - queue
        self.ics_ex = cfg.get(IAM, 'scp_exchange')
        self.ics_q = cfg.get(IAM, 'scp_routing_key')

        self.dcs_ex = cfg.get(IAM, 'dcss_exchange')
        self.dcs_q = cfg.get(IAM, 'dcss_routing_key')
        
        self.fits_path = cfg.get(IAM, 'fits_path')
        self.alive_chk_interval = int(cfg.get(IAM, 'alive-check-interval'))
        #--------------------------------------------
        
        self.ROI_mode = False
        self.output_channel = 32
        self.x_start, self.x_stop, self.y_start, self.y_stop = 0, FRAME_X-1, 0, FRAME_Y
        
        
        
        
    def __del__(self):
        self.log.logwrite(self.iam, INFO, "core closing...")

        for th in threading.enumerate():
            self.log.logwrite(self.iam, INFO, th.name + " exit.")

        if self.queue_ics:
            self.channel_ics_q.stop_consuming()
            self.connection_ics_q.close()

        self.log.logwrite(self.iam, INFO, "core closed!")
        
        
        
    def connect_to_server_ics_ex(self):
        # RabbitMQ connect        
        self.connection_ics_ex, self.channel_ics_ex = serv.connect_to_server(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_ics_ex:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_ics_ex, "direct", self.ics_ex)
        
        
    def send_message_to_ics(self, simul_mode, message):
            param = "%d %s" % (simul_mode, message)
            serv.send_message(IAM, TARGET, self.channel_ics_ex, self.ics_ex, self.ics_q, message)
            

    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
    def initialize2(self, slmul_mode):
        self.send_message_to_ics(slmul_mode, CMD_INITIALIZE2)
        
        
    def downloadMCD(self, simul_mode):
        self.send_message_to_ics(simul_mode, CMD_DOWNLOAD)
        
    
    def set_detector(self, slmul_mode, type, channel):
        msg = "%s %d %d" % (CMD_SETDETECTOR, MUX_TYPE, channel)
        self.sc.send_message_to_ics(slmul_mode, msg)
    
        
    def set_win_param(self, slmul_mode, x1, x2, y1, y2):
        param = "%s %d %d %d %d" % (CMD_SETWINPARAM, x1, x2, y1, y2)
        self.send_message_to_ics(slmul_mode, param)
        
        
    def set_fs_param(self, slmul_mode, exptime):
        #fsmode
        self.send_message_to_ics(slmul_mode, CMD_SETFSMODE + " 1")    
        
        #setparam
        param = " 1 1 1 %f 1" % exptime
        self.send_message_to_ics(slmul_mode, CMD_SETFSPARAM + param)
    
    
    def acquireramp(self, slmul_mode, ROI_mode):
        msg = "%s %d" % (CMD_ACQUIRERAMP, self.ROI_mode)
        self.send_message_to_ics(slmul_mode, msg)
        
          
    def alive_check(self, slmul_mode):
        self.send_message_to_ics(slmul_mode, "alive?")
        
        
    def stop_acquistion(self, slmul_mode):        
        self.send_message_to_ics(slmul_mode, CMD_STOPACQUISITION)
        
        