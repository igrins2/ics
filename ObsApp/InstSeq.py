# -*- coding: utf-8 -*-
"""
Created on Feb 15, 2023

Modified on 

@author: hilee
"""

import os, sys
import threading

import subprocess
#import time as ti

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
        self.consumer = [None, None]
                
        self.proc_sub = [None for _ in range(COM_CNT)]
        
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
        
        self.proc_simul = None
        if bool(int(simul)):
            cmd = "%sworkspace/ics/igos2_simul/run_hk_simulator.py" % WORKING_DIR
            self.proc_simul = subprocess.Popen(["python", cmd])
            
            ti.sleep(3)
            
        self.start_sub_system(simul) 
        
        self.producer[OBS_APP].send_message(self.InstSeq_ObsApp_q, READY) 
         
        
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for i in range(COM_CNT):
            if self.proc_sub[i] != None:
                self.proc_sub[i].terminate()
                self.log.send(self.iam, INFO, str(self.proc_sub[i].pid) + " exit")                

        if self.proc_simul != None:
            self.proc_simul.terminate()
            self.log.send(self.iam, INFO, str(self.proc_simul.pid) + " exit")        
                
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        for i in range(2):
            self.producer[i].__del__()  

        self.log.send(self.iam, DEBUG, "Closed!") 
        
    
    def start_sub_system(self, simul):
                
        comport = []
        com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "uploader"]
        for name in com_list:
            if name != com_list[UPLOADER]:
                comport.append(self.cfg.get(HK, name + "-port"))
    
        for i in range(COM_CNT-1):
            if self.proc_sub[i] != None:
                continue
                
            if i <= TMC3:
                cmd = "%sworkspace/ics/HKP/temp_ctrl.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i], simul])
            elif i == TM or i == VM:
                cmd = "%sworkspace/ics/HKP/monitor.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i], simul])
            elif i == PDU:
                cmd = "%sworkspace/ics/HKP/pdu.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, simul])              
                        
        if self.proc_sub[UPLOADER] == None:
            cmd = "%sworkspace/ics/HKP/uploader.py" % WORKING_DIR
            self.proc_sub[UPLOADER] = subprocess.Popen(['python', cmd, simul]) 
                
            
            
    #--------------------------------------------------------
    # ObsApp -> Inst. Sequencer
    def connect_to_server_InstSeq_ex(self):
        self.producer[OBS_APP] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ObsApp_ex)      
        self.producer[OBS_APP].connect_to_server()
        self.producer[OBS_APP].define_producer()
            
        
    
    #--------------------------------------------------------
    # Inst. Sequencer -> ObsApp
    def connect_to_server_ObsApp_q(self):
        self.consumer[OBS_APP] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_InstSeq_ex)      
        self.consumer[OBS_APP].connect_to_server()
        self.consumer[OBS_APP].define_consumer(self.ObsApp_InstSeq_q, self.callback_ObsApp)       
        
        th = threading.Thread(target=self.consumer[OBS_APP].start_consumer)
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
        self.consumer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dcs_InstSeq_ex)      
        self.consumer[DCS].connect_to_server()
        self.consumer[DCS].define_consumer(self.dcs_InstSeq_q, self.callback_dcs)
        
        th = threading.Thread(target=self.consumer[DCS].start_consumer)
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
                if self.acquiring[H] == False and self.acquiring[K] == False:
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
        
    Inst_Seq(sys.argv[1])
    