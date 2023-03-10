# -*- coding: utf-8 -*-
"""
Created on Feb 15, 2023

Modified on 

@author: hilee
"""

import os, sys
import threading

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from ObsApp.ObsApp_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

class Inst_Seq(threading.Thread):
    
    def __init__(self, simul='0'):
        
        self.iam = "InstSeq"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")
                    
        # ---------------------------------------------------------------   
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(ini_file)
                
        self.ics_ip_addr = self.cfg.get(MAIN, "ip_addr")
        self.ics_id = self.cfg.get(MAIN, "id")
        self.ics_pwd = self.cfg.get(MAIN, "pwd")
        
        self.InstSeq_ObsApp_ex = self.cfg.get(MAIN, 'main_gui_exchange')
        self.InstSeq_ObsApp_q = self.cfg.get(MAIN, 'main_gui_routing_key')
        self.ObsApp_InstSeq_ex = self.cfg.get(MAIN, 'gui_main_exchange')     
        self.ObsApp_InstSeq_q = self.cfg.get(MAIN, 'gui_main_routing_key')
        
        self.InstSeq_dcs_ex = self.cfg.get(DT, 'dt_dcs_exchange')     
        self.InstSeq_dcs_q = self.cfg.get(DT, 'dt_dcs_routing_key')
        self.dcs_InstSeq_ex = self.cfg.get(DT, 'dcs_dt_exchange')
        self.dcs_InstSeq_q = self.cfg.get(DT, 'dcs_dt_routing_key')
        
        # 0 - ObsApp, 1 - DCS
        self.producer = [None, None]
                        
        self.simulation_mode = bool(int(simul))
        self.exptime_obs = 0.0
        self.exptime_svc = 0.0
        self.FS_number = 0
                
        # 0 - SVC, 1 - H, 2 - K
        self.acquiring = [False for _ in range(DC_CNT)]
        
        self.dcs_list = ["DCSS", "DCSH", "DCSK"]
                        
        self.connect_to_server_InstSeq_ex()
        self.connect_to_server_ObsApp_q()
        
        self.connect_to_server_dt_ex()
        self.connect_to_server_dcs_q()
                                     
        
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
                    
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        for i in range(2):
            self.producer[i].__del__()  

        self.log.send(self.iam, DEBUG, "Closed!") 
        #exit()
        
    
    #--------------------------------------------------------
    # ObsApp -> Inst. Sequencer
    def connect_to_server_InstSeq_ex(self):
        self.producer[OBS_APP] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ObsApp_ex)      
        self.producer[OBS_APP].connect_to_server()
        self.producer[OBS_APP].define_producer()
            
        
    
    #--------------------------------------------------------
    # Inst. Sequencer -> ObsApp
    def connect_to_server_ObsApp_q(self):
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_InstSeq_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.ObsApp_InstSeq_q, self.callback_ObsApp)       
        
        th = threading.Thread(target=consumer.start_consumer)
        th.start()
    
    
    def callback_ObsApp(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
    
        param = cmd.split()
        
        if param[0] == EXIT:
            self.__del__()          
        
   
    #--------------------------------------------------------
    # sub -> hk    
    def connect_to_server_dt_ex(self):
        # RabbitMQ connect  
        self.producer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_dcs_ex)      
        self.producer[DCS].connect_to_server()
        self.producer[DCS].define_producer()
        
                   
    #--------------------------------------------------------
    # hk -> sub
    def connect_to_server_dcs_q(self):
        # RabbitMQ connect
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dcs_InstSeq_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.dcs_InstSeq_q, self.callback_dcs)
        
        th = threading.Thread(target=consumer.start_consumer)
        th.start()
                        
                
            
    def callback_dcs(self, ch, method, properties, body):
        cmd = body.decode()        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)

        param = cmd.split()
        dc_idx = self.dcs_list.index(param[1])
        
        if param[0] == CMD_INITIALIZE2_ICS:
            pass
    
        elif param[0] == CMD_SETFSPARAM_ICS:    
            pass
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            self.acquiring[dc_idx] = False
            if dc_idx == SVC:
                msg = "%s %s" % (CMD_COMPLETED, self.dcs_list[SVC])
                self.producer[OBS_APP].send_message(self.InstSeq_ObsApp_q, msg)
                
            else:
                if not self.acquiring[H] and not self.acquiring[K]:
                    msg = "%s %s" % (CMD_COMPLETED, "all")
                    self.producer[OBS_APP].send_message(self.InstSeq_ObsApp_q, msg)
                
                
            

    #-------------------------------
    # dcs command
    def initialize2(self, dc_idx):
        target = self.dcs_list[dc_idx]
        if dc_idx == DC_CNT:
            target = "all"
        msg = "%s %s %d" % (CMD_INITIALIZE2_ICS, target, self.simulation_mode)
        self.producer[DCS].send_message(self.InstSeq_dcs_q, msg)
        
        
    def set_exp(self, dc_idx):      
        target = self.dcs_list[dc_idx]
        _exptime = 0
        if dc_idx == SVC:
            _exptime = self.exptime_svc
        else:
            _exptime = self.exptime_obs
                  
        _fowlerTime = _exptime - T_frame * self.FS_number
        msg = "%s %s %d %.3f 1 %d 1 %.3f 1" % (CMD_SETFSPARAM_ICS, self.dcs_list[dc_idx], self.simulation_mode, _exptime, self.FS_number, _fowlerTime)
        self.producer[DCS].send_message(self.InstSeq_dcs_q, msg)

        
    def start_acquisition(self, dc_idx):
        target = self.dcs_list[dc_idx]
        self.acquiring[dc_idx] = True
        if dc_idx == DC_CNT:
            target = "all"
            for i in range(DC_CNT):
                self.acquiring[i] = True
        
        msg = "%s %s %d" % (CMD_ACQUIRERAMP_ICS, target, self.simulation_mode)
        self.producer[DCS].send_message(self.InstSeq_dcs_q, msg)
        
        
    def save_fits_cube(self):
        pass




if __name__ == "__main__":
        
    #sys.argv.append('1')
    Inst_Seq(sys.argv[1])
    