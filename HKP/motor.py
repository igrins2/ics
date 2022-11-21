# -*- coding: utf-8 -*-
"""
Created on Nov 10, 2022

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


class motor() :
    
    def __init__(self, motor, port, gui=False):
        
        self.log = LOG(WORKING_DIR + "IGRINS", TARGET)
        
        self.port = port
        self.motor = motor
        
        self.iam = "%s(%d)" % (self.motor, int(self.port)-10000)
        self.log.logwrite(self.iam, INFO, "start") 
        
        # load ini file
        self.ini_file = WORKING_DIR + "/IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(self.ini_file)
        
        global TOUT, CMCWTIME, REBUFSIZE
        TOUT = int(self.cfg.get("HK", "tout"))
        CMCWTIME = float(self.cfg.get("HK", "cmcwtime"))
        REBUFSIZE = int(self.cfg.get("HK", "rebufsize")) 
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.hk_sub_ex = self.cfg.get(MAIN, 'hk_sub_exchange')     
        self.hk_sub_q = self.cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_hk_ex = self.cfg.get(MAIN, 'sub_hk_exchange')
        self.sub_hk_q = self.cfg.get(MAIN, 'sub_hk_routing_key')
        
        motor_pos = "%s-pos" % self.motor
        self.motor_pos = self.cfg.get("HK", motor_pos).split(",")
        
        ip_addr = "%s-ip" % self.motor
        self.ip = self.cfg.get("HK", ip_addr)
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
  
 
 
    # CLI
    def init_motor(self):
        
        self.send_to_motor("ZS")
        self.send_to_motor("ECHO_OFF")

        message = ""
        if self.motor == "UT":
            message = "%s Initializing (Upper Translator) ..." 
        elif self.motor == "LT":
            message = "%s Initializing (Lower Translator) ..." 
        
        self.log.logwrite(self.iam, INFO, message)
        
        # -------------------------------------------------
        # Go to left 
        self.send_to_motor("ADT=40")
        self.send_to_motor(VELOCITY_200)
        #self.send_to_motor("GOSUB1")
        
        cmd = ""
        
        if self.motor == "UT":
            cmd = "PRT=-%d" % RELATIVE_DELTA_L 
        elif self.motor == "LT":
            cmd = "PRT=%d" % RELATIVE_DELTA_L
        self.send_to_motor(cmd)
            
        sts = ["", ""]
        sts_ut = ["RIN(3)", "RBl"]
        sts_lt = ["RIN(2)", "RBr"]
        sts_bit = []
        if self.motor == "UT":
            sts_bit = sts_ut
        elif self.motor == "LT":
            sts_bit = sts_lt
                
        while True:
            self.motor_go()
            
            sts[0] = self.send_to_motor(sts_bit[0], True)
            sts[1] = self.send_to_motor(sts_bit[1], True)
        
            if (sts[0] == "1" and sts[1] == "1") or (sts[0] == "ok" and sts[1] == "ok"):
                break
                        
        # -------------------------------------------------
        # reset the bits
        while True:
            self.send_to_motor("ZS")
            if (self.send_to_motor(sts_bit[1], True) == "0") or (self.send_to_motor(sts_bit[1], True) == "ok"):
                break
                           
        # -------------------------------------------------
        # Go to near the bit 3(ut) or 2(lt)
        self.send_to_motor(VELOCITY_1)
        #self.send_to_motor("GOSUB2")
        
        if self.motor == "UT":
            cmd = "PRT=%d" % RELATIVE_DETLA_S 
        elif self.motor == "LT":
            cmd = "PRT=-%d" % RELATIVE_DETLA_S
        self.send_to_motor(cmd)
        
        while True:
            self.motor_go()
            sts[0] = self.send_to_motor(sts_bit[0], True)
            if sts[0] == "0" or sts[0] == "ok":
                break
            
        # -------------------------------------------------
        # Set 0 position
        while True:
            self.send_to_motor("O=0")
            if (self.send_to_motor("RPA", True) == "0") or (self.send_to_motor("RPA", True) == "ok"):
                break

    
    def send_to_motor(self, cmd, ret=False):
        #time.sleep(TSLEEP)
        cmd += "\r"
        self.comSocket.send(cmd.encode())
        self.log.logwrite(self.iam, INFO, "send_to_motor: " + cmd)
        ti.sleep(CMCWTIME)
        if ret:
            res = self.comSocket.recv(REBUFSIZE)
            res = res.decode()
            res = res[:-1]          
            self.log.logwrite(self.iam, INFO, "ReceivedFromMotor: " + res)
        else:
            res = ""
            
        return res
        
        
    def motor_go(self):
        message = ""
        if self.motor == "UT":
            message = "%s Moving (Upper Translator) ..."
        elif self.motor == "LT":
            message = "%s Moving (Lower Translator) ..."
        
        self.log.logwrite(self.iam, INFO, message)
            
        self.send_to_motor("G")
        return self.check_motor()
    
    
    def check_motor(self):
        message = ""
        if self.motor == "UT":
            message = "%s Checking (Upper Translator) ..."
        elif self.motor == "LT":
            message = "%s Checking (Lower Translator) ..."
        
        self.log.logwrite(self.iam, INFO, message)
        
        curpos = ""
        while True:
            curpos = self.send_to_motor("RPA", True)
            
            self.log.logwrite(self.iam, INFO, " CurPos: " + curpos)
            if self.send_to_motor("RBt", True) == "0":
                break
        self.log.logwrite(self.iam, INFO, "idle")   
        return curpos
                   

    # CLI
    def move_motor(self, posnum):
        # Set Velocity
        self.send_to_motor("ADT=40")
        self.send_to_motor(VELOCITY_200)
        #self.send_to_motor("GOSUB1")
        
        cmd = ""
        desti = int(self.motor_pos[posnum])
        if self.motor == "UT":
            cmd = "PT=%d" % desti
        elif self.motor == "LT":
            cmd = "PT=-%d" % desti
            
        self.send_to_motor(cmd)
        curpos = self.motor_go()
        self.motor_err_correction(desti, curpos)
              
                
    
    def motor_err_correction(self, desti, curpos):
        
        err = abs(desti) - abs(int(curpos))
        while abs(err) > MOTOR_ERR:
            message = ""
            if self.motor == "UT":
                message = "%s error correction (Upper Translate) ..."
            elif self.motor == "LT":
                message = "%s error correction (Lower Translate) ..."
            
            self.log.logwrite(self.iam, INFO, message)
            
            self.send_to_motor(VELOCITY_1)
            #self.send_to_motor("GOSUB2")
            curpos = self.motor_go()
            err = abs(desti) - abs(int(curpos))


    # CLI, main
    def move_motor_delta(self, go, delta):  
        # Set Velocity
        self.send_to_motor("ADT=40")
        self.send_to_motor(VELOCITY_1)
        #self.send_to_motor("GOSUB1")

        curpos = self.send_to_motor("RPA", True)
        self.log.logwrite(self.iam, INFO, "CurPos: " + curpos)
        
        cmd = ""
        
        if self.motor == "LT":
            if go is True:
                delta *= (-1)
        elif self.motor == "UT":
            if go is False:
                delta *= (-1)

        cmd = "PRT=%d" % delta  
        self.send_to_motor(cmd)
        curpos = self.motor_go()
        #self.motor_err_correction(movepos, curpos)
        


    # CLI
    def setUT(self, posnum):     
        res = self.send_to_motor("RPA", True)
        self.log.logwrite(self.iam, INFO, "CurPos: " + res)

        self.motor_pos[posnum] = res
        utpos = self.motor_pos[0] + "," + self.motor_pos[1]
        self.cfg.set("HK", "ut-pos", utpos )
        sc.SaveConfig(self.cfg, self.ini_file)
        self.log.logwrite(self.iam, INFO, "saved (" + utpos + ")")
        
                
    # CLI
    def setLT(self, posnum):       
        res = self.send_to_motor("RPA", True)
        self.log.logwrite(self.iam, INFO, "CurPos: " + res)

        self.motor_pos[posnum] = str(int(res)*(-1))
        ltpos = ""
        for i in range(4):
            ltpos += self.motor_pos[i]
            ltpos += ","
        self.cfg.set("HK", "lt-pos", ltpos)
        sc.SaveConfig(self.cfg, self.ini_file)
        self.log.logwrite(self.iam, INFO, "saved (" + ltpos + ")")
        
        
    def save_setpoint(self, setp):
        for i, v in enumerate(setp):
            key = "setp%d" % (i+1)
            self.cfg.set("HK", key, v)
        
        self.log.logwrite(self.iam, INFO, self.cfg)
        self.log.logwrite(self.iam, INFO, self.ini_file)
        sc.SaveConfig(self.cfg, self.ini_file)   #IGRINS.ini
        
        
    
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

        if param[0] == HK_REQ_INITMOTOR and param[1] == self.motor:
            self.init_motor()
            
        elif param[0] == HK_REQ_MOVEMOTOR and param[1] == self.motor:
            self.move_motor(int(param[2]))
            
        elif param[0] == HK_REQ_MOTORGO and param[1] == self.motor:
            self.move_motor_delta(int(param[2]), True)
            
        elif param[0] == HK_REQ_MOTORBACK and param[1] == self.motor:
            self.move_motor_delta(int(param[2]), False)
            
        elif param[0] == HK_REQ_SETUT and param[1] == self.motor:
            self.setUT(int(param[2]))
            
        elif param[0] == HK_REQ_SETLT and param[1] == self.motor:
            self.setLT(int(param[2]))
            
        elif param[0] == HK_REQ_EXIT:
            self.exit()

    
if __name__ == "__main__":

    if len(sys.argv) < 1:
        print("Please add ip and port")
        
     
    proc = motor(sys.argv[1], sys.argv[2], True)
    proc.connect_to_component()
               
    proc.connect_to_server_hk_ex()
    proc.connect_to_server_hk_q()
        
    '''
    proc = motor("LT", "10006")
    #proc = motor("UT", "10007")
    
    proc.connect_to_component()
    
    st = ti.time()
    
    proc.init_motor()
    print("--------------------------------")
    proc.move_motor(3)
    
    duration = ti.time() - st
    print(duration)
    
    #del proc
    '''