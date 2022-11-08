# -*- coding: utf-8 -*-
"""
Created on Sep 17, 2021

Modified on Nov 8, 2022

@author: hilee
"""

import os, sys
#import asyncio
from socket import *
import threading
import time as ti

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from hk_def import *
import Libs.SetConfig as sc
import Libs.rabbitmq_server as serv
from Libs.logger import *


class temp_ctrl():
    
    def __init__(self, iam, ip, port):
        
        self.log = LOG(WORKING_DIR + "IGRINS")
        
        self.iam = iam
        print(iam)
        
        self.logwrite(INFO, "start subsystem: temp ctrl!!!")
        
        # load ini file
        self.ini_file = WORKING_DIR + "/IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(self.ini_file)
        
        global TOUT, REBUFSIZE
        TOUT = int(self.cfg.get("HK", "tout"))
        REBUFSIZE = int(self.cfg.get("HK", "rebufsize")) 
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.ip = ip
        self.port = port
        self.comSocket = None
        self.send_msg = ""
        self.recv_msg = ""
        
        self.connect_to_component()
        
        recv_th = threading.Thread(target=self.socket_recv)
        recv_th.daemon = True
        recv_th.start()
        
        
    def __del__(self):
        self.exit()
            
            
    def exit(self):
        print("Closing %s : " % sys.argv[0])
        
        for th in threading.enumerate():
            print(th.name + " exit.")
               
        
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
        
        
    def connect_to_component(self):
            
        try:            
            self.comSocket = socket(AF_INET, SOCK_STREAM)
            self.comSocket.settimeout(TOUT)
            self.comSocket.connect((self.ip, int(self.port)))
            self.comStatus = True
            
            msg = "%s:%s is connected" % (self.ip, self.port)
            self.logwrite(INFO, msg)
            
        except:
            self.comSocket = None
            self.comStatus = False
            
            msg = "%s:%s is not connected" % (self.ip, self.port)
            self.logwrite(ERROR, msg)
            
            self.re_connect_to_component()
              
    
    def re_connect_to_component(self):
        msg = "%s:%s is trying to connect again" % (self.ip, self.port)
        self.logwrite(WARNING, msg)
            
        if self.comSocket != None:
            self.close_component()
        self.connect_to_component()

           
    def close_component(self):
        self.comSocket.close()
        self.comStatus = False
        
        
    # CLI, TMC-Get SetPoint
    def get_setpoint(self, nPort):
        self.send_msg = "SETP? %d" % nPort
        cmd = self.send_msg + "\r\n"
        self.socket_send(cmd)


    # CLI, TMC-Heating Value
    def get_heating_power(self, nPort):
        self.send_msg = "HTR? %d" % nPort
        cmd = self.send_msg + "\r\n"
        self.socket_send(cmd)
    
    
    # CLI, TMC-Heating(Manual) Get Value
    def get_heating_power_manual(self, nPort):
        self.send_msg = "MOUT? %d" % nPort
        cmd = self.send_msg + "\r\n"
        self.socket_send(cmd) 
    
    
    # CLI, TMC-Heating(Manual) Set Value
    def SetHeatingValue_manual(self, nPort, value):
        self.send_msg = "MOUT %d,%f" % (nPort, value)
        cmd = self.send_msg + "\r\n"
        self.socket_send(cmd)
    

    # CLI, TMC-Monitorig
    def get_value(self, sPort):  
        self.send_msg = "KRDG? " + sPort
        cmd = self.send_msg + "\r\n"
        self.socket_send(cmd)


    def socket_send(self, cmd):
        send_th = threading.Thread(target=self.handle_send, args=(cmd,))
        send_th.daemon = True
        send_th.start()
        

    # Socket function        
    def handle_send(self, cmd):
        try:         
            self.comSocket.send(cmd.encode())
            #self.comSocket.sendall(cmd.encode())

            log = "send: %s >>> %s" % (self.port, cmd)
            self.logwrite(INFO, log)
        
            if cmd.find("MOUT ") == 0:
                d1, d2 = cmd.split(',')
                print("set:",str(float(d2)))
                log = "set:",str(float(d2))
                self.logwrite(INFO, log)
                    
        except:
            self.comStatus = False
            self.logwrite(ERROR, "sending error") 
            self.re_connect_to_component()
            

    # Socket function
    def socket_recv(self):
        
        #count = 0
        print("receving start!")
        while True:
            
            if self.send_msg == "":
                continue
            
            try:                     
                res0 = self.comSocket.recv(REBUFSIZE)
                info = res0.decode()
                        
                log = "recv %s <<< %s: %s" % (self.port,  self.send_msg, info)
                self.logwrite(INFO, log)   
                
                #count += 1
                #print(count)
                
                if info.find('\r\n') < 0:
                    self.recv_msg = info
                else:
                    self.recv_msg = info[:-2]
                        
                self.send_msg = ""
                
            except:
                self.comStatus = False
                #self.logwrite(ERROR, "receiving error") 
                #self.re_connect_to_component()   
                
                print("disconnected!")
                break         
            
            
            
    def save_setpoint(self, setp):
        for i, v in enumerate(setp):
            key = "setp%d" % (i+1)
            self.cfg.set("HK", key, v)
        
        self.logwrite(INFO, self.cfg)
        self.logwrite(INFO, self.ini_file)
        sc.SaveConfig(self.cfg, self.ini_file)   #IGRINS.ini
        
        
        
    def connect_to_server_ics_ex(self):
        # RabbitMQ connect        
        self.connection_ics_ex, self.channel_ics_ex = serv.connect_to_server(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_ics_ex:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_ics_ex, "direct", self.ics_ex)
        
        
    def send_message_to_ics(self, simul_mode, message):
            param = "%d %s" % (simul_mode, message)
            serv.send_message(IAM, TARGET, self.channel_ics_ex, self.ics_ex, self.ics_q, message)




if __name__ == "__main__":
    
    if len(sys.argv) < 1:
        print("Please add ip and port")

    #proc = temp_ctrl("temp_ctrl.py", "127.0.0.1", "10001")
    proc = temp_ctrl(sys.argv[0], sys.argv[1], sys.argv[2])
    
    '''
    #st = ti.time()
    
    for i in range(1):
        proc.get_setpoint(1)
        ti.sleep(1)
        proc.get_setpoint(2)
        ti.sleep(1)
        
        proc.get_heating_power(1)
        ti.sleep(1)
        proc.get_heating_power(2)
        ti.sleep(1)
        
        proc.get_value("A")
        ti.sleep(1)
        proc.get_value("B")
        ti.sleep(1)
    
    #duration = ti.time() - st
    #print(duration)
    
    del proc
    '''
        
