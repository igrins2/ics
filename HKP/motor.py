# -*- coding: utf-8 -*-
"""
Created on Nov 10, 2022

Created on Dec 14, 2022

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

class motor(threading.Thread) :
    
    def __init__(self, motor, port, simul='0', gui=False):
        
        self.iam = motor  
        self.port = port 
        #self.iam = "%s(%d)" % (self.motor, int(self.port)-10000)
        
        self.log = LOG(WORKING_DIR + "IGRINS", "EngTools", gui)    
        self.log.send(self.iam, INFO, "start")
        
        # load ini file
        self.ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(self.ini_file)
        
        global TOUT, CMCWTIME, REBUFSIZE
        TOUT = int(self.cfg.get(HK, "tout"))
        CMCWTIME = float(self.cfg.get(HK, "cmcwtime"))
        REBUFSIZE = int(self.cfg.get(HK, "rebufsize")) 
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.hk_sub_ex = self.cfg.get(MAIN, 'hk_sub_exchange')     
        self.hk_sub_q = self.cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_hk_ex = self.cfg.get(MAIN, 'sub_hk_exchange')
        self.sub_hk_q = self.cfg.get(MAIN, 'sub_hk_routing_key')
                
        motor_pos = "%s-pos" % self.iam
        self.motor_pos = self.cfg.get(HK, motor_pos).split(",")
        
        ip_addr = "%s-ip" % self.iam
        
        if bool(int(simul)):
            self.ip = "localhost"
        else:
            self.ip = self.cfg.get(HK, ip_addr)
        self.gui = gui
        
        self.comSocket = None
        self.comStatus = False
        
        self.producer = None
        self.consumer = None
                
        self.init = False
        
        self.curpos = 0
        
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, DEBUG, th.name + " exit.")
            
        self.close_component()
                    
        if self.gui:
            self.producer.__del__()                    
            
        
    def connect_to_component(self):
            
        try:            
            self.comSocket = socket(AF_INET, SOCK_STREAM)
            self.comSocket.settimeout(TOUT)
            self.comSocket.connect((self.ip, int(self.port)))
            self.comStatus = True
            
            msg = "connected"
            self.log.send(self.iam, INFO, msg)
            
        except:
            self.comSocket = None
            self.comStatus = False
            
            msg = "disconnected"
            self.log.send(self.iam, ERROR, msg)
            
            threading.Timer(1, self.re_connect_to_component).start()
                        
        msg = "%s %s %d" % (HK_REQ_COM_STS, self.iam, self.comStatus)   
        if self.gui:
            self.producer.send_message(DT, self.sub_hk_q, msg)
                             
    
    def re_connect_to_component(self):
        
        msg = "trying to connect again"
        self.log.send(self.iam, WARNING, msg)
            
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
        if self.iam == MOTOR_UT:
            message = "%s Initializing (Upper Translator) ..." % self.iam
        elif self.iam == MOTOR_LT:
            message = "%s Initializing (Lower Translator) ..." % self.iam
        
        self.log.send(self.iam, INFO, message)
        # -------------------------------------------------
        # Go to left 
        self.send_to_motor("ADT=40")
        self.send_to_motor(VELOCITY_200)
        #self.send_to_motor("GOSUB1")
        
        cmd = ""
        if self.iam == MOTOR_UT:
            cmd = "PRT=-%d" % RELATIVE_DELTA_L 
        elif self.iam == MOTOR_LT:
            cmd = "PRT=%d" % RELATIVE_DELTA_L
        self.send_to_motor(cmd)
            
        sts_ut = ["RIN(3)", "RBl"]
        sts_lt = ["RIN(2)", "RBr"]
        sts_bit = []
        if self.iam == MOTOR_UT:
            sts_bit = sts_ut
        elif self.iam == MOTOR_LT:
            sts_bit = sts_lt
                
        while True:
            self.motor_go()

            if self.send_to_motor(sts_bit[0], True) == "1" and self.send_to_motor(sts_bit[1], True) == "1":
                break
                        
        # -------------------------------------------------
        # reset the bits
        while True:
            self.send_to_motor("ZS")
            if self.send_to_motor(sts_bit[1], True) == "0":
                break
                           
        # -------------------------------------------------
        # Go to near the bit 3(ut) or 2(lt)
        self.send_to_motor(VELOCITY_1)
        #self.send_to_motor("GOSUB2")
        
        if self.iam == MOTOR_UT:
            cmd = "PRT=%d" % RELATIVE_DETLA_S 
        elif self.iam == MOTOR_LT:
            cmd = "PRT=-%d" % RELATIVE_DETLA_S
        self.send_to_motor(cmd)
        
        while True:
            self.motor_go()
            if self.send_to_motor(sts_bit[0], True) == "0":
                break
            
        # -------------------------------------------------
        # Set 0 position
        while True:
            self.send_to_motor("O=0")
            if self.send_to_motor("RPA", True) == "0":
                self.curpos = 0
                break
            
        self.init = True
        
    
    def send_to_motor(self, cmd, ret=False):
        if not self.comStatus:
            return
        
        #time.sleep(TSLEEP)
        cmd += "\r"
        self.comSocket.send(cmd.encode())
        self.log.send(self.iam, INFO, "send_to_motor: " + cmd)
        ti.sleep(CMCWTIME)
        res = self.comSocket.recv(REBUFSIZE)
        if ret:
            res = res.decode()
            res = res[:-1]
            self.log.send(self.iam, INFO, "ReceivedFromMotor: " + res)
            
        return res
        
        
    def motor_go(self):
        message = ""
        if self.iam == MOTOR_UT:
            message = "%s Moving (Upper Translator) ..." % self.iam
        elif self.iam == MOTOR_LT:
            message = "%s Moving (Lower Translator) ..." % self.iam
        
        self.log.send(self.iam, INFO, message)
            
        self.send_to_motor("G")
        return self.check_motor()
    
    
    def check_motor(self):
        message = ""
        if self.iam == MOTOR_UT:
            message = "%s Checking (Upper Translator) ..." % self.iam
        elif self.iam == MOTOR_LT:
            message = "%s Checking (Lower Translator) ..." % self.iam
        
        self.log.send(self.iam, INFO, message)
        
        curpos = ""
        while True:
            curpos = self.send_to_motor("RPA", True)
            self.log.send(self.iam, INFO, " CurPos: " + curpos)
            if self.send_to_motor("RBt", True) == "0":
                break
        self.log.send(self.iam, INFO, "idle")   
            
        return curpos
                   

    # CLI
    def move_motor(self, posnum):
        # Set Velocity
        self.send_to_motor("ADT=40")
        self.send_to_motor(VELOCITY_200)
        #self.send_to_motor("GOSUB1")
        
        cmd = ""
        desti = int(self.motor_pos[posnum])
        
        if abs(desti) - abs(self.curpos) < MOTOR_ERR:
            return self.curpos
            
        if self.iam == MOTOR_UT:
            cmd = "PT=%d" % desti
        elif self.iam == MOTOR_LT:
            cmd = "PT=-%d" % desti
            
        self.send_to_motor(cmd)
        curpos = self.motor_go()
        curpos = self.motor_err_correction(desti, curpos)
        self.log.send(self.iam, INFO, "Finished") 
    
        self.curpos = int(curpos)
        return curpos
                
    
    def motor_err_correction(self, desti, curpos):
        
        err = abs(desti) - abs(int(curpos))
        while abs(err) > MOTOR_ERR:
            message = ""
            if self.iam == MOTOR_UT:
                message = "%s error correction (Upper Translate) ..." % self.iam
            elif self.iam == MOTOR_LT:
                message = "%s error correction (Lower Translate) ..." % self.iam
            
            self.log.send(self.iam, INFO, message)
            
            self.send_to_motor(VELOCITY_1)
            #self.send_to_motor("GOSUB2")
            curpos = self.motor_go()
            err = abs(desti) - abs(int(curpos))
        
        return curpos


    # CLI, main
    def move_motor_delta(self, go, delta):  
        # Set Velocity
        self.send_to_motor("ADT=40")
        self.send_to_motor(VELOCITY_1)
        #self.send_to_motor("GOSUB1")

        curpos = self.send_to_motor("RPA", True)
        self.log.send(self.iam, INFO, "CurPos: " + curpos)
        
        cmd = ""
        
        if self.iam == MOTOR_LT:
            if go is True:
                delta *= (-1)
        elif self.iam == MOTOR_UT:
            if go is False:
                delta *= (-1)

        cmd = "PRT=%d" % delta  
        self.send_to_motor(cmd)
        curpos = self.motor_go()
        #self.motor_err_correction(movepos, curpos)
        
        self.log.send(self.iam, INFO, "Finished")
        
        self.curpos = int(curpos)
        return curpos
        


    # CLI
    def setUT(self, posnum):     
        res = self.send_to_motor("RPA", True)
        self.log.send(self.iam, INFO, "CurPos: " + res)

        self.motor_pos[posnum] = res
        utpos = self.motor_pos[0] + "," + self.motor_pos[1]
        self.cfg.set(HK, "ut-pos", utpos )
        sc.SaveConfig(self.cfg, self.ini_file)
        self.log.send(self.iam, INFO, "saved (" + utpos + ")")
        
                
    # CLI
    def setLT(self, posnum):       
        res = self.send_to_motor("RPA", True)
        self.log.send(self.iam, INFO, "CurPos: " + res)

        self.motor_pos[posnum] = str(int(res)*(-1))
        ltpos = ""
        for i in range(4):
            ltpos += self.motor_pos[i]
            ltpos += ","
        self.cfg.set(HK, "lt-pos", ltpos)
        sc.SaveConfig(self.cfg, self.ini_file)
        self.log.send(self.iam, INFO, "saved (" + ltpos + ")")        
        
    
    #-------------------------------
    # sub -> hk    
    def connect_to_server_sub_ex(self):
        # RabbitMQ connect  
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.sub_hk_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
    


    #-------------------------------
    # hk -> sub
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex)      
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
        if not self.comStatus:
            return
        
        #msg = "receive: %s" % cmd
        #self.log.send(self.iam, INFO, msg)
        
        if param[0] == DT_REQ_INITMOTOR:
            self.init_motor()
            msg = "%s %s OK" % (param[0], self.iam)
            self.producer.send_message(DT, self.sub_hk_q, msg)
        else:
            if self.init is False:
                msg = "%s %s TRY" % (DT_REQ_INITMOTOR, self.iam)
                self.producer.send_message(DT, self.sub_hk_q, msg)
            
            elif param[0] == DT_REQ_MOVEMOTOR:
                curpos = self.move_motor(int(param[2]))
                if self.iam == MOTOR_LT:
                    curpos = "%s" % (int(curpos) * (-1))
                msg = "%s %s %s" % (param[0], self.iam, curpos)
                self.producer.send_message(DT, self.sub_hk_q, msg)
                
            elif param[0] == DT_REQ_MOTORGO:
                curpos = self.move_motor_delta(True, int(param[2]))
                if self.iam == MOTOR_LT:
                    curpos = "%s" % (int(curpos) * (-1))
                msg = "%s %s %s" % (param[0], self.iam, curpos)
                self.producer.send_message(DT, self.sub_hk_q, msg)
                
            elif param[0] == DT_REQ_MOTORBACK:
                curpos = self.move_motor_delta(False, int(param[2]))
                if self.iam == MOTOR_LT:
                    curpos = "%s" % (int(curpos) * (-1))
                msg = "%s %s %s" % (param[0], self.iam, curpos)
                self.producer.send_message(DT, self.sub_hk_q, msg)
                
            elif param[0] == DT_REQ_SETUT:
                self.setUT(int(param[2]))
                msg = "%s %s OK" % (param[0], self.iam)
                self.producer.send_message(DT, self.sub_hk_q, msg)
                
            elif param[0] == DT_REQ_SETLT:
                self.setLT(int(param[2]))
                msg = "%s %s OK" % (param[0], self.iam)
                self.producer.send_message(DT, self.sub_hk_q, msg)

    
if __name__ == "__main__":

    #ys.argv.append("ut")
    #sys.argv.append("10007")
    #sys.argv.append("lt")
    #sys.argv.append("10006")
    #if len(sys.argv) < 3:
    #    print("Please add ip and port")
    #    exit()
    
    proc = motor(sys.argv[1], sys.argv[2], sys.argv[3], True)
        
    proc.connect_to_server_sub_ex()
    proc.connect_to_server_hk_q()
        
    proc.connect_to_component()

    #proc.init_motor()
    #proc.move_motor(1)
    
    #proc.move_motor_delta(True, 50)    
    #proc.move_motor_delta(False, 50)

    #proc.setUT(1)
    '''
    proc = motor("lt", "10006")
    #proc = motor("ut", "10007")
    
    proc.connect_to_component()
    
    st = ti.time()
    
    proc.init_motor()
    print("--------------------------------")
    proc.move_motor(3)
    
    duration = ti.time() - st
    print(duration)
    
    #del proc
    '''