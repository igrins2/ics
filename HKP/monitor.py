# -*- coding: utf-8 -*-
"""
Created on Nov 9, 2022

Created on Nov 29, 2022

@author: hilee
"""

import os, sys
from socket import *
import threading
import time as ti

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.HK_def import *
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

class monitor() :
    
    def __init__(self, comport, gui=False):  
        
        self.iam = ""
        self.comport = comport
        if self.comport == "10004":
            self.iam = "tm"
        elif self.comport == "10005":
            self.iam = "vm"
            
        self.log = LOG(WORKING_DIR + "/IGRINS", "EngTools")
        self.log.send(self.iam, "INFO", "start")  
        
        # load ini file
        ini_file = WORKING_DIR + "/IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        global TOUT, REBUFSIZE
        TOUT = int(cfg.get(HK, "tout"))
        REBUFSIZE = int(cfg.get(HK, "rebufsize")) 
        
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')
        
        self.hk_sub_ex = cfg.get(MAIN, 'hk_sub_exchange')     
        self.hk_sub_q = cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_hk_ex = cfg.get(MAIN, 'sub_hk_exchange')
        self.sub_hk_q = cfg.get(MAIN, 'sub_hk_routing_key')
                
        self.ip = cfg.get(HK, "device-server-ip")
        
        self.gui = gui
        
        self.comSocket = None
        
        self.producer = None
        self.consumer = None
        
        self.th = threading.Timer(1, self.re_connect_to_component)
        self.th.daemon = True
        
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, "DEBUG", msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, "DEBUG", th.name + " exit.")
            
        self.close_component()
        
        if self.gui:
            #self.consumer.stop_consumer()
            
            self.producer.__del__()                    
            self.consumer.__del__()
                    
        

    def connect_to_component(self):
            
        try:            
            self.comSocket = socket(AF_INET, SOCK_STREAM)
            self.comSocket.settimeout(TOUT)
            self.comSocket.connect((self.ip, int(self.comport)))
            self.comStatus = True
            
            msg = "connected"
            self.log.send(self.iam, "INFO", msg)
            
        except:
            self.comSocket = None
            self.comStatus = False
            
            msg = "disconnected"
            self.log.send(self.iam, "ERROR", msg)
            
            self.th.start()
            
        msg = "%s %s %d" % (HK_REQ_COM_STS, self.iam, self.comStatus)   
        if self.gui:
            self.producer.send_message(HK, self.sub_hk_q, msg)        
                 
    
    def re_connect_to_component(self):
        self.th.cancel()
        
        msg = "trying to connect again"
        self.log.send(self.iam, "WARNING", msg)
            
        if self.comSocket != None:
            self.close_component()
        self.connect_to_component()        

           
    def close_component(self):
        self.comSocket.close()
        self.comStatus = False
        

    # TM-Monitorig
    def get_value_fromTM(self, port=0):
        cmd = "KRDG? %s" % port
        cmd += "\r\n"
        self.socket_send(HK_REQ_GETVALUE, cmd, port)
        
        
    # VM-Monitorig
    def get_value_fromVM(self):
        #PR1 - MicroPirani, PR2/PR5 - Cold Cathode, PR3 - both (3 digits), PR4 - both (4 digits)
        cmd = "@253PR3?;FF"
        cmd += "\r\n"
        self.socket_send(HK_REQ_GETVALUE, cmd)
            
    
    def socket_send(self, param, cmd, port=0):
        if self.gui:
            send_th = threading.Thread(target=self.handle_com, args=(param, cmd, port))
            send_th.daemon = True
            send_th.start()
        else:
            self.handle_com(param, cmd, port)
        
        
    # Socket function        
    def handle_com(self, param, cmd, port):
        try:         
            
            #send
            self.comSocket.send(cmd.encode())
            #self.comSocket.sendall(cmd.encode())

            log = "send >>> %s" % cmd[:-2]
            self.log.send(self.iam, "INFO", log)
            
            #rev
            res0 = self.comSocket.recv(REBUFSIZE)
            info = res0.decode()
                    
            log = "recv <<< %s" % info[:-2]
            self.log.send(self.iam, "INFO", log)   
                                            
            if self.iam == "tm":
                if info.find('\r\n') < 0:
                    for i in range(30*10):
                        ti.sleep(0.1)
                        try:
                            res0 = self.comSocket.recv(REBUFSIZE)
                            info += res0.decode()

                            log = "recv <<< %s (again)" % info[:-2]
                            self.log.send(self.iam, "INFO", log)

                            if info.find('\r\n') >= 0:
                                break
                        except:
                            continue
            
                msg = "%s %s %s %s" % (param, self.iam, port, info[:-2])
                
            else:
                msg = "%s %s 0 %s" % (param, self.iam, info[7:-3])
               
            if self.gui: 
                self.producer.send_message(HK, self.sub_hk_q, msg)     
        except:
            self.comStatus = False
            self.log.send(self.iam, "ERROR", "communication error") 
            self.re_connect_to_component()

    
    #-------------------------------
    # sub -> hk    
    def connect_to_server_sub_ex(self):
        # RabbitMQ connect        
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.sub_hk_ex, "direct")      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
        
        
    #-------------------------------
    # hk -> sub
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex, "direct")      
        self.consumer.connect_to_server()
        self.consumer.define_consumer(self.hk_sub_q, self.callback_hk)
        
        th = threading.Thread(target=self.consumer.start_consumer)
        th.start()
        
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        if len(param) < 2:
            return
        if param[1] != self.iam:
            return
        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, "INFO", msg)
        
        if param[0] == HK_REQ_GETVALUE and param[1] == "tm":
            self.get_value_fromTM(param[2])      
        
        elif param[0] == HK_REQ_GETVALUE and param[1] == "vm":
            self.get_value_fromVM()    
            
        elif param[0] == HK_REQ_MANUAL_CMD and param[1] == self.iam:
            cmd = "%s %s\r\n" % (param[2], param[3])
            self.socket_send(HK_REQ_MANUAL_CMD, cmd, param[3])
            
        #elif param[0] == HK_REQ_EXIT:
        #    self.__del__()
            
            
 
            
if __name__ == "__main__":
    
    #sys.argv.append("10004")
    if len(sys.argv) < 2:
        print("Please add comport")
        exit()
    
    proc = monitor(sys.argv[1], True)
        
    proc.connect_to_server_sub_ex()
    proc.connect_to_server_hk_q()
    
    proc.connect_to_component()
    
    #proc.get_value_fromVM()
    '''
    delay = 0.1
    for i in range(1):
        proc.get_value_fromTM(0)
        ti.sleep(delay)
    
    del proc
    '''