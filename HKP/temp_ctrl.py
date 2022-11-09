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
#import Libs.rabbitmq_server as serv
from Libs.logger import *


class temp_ctrl():
    
    def __init__(self, ip, port):
        
        self.log = LOG(WORKING_DIR + "IGRINS", IAM)
        
        #self.iam = iam
        #print(iam)
        
        self.logwrite(INFO, "start subsystem: temp ctrl!!!")
        
        # load ini file
        ini_file = WORKING_DIR + "/IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        global TOUT, REBUFSIZE
        TOUT = int(cfg.get("HK", "tout"))
        REBUFSIZE = int(cfg.get("HK", "rebufsize")) 
        
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')
        
        self.hk_sub_ex = cfg.get(MAIN, 'hk_sub_exchange')     
        self.hk_sub_q = cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_hk_ex = cfg.get(MAIN, 'sub_hk_exchange')
        self.sub_hk_q = cfg.get(MAIN, 'sub_hk_routing_key')
        
        self.ip = ip
        self.port = port
        self.comSocket = None
        self.send_msg = ""
        self.recv_msg = ""
        
        self.connect_to_component()
        
        recv_th = threading.Thread(target=self.socket_recv)
        recv_th.daemon = True
        recv_th.start()
        
        #self.connect_to_server_hk_ex()
        #self.connect_to_server_hk_q()
        
        
        
        
        
    def __del__(self):
        self.exit()
            
            
    def exit(self):
        print("Closing %s : " % IAM)
        
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
        
        msg = "[%s:%s] %s" % (IAM, level_name, message)
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
                    for i in range(30):
                        ti.sleep(1)
                        try:
                            res0 = self.comSocket.recv(REBUFSIZE)
                            info += res0.decode()

                            log = "recv %s <<< %s: %s (again)" % (self.port,  self.send_msg, info)
                            self.logwrite(INFO, log)

                            if info.find('\r\n') >= 0:
                                break
                        except:
                            continue

                self.recv_msg = info[:-2]
                
                msg = "%s %s" % (self.send_msg, self.recv_msg)    
                #self.send_message_to_hk(msg)
                        
                self.send_msg = ""
                
            except:
                self.comStatus = False
                #self.logwrite(ERROR, "receiving error") 
                #self.re_connect_to_component()   
                
                print("disconnected!")
                break                
        
    #-------------------------------
    # sub -> hk    
    def connect_to_server_hk_ex(self):
        # RabbitMQ connect        
        self.connection_hk_ex, self.channel_hk_ex = serv.connect_to_server(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_hk_ex:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_hk_ex, "direct", self.sub_hk_ex)
        
        
    def send_message_to_hk(self, message):
        serv.send_message(IAM, TARGET, self.channel_hk_ex, self.sub_hk_ex, self.sub_hk_q, message)
            
            
    #-------------------------------
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.connection_hk_q, self.channel_hk_q = serv.connect_to_server(IAM, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_hk_q:
            # RabbitMQ: define consumer
            self.queue_hk = serv.define_consumer(IAM, self.connection_hk_q, "direct", self.hk_sub_ex, self.hk_sub_q)

            th = threading.Thread(target=self.consumer_hk)
            th.start()
            
            
    # RabbitMQ communication    
    def consumer_hk(self):
        try:
            self.connection_hk_q.basic_consume(queue=self.queue_hk, on_message_callback=self.callback_hk, auto_ack=True)
            self.connection_hk_q.start_consuming()
        except Exception as e:
            if self.connection_hk_q:
                self.logwrite(ERROR, "The communication of server was disconnected!")
                
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == HK_REQ_GETSETPOINT:
            self.get_setpoint(int(param[1]))
        elif param[0] == HK_REQ_GETHEATINGPOWER:
            self.get_heating_power(int(param[1]))
        elif param[0] == HK_REQ_GETVALUE:
            self.get_value(param[1])      
        elif param[0] == HK_REQ_EXIT:
            self.exit()



if __name__ == "__main__":
    
    if len(sys.argv) < 1:
        print("Please add ip and port")

    print(sys.argv)

    proc = temp_ctrl("192.168.1.20", "10001")
    #proc = temp_ctrl(sys.argv[1], sys.argv[2])
    
    
    #st = ti.time()
    
    delay = 5
    #for i in range(1):
    while True:
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
    
    #duration = ti.time() - st
    #print(duration)
    
    #del proc
    
        
