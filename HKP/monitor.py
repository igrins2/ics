# -*- coding: utf-8 -*-
"""
Created on Nov 9, 2022

Created on Nov 9, 2022

@author: hilee
"""

import os, sys
from socket import *
import threading
import time as ti

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.HK_def import *
import Libs.SetConfig as sc
import Libs.rabbitmq_server as serv
from Libs.logger import *




class monitor() :
    
    def __init__(self, monit, port, gui=False):
        
        self.log = LOG(WORKING_DIR + "IGRINS", TARGET)
        
        self.port = port
        self.monit = monit
        
        self.iam = ""
        if self.monit == "temp":
            self.iam = "temp.monitor(%d)" % (int(self.port)-10000)
        elif self.monit == "vm":
            self.iam = "v.monitor(%d)" % (int(self.port)-10000)
        self.log.logwrite(self.iam, INFO, "start")
        
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
        
        self.ip = cfg.get("HK", "device-server-ip")
        self.comSocket = None
        
        self.gui = gui
        
        
    
    def __del__(self):
        print("Closing %s" % self.iam)
        
        for th in threading.enumerate():
            print(th.name + " exit.")
            
        self.close_component()
                    
        

    def connect_to_component(self):
            
        try:            
            self.comSocket = socket(AF_INET, SOCK_STREAM)
            self.comSocket.settimeout(TOUT)
            self.comSocket.connect((self.ip, int(self.port)))
            self.comStatus = True
            
            msg = "connected"
            self.log.logwrite(self.iam, INFO, msg)
            
        except:
            self.comSocket = None
            self.comStatus = False
            
            msg = "disconnected"
            self.log.logwrite(self.iam, ERROR, msg)
            
            self.re_connect_to_component()         
                 
    
    def re_connect_to_component(self):
        msg = "trying to connect again"
        self.log.logwrite(self.iam, WARNING, msg)
            
        if self.comSocket != None:
            self.close_component()
        self.connect_to_component()        

           
    def close_component(self):
        self.comSocket.close()
        self.comStatus = False
        

    # CLI, TM-Monitorig
    def get_value(self, port=0):
        
        cmd = ""
        if self.monit == "temp":
            cmd = "KRDG? %d" % port
            
        elif self.monit == "vm":
            #PR1 - MicroPirani, PR2/PR5 - Cold Cathode, PR3 - both (3 digits), PR4 - both (4 digits)
            cmd = "@253PR3?;FF"

        cmd += "\r\n"
        self.socket_send(cmd)
            
    
    
    def socket_send(self, cmd):
        send_th = threading.Thread(target=self.handle_com, args=(cmd,))
        send_th.daemon = True
        send_th.start()
        
        
    # Socket function        
    def handle_com(self, cmd):
        try:         
            
            #send
            self.comSocket.send(cmd.encode())
            #self.comSocket.sendall(cmd.encode())

            log = "send >>> %s" % cmd
            self.log.logwrite(self.iam, INFO, log)
            
            #rev
            res0 = self.comSocket.recv(REBUFSIZE)
            info = res0.decode()
                    
            log = "recv <<< %s" % info[:-2]
            self.log.logwrite(self.iam, INFO, log)   
                            
            if self.monit =="vm":
                self.recv_msg = info[7:-3]
                
            else:
                if info.find('\r\n') < 0:
                    for i in range(30*10):
                        ti.sleep(0.1)
                        try:
                            res0 = self.comSocket.recv(REBUFSIZE)
                            info += res0.decode()

                            log = "recv <<< %s (again)" % info[:-2]
                            self.log.logwrite(self.iam, INFO, log)

                            if info.find('\r\n') >= 0:
                                break
                        except:
                            continue
            
            msg = "%s" % info[:-2]   
            if self.gui: 
                self.send_message_to_hk(msg)
                    
        except:
            self.comStatus = False
            self.log.logwrite(self.iam, ERROR, "sending error") 
            self.re_connect_to_component()

    
    #-------------------------------
    # sub -> hk    
    def connect_to_server_hk_ex(self):
        # RabbitMQ connect        
        self.connection_hk_ex, self.channel_hk_ex = serv.connect_to_server(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_hk_ex:
            # RabbitMQ: define producer
            serv.define_producer(self.iam, self.channel_hk_ex, "direct", self.sub_hk_ex)
        
        
    def send_message_to_hk(self, message):
        serv.send_message(self.iam, TARGET, self.channel_hk_ex, self.sub_hk_ex, self.sub_hk_q, message)    

    
    #-------------------------------
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.connection_hk_q, self.channel_hk_q = serv.connect_to_server(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_hk_q:
            # RabbitMQ: define consumer
            self.queue_hk = serv.define_consumer(self.iam, self.connection_hk_q, "direct", self.hk_sub_ex, self.hk_sub_q)

            th = threading.Thread(target=self.consumer_hk)
            th.start()
            
            
    # RabbitMQ communication    
    def consumer_hk(self):
        try:
            self.connection_hk_q.basic_consume(queue=self.queue_hk, on_message_callback=self.callback_hk, auto_ack=True)
            self.connection_hk_q.start_consuming()
        except Exception as e:
            if self.connection_hk_q:
                self.log.logwrite(self.iam, ERROR, "The communication of server was disconnected!")
                
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.logwrite(self.iam, INFO, msg)

        param = cmd.split()

        if param[0] == HK_REQ_GETVALUE and param[1] == self.monit:
            self.get_value(int(param[2])) 
                
        elif param[0] == HK_REQ_EXIT:
            self.exit()
            
            
if __name__ == "__main__":
    
    if len(sys.argv) < 1:
        print("Please add ip and port")
    
    
    proc = monitor(sys.argv[1], sys.argv[2], True)
    proc.connect_to_component()
        
    proc.connect_to_server_hk_ex()
    proc.connect_to_server_hk_q()
    
    '''
    
    proc = monitor("temp", "10004")
    #proc = monitor("vm", "10005")
    
    proc.connect_to_component()
    
    st = ti.time()
    
    delay = 0.1
    for i in range(1):
    #while True:
        proc.get_value(0)
        ti.sleep(delay)
    
    duration = ti.time() - st
    print(duration)
    
    del proc
    '''