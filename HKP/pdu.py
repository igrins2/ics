# -*- coding: utf-8 -*-
"""
Created on Nov 9, 2022

Created on Nov 10, 2022

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


class pdu() :
    
    def __init__(self, port, gui=False):
        
        self.log = LOG(WORKING_DIR + "IGRINS", TARGET)
        
        self.port = port
        
        self.iam = "PDU(%d)" % (int(self.port))
        self.log.logwrite(self.iam, INFO, "start") 
        
        # load ini file
        ini_file = WORKING_DIR + "/IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        global TOUT, TSLEEP, REBUFSIZE
        TOUT = int(cfg.get("HK", "tout"))
        TSLEEP = int(cfg.get('HK','tsleep'))
        REBUFSIZE = int(cfg.get("HK", "rebufsize")) 
        
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')
        
        self.hk_sub_ex = cfg.get(MAIN, 'hk_sub_exchange')     
        self.hk_sub_q = cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_hk_ex = cfg.get(MAIN, 'sub_hk_exchange')
        self.sub_hk_q = cfg.get(MAIN, 'sub_hk_routing_key')
        
        pdu_list = cfg.get("HK", "pdu-list").split(',')
        self.POWERSTR = pdu_list
        self.pow_flag = ["OFF" for _ in range(PDU_IDX)]
        
        self.ip = cfg.get("HK", "pdu-ip")
        self.comSocket = None
        self.send_msg = ""
        self.recv_msg = ""
        
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
        

    # CLI
    def initPDU(self):
        if not self.comStatus:
            return 
        
        try:
            cmd = "@@@@\r"
            self.comSocket.send(cmd.encode())
            log = "send >>> %s" % cmd
            self.log.logwrite(self.iam, INFO, log)
            
            res = self.comSocket.recv(REBUFSIZE)
            log = "recv <<< %s" % res.decode()
            self.log.logwrite(self.iam, INFO, log)
            
            cmd = "DN0\r"   #need to check!!!
            self.power_status(cmd) 
                
            self.log.logwrite(self.iam, INFO, "powctr init is completed")
                    
        except:
            self.log.logwrite(self.iam, ERROR, "powctr init is error")
                   
            self.comStatus = False
            self.re_connect_to_component()
        
                    
    def power_status(self, cmd):
        if not self.comStatus:
            return      
        
        try:
            self.comSocket.send(cmd.encode())
            log = "send >>> %s" % cmd
            self.log.logwrite(self.iam, INFO, log)
            ti.sleep(TSLEEP)
            res = self.comSocket.recv(REBUFSIZE)
            sRes = res.decode()
            log = "recv <<< %s" % sRes
            self.log.logwrite(self.iam, INFO, log)
            
            # check PDU status
            for i in range(PDU_IDX):
                if sRes.find("OUTLET %d ON" % (i + 1,)) >= 0:
                    self.pow_flag[i] = "ON"
                else:
                    self.pow_flag[i] = "OFF"
        except:
            self.log.logwrite(self.iam, ERROR, "powctr sending fail")
                   
            self.comStatus = False
            self.re_connect_to_component()
            

    # CLI, main - on/off�� �ٷ� �����ϸ� �ȵǳ�??? �Ʒ��ڵ� �׽�Ʈ �غ���, �ȵǸ� ����!
    def change_power(self, idx, onoff):  # definition OnOff: ON, OFF
        # this function is used when received PDU On/Off status and change status
        
        if not self.comStatus:
            return
        
        if onoff == OFF:
            self.pow_flag[idx-1] = "OFF"
            cmd = "F0%d\r" % (idx)
        elif onoff == ON:
            self.pow_flag[idx-1] = "ON"
            cmd = "N0%d\r" % (idx)
                   
        msg = " %s Button clicked"  % self.pow_flag[idx-1]
        self.log.logwrite(self.iam, INFO, self.POWERSTR[idx-1] + msg)
    
        self.power_status(cmd)
            
    
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

        if param[0] == HK_REQ_PWR_ONOFF:
            self.change_power(int(param[1]), param[2]) 
            
        elif param[0] == HK_REQ_EXIT:
            self.exit()
            
            
if __name__ == "__main__":
    
    if len(sys.argv) < 1:
        print("Please add ip and port")

    #print(sys.argv)

    #
    proc = pdu(sys.argv[1], True)
    proc.connect_to_component()
    proc.initPDU()
        
    proc.connect_to_server_hk_ex()
    proc.connect_to_server_hk_q()
    
    '''
    proc = pdu("50023")
    proc.connect_to_component()
    proc.initPDU()
    
    st = ti.time()
    
    for i in range(1, 9):
        proc.change_power(i, ON)
    
    duration = ti.time() - st
    print(duration)
    
    #del proc
    '''
    
    
    
    

    

 