# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Nov 7, 2022 

@author: hilee
"""

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from DT_def import *
import time
from time import localtime, strftime

import Libs.SetConfig as sc
import Libs.rabbitmq_server as serv
from Libs.logger import *

import threading
class DT():
    def __init__(self, gui=False):
        
        self.log = LOG(WORKING_DIR + "IGRINS", IAM)
        self.iam = "CORE"
        self.logwrite(INFO, "start DCS core!!!")
        
        #--------------------------------------------
        # load ini file
        cfg = sc.LoadConfig(WORKING_DIR + "IGRINS/Config/IGRINS.ini")
        
        # ICS
        #self.mainlogpath = cfg.get(MAIN, "main-log-location")
                
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')
        
        self.main_dt_ex = cfg.get(MAIN, 'main_dt_exchange')     
        self.main_dt_q = cfg.get(MAIN, 'main_dt_routing_key')
        self.dt_main_ex = cfg.get(MAIN, 'dt_main_exchange')
        self.dt_main_q = cfg.get(MAIN, 'dt_main_routing_key')
        
        self.hk_dt_ex = cfg.get(MAIN, 'hk_dt_exchange')     
        self.hk_dt_q = cfg.get(MAIN, 'hk_dt_routing_key')
        self.dt_hk_ex = cfg.get(MAIN, 'dt_hk_exchange')
        self.dt_hk_q = cfg.get(MAIN, 'dt_hk_routing_key')

        # exchange - queue, list
        self.ics_ex = [cfg.get(IAM, 'dt_dcsh_exchange'), cfg.get(IAM, 'dt_dcsk_exchange')]
        self.ics_q = [cfg.get(IAM, 'dt_dcsh_routing_key'), cfg.get(IAM, 'dt_dcsk_routing_key')]

        self.dcs_ex = [cfg.get(IAM, 'dcsh_dt_exchange'), cfg.get(IAM, 'dcsk_dt_exchange')]
        self.dcs_q = [cfg.get(IAM, 'dcsh_dt_routing_key'), cfg.get(IAM, 'dcsk_dt_routing_key')]
        
        self.fits_path = cfg.get(IAM, 'fits_path')
        self.alive_chk_interval = int(cfg.get(IAM, 'alive-check-interval'))
        #--------------------------------------------
        
        self.connection_ics_ex = [None, None]
        self.channel_ics_ex = [None, None]
        
        self.output_channel = 32
        
        
        def __del__(self):
            self.logwrite(INFO, "DTP core closing...")

            for th in threading.enumerate():
                self.logwrite(INFO, th.name + " exit.")

            if self.queue_ics:
                self.channel_ics_q.stop_consuming()
                self.connection_ics_q.close()

            self.logwrite(INFO, "DTP core closed!")
        
        
        
    def logwrite(self, level, message):
        level_name = ""
        if level == DEBUG:
            level_name = "DEBUG"
        elif level == INFO:
            level_name = "INFO"
        elif level == WARNING:
            level_name = "WARNING"
        elif level == ERROR:
            level_name = "ERROR"
        
        msg = "[%s:%s] %s" % (self.iam, level_name, message)
        self.log.send(level, msg)
        
        
    def connect_to_server_ics_ex(self, dc_idx):
        # RabbitMQ connect        
        self.connection_ics_ex[dc_idx], self.channel_ics_ex[dc_idx] = serv.connect_to_server(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_ics_ex[dc_idx]:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_ics_ex[dc_idx], "direct", self.ics_ex[dc_idx])
        
        
    def send_message_to_ics(self, dc_idx, simul_mode, message):
            param = "%d %s" % (simul_mode, message)
            serv.send_message(IAM, TARGET[dc_idx], self.channel_ics_ex[dc_idx], self.ics_ex[dc_idx], self.ics_q[dc_idx], message)


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
    def initialize2(self, dc_idx, slmul_mode):
        self.send_message_to_ics(dc_idx, slmul_mode, CMD_INITIALIZE2)
        
        
    def downloadMCD(self, dc_idx, simul_mode):
        self.send_message_to_ics(dc_idx, simul_mode, CMD_DOWNLOAD)
        
    
    def set_detector(self, dc_idx, slmul_mode, type, channel):
        msg = "%s %d %d" % (CMD_SETDETECTOR, MUX_TYPE, channel)
        self.sc.send_message_to_ics(dc_idx, slmul_mode, msg)
    
          
    def set_fs_param(self, dc_idx, slmul_mode, exptime):
        #fsmode
        self.send_message_to_ics(dc_idx, slmul_mode, CMD_SETFSMODE + " 1")    
        
        #setparam
        param = " 1 1 1 %f 1" % exptime
        self.send_message_to_ics(dc_idx, slmul_mode, CMD_SETFSPARAM + param)
    
    
    def acquireramp(self, dc_idx, slmul_mode):
        msg = "%s 0" % CMD_ACQUIRERAMP
        self.send_message_to_ics(dc_idx, slmul_mode, msg)
        
          
    def alive_check(self, dc_idx, slmul_mode):
        self.send_message_to_ics(dc_idx, slmul_mode, "alive?")
        
        
    def stop_acquistion(self, dc_idx, slmul_mode):        
        self.send_message_to_ics(dc_idx, slmul_mode, CMD_STOPACQUISITION)
