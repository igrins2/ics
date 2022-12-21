# -*- coding: utf-8 -*-
"""
Created on Nov 8, 2022

Modified on Dec 14, 2022

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

class temp_ctrl():
    
    def __init__(self, comport, gui=False):
                       
        self.comport = comport
        self.iam = "tmc%d" % (int(self.comport)-10000)               
    
        self.log = LOG(WORKING_DIR + "/IGRINS", "EngTools", gui)
        self.log.send(self.iam, INFO, "start")    
     
        # load ini file
        ini_file = WORKING_DIR + "/IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        global TOUT, REBUFSIZE
        TOUT = int(cfg.get(HK, "tout"))
        REBUFSIZE = int(cfg.get(HK, "rebufsize")) 
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_sub_ex = cfg.get(MAIN, "hk_sub_exchange")     
        self.hk_sub_q = cfg.get(MAIN, "hk_sub_routing_key")
        self.sub_hk_ex = cfg.get(MAIN, "sub_hk_exchange")
        self.sub_hk_q = cfg.get(MAIN, "sub_hk_routing_key")
                
        self.ip = cfg.get(HK, "device-server-ip")
 
        self.gui = gui
        
        self.comSocket = None
        self.comStatus = False
        
        self.producer = None
        self.consumer = None
        
        #self.th = threading.Timer(1, self.re_connect_to_component)
        #self.th.daemon = True
        
        
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, DEBUG, th.name + " exit.")
            
        self.close_component()
        
        if self.gui:
            #self.consumer.stop_consumer()
            
            self.producer.__del__()                    
            self.consumer.__del__()
        
        
    def connect_to_component(self):
            
        try:     
            msg = "try to connect TMC1..."
            self.log.send(self.iam, DEBUG, msg)      

            self.comSocket = socket(AF_INET, SOCK_STREAM)
            self.comSocket.settimeout(TOUT)
            self.comSocket.connect((self.ip, int(self.comport)))
            #ti.sleep(3)
            self.comStatus = True
            
            msg = "connected"
            self.log.send(self.iam, INFO, msg)
            
        except:
            self.comSocket = None
            self.comStatus = False
            
            msg = "disconnected"
            self.log.send(self.iam, ERROR, msg)
            
            #self.th.start()
            th = threading.Timer(3, self.re_connect_to_component)
            th.start()
            
        msg = "%s %s %d" % (HK_REQ_COM_STS, self.iam, self.comStatus)   
        if self.gui:
            self.producer.send_message(HK, self.sub_hk_q, msg) 
              
    
    def re_connect_to_component(self):
        #self.th.cancel()
        
        msg = "trying to connect again"
        self.log.send(self.iam, WARNING, msg)
            
        if self.comSocket != None:
            self.close_component()
        self.connect_to_component()

           
    def close_component(self):
        self.comSocket.close()
        self.comStatus = False
        
        
    # TMC-Get SetPoint
    def get_setpoint(self, port):
        cmd = "SETP? %d" % port
        cmd += "\r\n"
        self.socket_send(HK_REQ_GETSETPOINT, str(port), cmd)
            

    # TMC-Heating Value
    def get_heating_power(self, port):
        cmd = "HTR? %d" % port
        cmd += "\r\n"
        self.socket_send(HK_REQ_GETHEATINGPOWER, str(port), cmd)
    
    
    # TMC-Monitorig
    def get_value(self, port):  
        cmd = "KRDG? " + port
        cmd += "\r\n"
        self.socket_send(HK_REQ_GETVALUE, port, cmd)


    def socket_send(self, param, port, cmd):
        if self.gui:
            send_th = threading.Thread(target=self.handle_com, args=(param, port, cmd))
            send_th.daemon = True
            send_th.start()
        else:
            self.handle_com(param, port, cmd)
        

    # Socket function        
    def handle_com(self, param, port, cmd):
        try:    
            #send     
            self.comSocket.send(cmd.encode())
            #self.comSocket.sendall(cmd.encode())
            
            log = "send >>> %s" % cmd[:-2]
            self.log.send(self.iam, INFO, log)
                    
            #rev
            res0 = self.comSocket.recv(REBUFSIZE)
            info = res0.decode()
                    
            log = "recv <<< %s" % info[:-2]
            self.log.send(self.iam, INFO, log)   
            
            if info.find('\r\n') < 0:
                '''
                for i in range(30*10):
                    ti.sleep(0.1)
                    try:
                        res0 = self.comSocket.recv(REBUFSIZE)
                        info += res0.decode()

                        log = "recv <<< %s (again)" % info[:-2]
                        self.log.send(self.iam, INFO, log)

                        if info.find('\r\n') >= 0:
                            break
                    except:
                        continue
                '''

                th = threading.Timer(1, self.handle_com, args=(param, port, cmd))
                th.start()

                return
            
            msg = "%s %s %s %s" % (param, self.iam, port, info[:-2]) 
            if self.gui: 
                self.producer.send_message(HK, self.sub_hk_q, msg)
            
        except:
            self.comStatus = False
            self.log.send(self.iam, ERROR, "communication error") 
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
        
        #th = threading.Thread(target=self.consumer.define_consumer, args=(self.hk_sub_q, self.callback_hk))
        #th.start()
        
            
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if len(param) < 3:
            return
        if param[1] != self.iam:
            return
        if self.comStatus is False:
            return
        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
                
        if param[0] == HK_REQ_GETSETPOINT:
            self.get_setpoint(int(param[2]))
            #self.get_setpoint(1)
            #self.get_setpoint(2)
            
        elif param[0] == HK_REQ_GETHEATINGPOWER:
            self.get_heating_power(int(param[2]))
            #self.get_heating_power(1)
            #self.get_heating_power(2)
            
        elif param[0] == HK_REQ_GETVALUE:
            self.get_value(param[2])  
            #self.get_value("A")  
            #self.get_value("B")     
        
        elif param[0] == HK_REQ_MANUAL_CMD:
            cmd = "%s %s\r\n" % (param[2], param[3])
            self.socket_send(HK_REQ_MANUAL_CMD, param[3], cmd)
            
        #elif param[0] == HK_REQ_EXIT:
        #    self.__del__()



if __name__ == "__main__":
    
    #sys.argv.append("10001")
    if len(sys.argv) < 2:
        print("Please add comport")
        exit()
    
    proc = temp_ctrl(sys.argv[1], True)
    #proc = temp_ctrl(sys.argv[1])
    
    proc.connect_to_server_sub_ex()
    proc.connect_to_server_hk_q()
    
    proc.connect_to_component()

    '''
    delay = 0
    for i in range(1):
        proc.get_setpoint(1)
        ti.sleep(delay)
        proc.get_setpoint(2)
        ti.sleep(delay)
        proc.get_heating_power(1)
        ti.sleep(delay)
        proc.get_heating_power(2)
        ti.sleep(delay)
        
        proc.get_value("A")
        ti.sleep(delay)
        proc.get_value("B")
        ti.sleep(delay)
        
    proc.__del__()
    '''
    
        
