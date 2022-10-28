# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Jun 28, 2022

@author: hilee
"""

import os, sys
from SC_def import *
import time
from time import localtime, strftime

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import Libs.SetConfig as sc
import Libs.rabbitmq_server as serv
from Libs.logger import *

import threading

class SC():
    def __init__(self):
    
        self.log = LOG(WORKING_DIR + "IGRINS")
        
        self.iam = "CORE"
        #self.target = "GUI"

        self.logwrite(INFO, "start DCS core!!!")
                        
        #--------------------------------------------
        # load ini file
        cfg = sc.LoadConfig(WORKING_DIR + "/IGRINS/Config/IGRINS.ini")
        
        # ICS
        #self.mainlogpath = cfg.get(MAIN, "main-log-location")
                
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')

        # exchange - queue
        self.ics_ex = cfg.get(IAM, 'ics_exchange')
        self.ics_q = cfg.get(IAM, 'ics_routing_key')

        self.dcs_ex = cfg.get(IAM, 'dcss_exchange')
        self.dcs_q = cfg.get(IAM, 'dcss_routing_key')
        
        self.fits_path = cfg.get(IAM, 'fits_path')
        self.alive_chk_interval = int(cfg.get(IAM, 'alive-check-interval'))
        #--------------------------------------------
        
        self.simulation_mode = True     #from EngTools
        
        self.ROI_mode = False
        self.output_channel = 32
        self.x_start, self.x_stop, self.y_start, self.y_stop = 0, FRAME_X-1, 0, FRAME_Y
        
        self.connect_to_server_ics_ex()
        self.connect_to_server_ics_q()

        
        
    def __del__(self):
        self.logwrite(INFO, "SCP core closing...")

        for th in threading.enumerate():
            self.logwrite(INFO, th.name + " exit.")

        if self.queue_ics:
            self.channel_ics_q.stop_consuming()
            self.connection_ics_q.close()

        self.logwrite(INFO, "SCP core closed!")
        
        
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
        
        
    def connect_to_server_ics_ex(self):
        # RabbitMQ connect        
        self.connection_ics_ex, self.channel_ics_ex = serv.connect_to_server(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_ics_ex:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_ics_ex, "direct", self.dcs_ex)
        
        
    def send_message_to_ics(self, simul_mode, message):
            param = "%d %s" % (simul_mode, message)
            serv.send_message(IAM, TARGET, self.channel_ics_ex, self.dcs_ex, self.dcs_q, message)
            
            
    def connect_to_server_ics_q(self):
        # RabbitMQ connect
        self.connection_ics_q, self.channel_ics_q = serv.connect_to_server(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_ics_q:
            # RabbitMQ: define consumer
            self.queue_ics = serv.define_consumer(IAM, self.channel_ics_q, "direct", self.ics_ex, self.ics_q)

            th = threading.Thread(target=self.consumer_ics)
            th.start()
            
            
    # RabbitMQ communication    
    def consumer_ics(self):
        try:
            self.channel_ics_q.basic_consume(queue=self.queue_ics, on_message_callback=self.callback_ics, auto_ack=True)
            self.channel_ics_q.start_consuming()
        except Exception as e:
            if self.channel_ics_q:
                self.logwrite(ERROR, "The communication of server was disconnected!")
                
                
    def callback_ics(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == "alive":
            self.dcss_sts = True               
        
        elif param[0] == CMD_INITIALIZE2:
            #downloadMCD
            self.send_message_to_ics(self.simulation_mode, CMD_DOWNLOAD)
            
        elif param[0] == CMD_DOWNLOAD:
            #setdetector
            msg = "%s %d %d" % (CMD_SETDETECTOR, MUX_TYPE, self.output_channel)
            self.send_message_to_ics(self.simulation_mode, msg)
            
        elif param[0] == CMD_SETFSPARAM:
            #acquire
            msg = "%s %d" % (CMD_ACQUIRERAMP, self.ROI_mode)
            self.send_message_to_ics(self.simulation_mode, msg)  

        elif param[0] == CMD_ACQUIRERAMP:
            pass
        
        elif param[0] == CMD_STOPACQUISITION:
            pass


    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
    def initialize2(self):
        self.send_message_to_ics(self.simulation_mode, CMD_INITIALIZE2)
    
        
    def set_win_param(self, x1, x2, y1, y2):
        param = "%s %d %d %d %d" % (CMD_SETWINPARAM, x1, x2, y1, y2)
        self.send_message_to_ics(self.simulation_mode, param)
    
    
    def acquireramp(self):
        #fsmode
        self.send_message_to_ics(self.simulation_mode, CMD_SETFSMODE + " 1")    
        
        #setparam
        param = " 1 1 1 %f 1" % self.fowler_exp
        self.send_message_to_ics(self.simulation_mode, CMD_SETFSPARAM + param)
        
          
    def alive_check(self):
        self.send_message_to_ics(self.simulation_mode, "alive?")
        
        
    def stop_acquistion(self):        
        self.send_message_to_ics(self.simulation_mode, CMD_STOPACQUISITION)
        
        