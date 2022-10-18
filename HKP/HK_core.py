# -*- coding: utf-8 -*-
"""
Created on Sep 17, 2021

Modified on May 9, 2022

@author: hilee
"""

#from curses import baudrate
import os
import Libs.SetConfig as sc
#import asyncio
from socket import *
import threading
import time
from time import localtime, strftime 

from HKP.HK_def import *

import serial


dtvalue_key_list = ["tmc1-temp-a",
                    "tmc1-temp-b",
                    "tmc2-temp-a",
                    "tmc2-temp-b",
                    "tmc3-temp-a",
                    "tmc3-temp-b",
                    "tm-temp-1",
                    "tm-temp-2",
                    "tm-temp-3",
                    "tm-temp-4",
                    "tm-temp-5",
                    "tm-temp-6",
                    "tm-temp-7",
                    "tm-temp-8"]

'''
class DewarFromKey():
    def __init__(self, key_to_label, labels, real_dewar):
        self._key_to_label = key_to_label
        self._loc_from = dict((n, i) for i, n in enumerate(labels))
        self._real_dewar = real_dewar

    def _get_loc(self, k):
        label = self._key_to_label[k]
        loc = self._loc_from.get(label, None)
        return loc

    def __getitem__(self, k):
        loc = self._get_loc(k)
        if loc is None:
            return DumbEntry()
        return self._real_dewar[loc]
'''    



class HK() :
    def __init__(self, gui=False):
        
        self.gui = gui
        print("start HKP!!!")        
        # definition: variables
        global COM_IP, COM_PORT
        global UT_POS, LT_POS
        global TOUT, TSLEEP, CMCWTIME
        global REBUFSIZE, CMCREBUFSIZE
            
        self.comList = ["tmc1", "tmc2", "tmc3", "tm", "vmc", "lt", "ut", "pdu"]
        COM_IP, COM_PORT = [], []
        self.comStatus = [False for _ in range(COM_CNT)]
        
        #for CLI mode
        self.comSocket = [None for _ in range(COM_CNT)]
                
        #for async
        #self.comReader = ["" for _ in range(COM_CNT)]
        #self.comWriter = ["" for _ in range(COM_CNT)]
         
        self.pow_flag = ["OFF" for _ in range(PDU_IDX)]

        # load ini file
        self.config_dir = "/IGRINS/TEST/Config"
        os.environ["IGRINS_CONFIG"] = ",".join([os.path.join(self.config_dir,
                                                         "IGRINS.ini"),
                                            os.path.join(self.config_dir,
                                                         "IGRINS_test.ini")])
        self.ini_file = sc.get_ini_files(
            env_name="IGRINS_CONFIG", default_file=""
        )
        #self.logwrite(CMDLINE, ini_file)
        self.cfg = sc.LoadConfig(self.ini_file)

        self.key_to_label = {}
        for k in dtvalue_key_list:
            v = self.cfg.get('HK', k)
            k0, k1, k2 = k.split("-")
            self.key_to_label[k0 + "-" + k2] = v
        
        #self.logwrite(CMDLINE, key_to_label)    
        
        #self.logwrite(CMDLINE, self.dtvalue_from_label.as_dict()) 
        
        #self.dewar = []
        #self.dewar_from_key = DewarFromKey(key_to_label, hk_labels, self.dewar)
        #self.logwrite(CMDLINE, self.dewar_from_key)
        
        TOUT = int(self.cfg.get("HK", "tout"))
        TSLEEP = int(self.cfg.get('HK','tsleep'))
        CMCWTIME = float(self.cfg.get("HK", "cmcwtime"))
        REBUFSIZE = int(self.cfg.get("HK", "rebufsize"))
        CMCREBUFSIZE = int(self.cfg.get("HK", "cmcrebufsize"))
        
        #read TEMP list from IGRINS.ini
        TEMP_LIST = self.cfg.get('HK','temp-descriptions').split(',')
        self.TEMPTEMPERATURE = [s.strip() for s in TEMP_LIST]
        
        #read Interval from IGRINS.ini
        self.Period = int(self.cfg.get('HK','hk-monitor-intv'))
        
        #read IP, port
        for name in self.comList:
            COM_IP.append(self.cfg.get("HK", name + "-ip"))
            COM_PORT.append(self.cfg.get("HK", name + "-port"))
            
        PDU_LIST = self.cfg.get('HK','pdu-list').split(',')
        self.POWERSTR = PDU_LIST

        #self.logwrite(CMDLINE, COM_IP)
        #self.logwrite(CMDLINE, COM_PORT)
                
        UT_POS = self.cfg.get("HK", "ut-pos").split(",")
        LT_POS = self.cfg.get("HK", "lt-pos").split(",")
        #self.logwrite(CMDLINE, LT_POS)
        #self.logwrite(CMDLINE, UT_POS)
        
        self.mainlogpath=self.cfg.get('MAIN','main-log-location')

        self.logpath=self.cfg.get('HK','hk-log-location')
        self.webpath=self.cfg.get('HK','hk-web-location')
        
        self.alert_label = self.cfg.get("HK", "hk-alert-label")  
        self.alert_temperature = int(self.cfg.get("HK", "hk-alert-temperature"))
        self.alert_email = self.cfg.get("HK", "hk-alert-email")
           
        self.cur_err = [False for _ in range(COM_CNT)]
        
        #self.logwrite(CMDLINE, TOUT)
        #self.logwrite(CMDLINE, CMCWTIME)
        #self.logwrite(CMDLINE, CMCREBUFSIZE)
        
        #----------------------------
        #for testing stable com... 20220621
        self.se_device = -1 #TMC3 
        self.se_port = "/dev/ttyS1"    
        self.comSerial = None
        
    # --------------------------------------------------
    # CLI
    def connect_to_component(self, nCom):
        
        #-------------------------------
        #without reconnect!!! 20220621
        if nCom == self.se_device:
            while True:
                try:
                    self.comSerial = serial.Serial(port=self.se_port, 
                                                   baudrate=9600, 
                                                   parity=serial.PARITY_ODD, 
                                                   stopbits=serial.STOPBITS_ONE, 
                                                   bytesize=serial.SEVENBITS)
                except (OSError, serial.SerialException):
                    continue
                
                else:
                    #print("connect", self.comSerial)
                    self.logwrite(BOTH, "[COM1] " + self.comList[nCom] + " is connected")
                    self.comStatus[nCom] = True
                    break
            return
        #-------------------------------
            
        try:            
            self.comSocket[nCom] = socket(AF_INET, SOCK_STREAM)
            self.comSocket[nCom].settimeout(TOUT)
            self.comSocket[nCom].connect((COM_IP[nCom], int(COM_PORT[nCom])))
            self.comStatus[nCom] = True
            
            if self.gui:
                self.logwrite(BOTH, self.comList[nCom] + " is connected")
            else:
                self.logwrite(CMDLINE, CLASS_NAME + " connection success (" + self.comList[nCom] + ")")
                
            if self.gui and self.cur_err[nCom]:
                self.cur_err[nCom] = False
                
                if nCom == VMC:
                    return
                
                log = ""    
                try:
                    buf = self.comSocket[nCom].recv(REBUFSIZE)
                    log = "recv %s <<< (reading from buffer) %s" % (self.comList[nCom], buf)
                except:
                    log = "recv %s <<< fail: reading from buffer" % (self.comList[nCom])
                self.logwrite(LOGGING, log)
            
        except:
            self.comSocket[nCom] = None
            self.comStatus[nCom] = False
            if self.gui:
                self.logwrite(BOTH, self.comList[nCom] + " is not connected")
                self.re_connect_to_component(nCom)
            else:
                self.logwrite(CMDLINE, CLASS_NAME + " connection fail (" + self.comList[nCom] + ")")
              
    
    def re_connect_to_component(self, nCom):
        #time.sleep(TOUT)
        self.cur_err[nCom] = True
        self.logwrite(BOTH, self.comList[nCom] + " is trying to connect again")
        if self.comSocket[nCom] != None:
            self.close_component(nCom)
        self.connect_to_component(nCom)
        ### ????
        #self.reconnect_T = threading.timer(0.5, self.connect_to_component, nCom)
        

           
    # CLI
    def close_component(self, nCom):
        
        #-------------------------
        #20220621
        if nCom == self.se_device:
            self.comSerial.close()
            self.logwrite(BOTH, "[COM1] " + self.comList[nCom] + " closed")
        else:  
        #-------------------------
            self.comSocket[nCom].close()
        self.comStatus[nCom] = False
        
        
    # CLI, TMC-Get SetPoint
    def get_setpoint_fromTMC(self, nCom, nPort):
        cmd = "SETP? %d" % nPort
        cmd += "\r\n"
        return self.socket_send_recv(nCom, nPort, cmd)


    # CLI, TMC-Heating Value
    def get_heating_power(self, nCom, nPort):
        cmd = "HTR? %d" % nPort
        cmd += "\r\n"
        return self.socket_send_recv(nCom, nPort, cmd)
    
    
    # CLI, TMC-Heating(Manual) Get Value
    def get_heating_power_manual(self, nCom, nPort):
        cmd = "MOUT? %d" % nPort
        cmd += "\r\n"
        return self.socket_send_recv(nCom, nPort, cmd) 
    
    
    # CLI, TMC-Heating(Manual) Set Value
    def SetHeatingValue_manual(self, nCom, nPort, value):
        cmd = "MOUT %d,%f" % (nPort, value)
        cmd += "\r\n"
        return self.socket_send_recv(nCom, nPort, cmd)
    

    # CLI, TMC-Monitorig
    def get_value_fromTMC(self, nCom, sPort):  
        cmd = "KRDG? " + sPort
        cmd += "\r\n"
        return self.socket_send_recv(nCom, sPort, cmd)

    # CLI, TM-Monitorig
    def get_value_fromTM(self, nPort):
        cmd = "KRDG? %d" % nPort
        cmd += "\r\n"
        return self.socket_send_recv(TM, nPort, cmd)

    # CLI, Vaccum monitoring
    #PR1 - MicroPirani, PR2/PR5 - Cold Cathode, PR3 - both (3 digits), PR4 - both (4 digits)
    def get_value_fromVM(self):
        cmd = "@253PR3?;FF"
        cmd += "\r\n"
        return self.socket_send_recv(VMC, 1, cmd)

    # Socket function
    def socket_send_recv(self, nCom, port, cmd):
        try:         
            #-------------------------
            #20220621
            log = ""
            if nCom == self.se_device:
                self.comSerial.write(cmd.encode())
                log = "[COM1] "
            else:
            #-------------------------
                self.comSocket[nCom].send(cmd.encode())
            
            if port == "A" or port == "B":
                log += "send: %s %s >>> %s" % (self.comList[nCom], port, cmd)
            else:
                log += "send: %s %d >>> %s" % (self.comList[nCom], port, cmd)
            self.logwrite(LOGGING, log)
        
            if cmd.find("MOUT ") == 0:
                d1, d2 = cmd.split(',')
                print("set:",str(float(d2)))
                return None
            
            #-------------------------
            #20220621
            res0 = ""
            log = ""
            if nCom == self.se_device:
                res0 = self.comSerial.readline()
                log = "[COM1] "
            else:
            #-------------------------
                res0 = self.comSocket[nCom].recv(REBUFSIZE)
            info = res0.decode()
                        
            if port == "A" or port == "B":
                log += "recv %s %s <<< %s" % (self.comList[nCom], port, info)
            else:
                log += "recv %s %d <<< %s" % (self.comList[nCom], port, info)
            self.logwrite(LOGGING, log)
            
            if info.find("\x00") >= 0:
                return None                
                      
            if self.gui:
                if nCom == VMC:
                    return info[7:-3]
                else:
                    #res = ""
                    #if info.find('\r\n') >= 0:
                    #    res = info[:-2]
                        
                    info_rest = ""
                    if info.find('\r\n') < 0:
                        #-------------------------
                        #20220621
                        log = ""
                        res0 = ""
                        if nCom == self.se_device:
                            res0 = self.comSerial.readline()
                            log = "[COM1] "
                        else:
                        #-------------------------
                            res0 = self.comSocket[nCom].recv(REBUFSIZE)
                        info_rest = res0.decode()
                        
                        log += "recv %s %d <<< %s" % (self.comList[nCom], port, info_rest)
                        self.logwrite(LOGGING, log)      
                        info += info_rest
                    return info[:-2]
            else:
                if nCom == VMC:
                    message = "%s received: %.2e (%s)" % (CLASS_NAME, float(info[7:-3]), self.comList[nCom])
                    self.logwrite(CMDLINE, message)
                    return info[7:-3]
                elif port == "A" or port == "B":
                    message = "%s received: %s (%s port %s)" % (CLASS_NAME, info[:-2], self.comList[nCom], port)
                    self.logwrite(CMDLINE, message)
                    return info[:-2]
                else:
                    message = "%s received: %s (%s port %d)" % (CLASS_NAME, info[:-2], self.comList[nCom], port)
                    self.logwrite(CMDLINE, message)
                    return info[:-2]

        except:
        
            if not self.gui:
                if nCom == VMC:
                    message = "%s sending fail (%s)" % (CLASS_NAME, self.comList[nCom])
                elif port == "A" or port == "B":
                    message = "%s sending fail (%s port %s)" % (CLASS_NAME, self.comList[nCom], port)
                else:
                    message = "%s sending fail (%s port %d)" % (CLASS_NAME, self.comList[nCom], port)
                self.logwrite(CMDLINE, message)
                
                return None
            
            self.comStatus[nCom] = False
            self.re_connect_to_component(nCom)
            
        

    # CLI
    def initPDU(self):
        if not self.comStatus[PDU]:
            return 
        
        try:
            cmd = "@@@@\r"
            self.comSocket[PDU].send(cmd.encode())
            log = "send: %s >>> %s" % (self.comList[PDU], cmd)
            self.logwrite(LOGGING, log)
            
            res = self.comSocket[PDU].recv(REBUFSIZE)
            log = "recv %s <<< %s" % (self.comList[PDU], res.decode())
            self.logwrite(LOGGING, log)
            
            cmd = "DN0\r"   #need to check!!!
            self.power_status(cmd) 
                
            if self.gui:
                self.logwrite(BOTH, "powctr init is completed")
            else:
                self.logwrite(CMDLINE, CLASS_NAME + " powctr init is completed (" + self.comList[PDU] + ")")
                    
        except:
            if self.gui:
                self.logwrite(BOTH, "powctr init is error")
                   
                self.comStatus[PDU] = False
                self.re_connect_to_component(PDU)
            else:
                self.logwrite(CMDLINE, CLASS_NAME + " sending fail (" + self.comList[PDU] + ")")
        
                    
    def power_status(self, cmd):
        if not self.comStatus[PDU]:
            return      
        
        try:
            self.comSocket[PDU].send(cmd.encode())
            log = "send: %s >>> %s" % (self.comList[PDU], cmd)
            self.logwrite(LOGGING, log)
            time.sleep(TSLEEP)
            res = self.comSocket[PDU].recv(REBUFSIZE)
            sRes = res.decode()
            log = "recv %s <<< %s" % (self.comList[PDU], sRes)
            self.logwrite(LOGGING, log)
            
            # check PDU status
            for i in range(PDU_IDX):
                if sRes.find("OUTLET %d ON" % (i + 1,)) >= 0:
                    self.pow_flag[i] = "ON"
                    if not self.gui:
                        message =  "%s Power %d ON" % (CLASS_NAME, i+1)
                        self.logwrite(CMDLINE, message)
                else:
                    self.pow_flag[i] = "OFF"
                    if not self.gui:
                        message =  "%s Power %d OFF" % (CLASS_NAME, i+1)
                        self.logwrite(CMDLINE, message)
        except:
            if self.gui:
                self.logwrite(BOTH, "powctr sending fail")
                   
                self.comStatus[PDU] = False
                self.re_connect_to_component(PDU)
            else:
                self.logwrite(CMDLINE, CLASS_NAME + " sending fail (" + self.comList[PDU] + ")")               


    # CLI, main - on/off�� �ٷ� �����ϸ� �ȵǳ�??? �Ʒ��ڵ� �׽�Ʈ �غ���, �ȵǸ� ����!
    def change_power(self, nIndex, sOnOff):  # definition OnOff: ON, OFF
        # this function is used when received PDU On/Off status and change status
        
        if not self.comStatus[PDU]:
            return
        
        if sOnOff == OFF:
            self.pow_flag[nIndex-1] = "OFF"
            cmd = "F0%d\r" % (nIndex)
        elif sOnOff == ON:
            self.pow_flag[nIndex-1] = "ON"
            cmd = "N0%d\r" % (nIndex)
        '''
        if sOnOff == OFF and self.pow_flag[nIndex-1] == "ON":
            self.pow_flag[nIndex-1] = "OFF"
            cmd = "F0%d\r" % (nIndex)
        elif sOnOff == ON and self.pow_flag[nIndex-1] == "OFF":
            self.pow_flag[nIndex-1] = "ON"
            cmd = "N0%d\r" % (nIndex)
        #else:
        #    return 
        '''
            
        if self.gui:
            msg = " %s Button clicked"  % self.pow_flag[nIndex-1]
            self.logwrite(BOTH, self.POWERSTR[nIndex-1] + msg)
    
        self.power_status(cmd)
        
        if not self.gui:
            self.logwrite(CMDLINE, "---------------------------------------------------------")
        #self.logwrite(CMDLINE, res.decode())


    # CLI
    def init_motor(self, nMotorNum):
        
        self.send_to_motor(nMotorNum, "ZS")
        self.send_to_motor(nMotorNum, "ECHO_OFF")

        message = ""
        if nMotorNum == MOTOR_UT:
            message = "%s Initializing (Upper Translator) ..." % CLASS_NAME
        elif nMotorNum == MOTOR_LT:
            message = "%s Initializing (Lower Translator) ..." % CLASS_NAME
        
        if not self.gui:
            self.logwrite(CMDLINE, message)
        
        # -------------------------------------------------
        # Go to left 
        self.send_to_motor(nMotorNum, "ADT=40")
        self.send_to_motor(nMotorNum, VELOCITY_200)
        #self.send_to_motor(nMotorNum, "GOSUB1")
        
        cmd = ""
        
        if nMotorNum == MOTOR_UT:
            cmd = "PRT=-%d" % RELATIVE_DELTA_L 
        elif nMotorNum == MOTOR_LT:
            cmd = "PRT=%d" % RELATIVE_DELTA_L
        self.send_to_motor(nMotorNum, cmd)
            
        sts = ["", ""]
        sts_ut = ["RIN(3)", "RBl"]
        sts_lt = ["RIN(2)", "RBr"]
        sts_bit = []
        if nMotorNum == MOTOR_UT:
            sts_bit = sts_ut
        elif nMotorNum == MOTOR_LT:
            sts_bit = sts_lt
                
        while True:
            self.motor_go(nMotorNum)
            
            sts[0] = self.send_to_motor(nMotorNum, sts_bit[0], True)
            sts[1] = self.send_to_motor(nMotorNum, sts_bit[1], True)
        
            if sts[0] == "1" and sts[1] == "1":
                break
                        
        # -------------------------------------------------
        # reset the bits
        while True:
            self.send_to_motor(nMotorNum, "ZS")
            if self.send_to_motor(nMotorNum, sts_bit[1], True) == "0":
                break
                           
        # -------------------------------------------------
        # Go to near the bit 3(ut) or 2(lt)
        self.send_to_motor(nMotorNum, VELOCITY_1)
        #self.send_to_motor(nMotorNum, "GOSUB2")
        
        if nMotorNum == MOTOR_UT:
            cmd = "PRT=%d" % RELATIVE_DETLA_S 
        elif nMotorNum == MOTOR_LT:
            cmd = "PRT=-%d" % RELATIVE_DETLA_S
        self.send_to_motor(nMotorNum, cmd)
        
        while True:
            self.motor_go(nMotorNum)
            sts[0] = self.send_to_motor(nMotorNum, sts_bit[0], True)
            if sts[0] == "0":
                break
            
        # -------------------------------------------------
        # Set 0 position
        while True:
            self.send_to_motor(nMotorNum, "O=0")
            if self.send_to_motor(nMotorNum, "RPA", True) == "0":
                break
        
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " Finished!")


    
    def send_to_motor(self, nMotorNum, cmd, ret=False):
        #time.sleep(TSLEEP)
        cmd += "\r"
        self.comSocket[5 + nMotorNum].send(cmd.encode())
        self.logwrite(CMDLINE, "send_to_motor: " + cmd)
        time.sleep(CMCWTIME)
        if ret:
            res = self.comSocket[5 + nMotorNum].recv(REBUFSIZE)
            #self.logwrite(CMDLINE, "[Debug]", res.decode())
            res = res.decode()
            res = res[:-1]          
            self.logwrite(CMDLINE, "ReceivedFromMotor: " + res)
        else:
            res = ""
            
        return res
        
        
    def motor_go(self, nMotorNum):
        message = ""
        if nMotorNum == MOTOR_UT:
            message = "%s Moving (Upper Translator) ..." % CLASS_NAME
        elif nMotorNum == MOTOR_LT:
            message = "%s Moving (Lower Translator) ..." % CLASS_NAME
        
        if not self.gui:
            self.logwrite(CMDLINE, message)
            
        self.send_to_motor(nMotorNum, "G")
        return self.check_motor(nMotorNum)
    
    
    def check_motor(self, nMotorNum):
        message = ""
        if nMotorNum == MOTOR_UT:
            message = "%s Checking (Upper Translator) ..." % CLASS_NAME
        elif nMotorNum == MOTOR_LT:
            message = "%s Checking (Lower Translator) ..." % CLASS_NAME
        if not self.gui:
            self.logwrite(CMDLINE, message)
        curpos = ""
        while True:
            curpos = self.send_to_motor(nMotorNum, "RPA", True)
            if not self.gui:
                self.logwrite(CMDLINE, CLASS_NAME + " CurPos: " + curpos)
            if self.send_to_motor(nMotorNum, "RBt", True) == "0":
                break
        if not self.gui:    
            self.logwrite(CMDLINE, CLASS_NAME + " idle")   
        return curpos
                   

    # CLI
    def move_motor(self, nMotorNum, nPosNum):
        # Set Velocity
        self.send_to_motor(nMotorNum, "ADT=40")
        self.send_to_motor(nMotorNum, VELOCITY_200)
        #self.send_to_motor(nMotorNum, "GOSUB1")
        
        cmd = ""
        desti = 0
        if nMotorNum == MOTOR_UT:
            desti = int(UT_POS[nPosNum])
            cmd = "PT=%d" % desti
        elif nMotorNum == MOTOR_LT:
            desti = int(LT_POS[nPosNum])
            cmd = "PT=-%d" % desti
            
        self.send_to_motor(nMotorNum, cmd)
        curpos = self.motor_go(nMotorNum)
        self.motor_err_correction(nMotorNum, desti, curpos)
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " Finished!")
                
                
    
    def motor_err_correction(self, nMotorNum, nDesti, nCurPos):
        
        err = abs(nDesti) - abs(int(nCurPos))
        while abs(err) > MOTOR_ERR:
            message = ""
            if nMotorNum == MOTOR_UT:
                message = "%s error correction (Upper Translate) ..." % CLASS_NAME
            elif nMotorNum == MOTOR_LT:
                message = "%s error correction (Lower Translate) ..." % CLASS_NAME
            if not self.gui:
                self.logwrite(CMDLINE, message)
            self.send_to_motor(nMotorNum, VELOCITY_1)
            #self.send_to_motor(nMotorNum, "GOSUB2")
            nCurPos = self.motor_go(nMotorNum)
            err = abs(nDesti) - abs(int(nCurPos))


    # CLI, main
    def move_motor_delta(self, nMotorNum, go, nDelta):  
        # Set Velocity
        self.send_to_motor(nMotorNum, "ADT=40")
        self.send_to_motor(nMotorNum, VELOCITY_1)
        #self.send_to_motor(nMotorNum, "GOSUB1")

        curpos = self.send_to_motor(nMotorNum, "RPA", True)
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " CurPos: " + curpos)
        
        cmd = ""
        '''
        if nMotorNum == MOTOR_UT:
            if nDelta > 0:
                cmd = "PRT=%d" % nDelta
            else:
                cmd = "PRT=-%d" % nDelta
        '''
        if nMotorNum == MOTOR_LT:
            if go is True:
                nDelta *= (-1)
        elif nMotorNum == MOTOR_UT:
            if go is False:
                nDelta *= (-1)

        cmd = "PRT=%d" % nDelta  
        self.send_to_motor(nMotorNum, cmd)
        curpos = self.motor_go(nMotorNum)
        #self.motor_err_correction(nMotorNum, movepos, curpos)
        
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " Finished!")


    # CLI
    def setUT(self, nPosNum):
        #self.logwrite(CMDLINE, CLASS_NAME + " SetUT:", posnum, value)
        
        res = self.send_to_motor(MOTOR_UT, "RPA", True)
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " CurPos: " + res)

        UT_POS[nPosNum] = res
        utpos = UT_POS[0]+","+UT_POS[1]
        self.cfg.set("HK", "ut-pos", utpos )
        sc.SaveConfig(self.cfg, self.ini_file[0])
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " saved (" + utpos + ")")
        
                
    # CLI
    def setLT(self, nPosNum):
        #self.logwrite(CMDLINE, CLASS_NAME + " SetLT:", posnum, value)
        
        res = self.send_to_motor(MOTOR_LT, "RPA", True)
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " CurPos: " + res)

        LT_POS[nPosNum] = str(int(res)*(-1))
        ltpos = ""
        for i in range(4):
            ltpos += LT_POS[i]
            ltpos += ","
        self.cfg.set("HK", "lt-pos", ltpos)
        sc.SaveConfig(self.cfg, self.ini_file[0])
        if not self.gui:
            self.logwrite(CMDLINE, CLASS_NAME + " saved (" + ltpos + ")")
        
        
    def save_setpoint(self, setp):
        for i, v in enumerate(setp):
            key = "setp%d" % (i+1)
            self.cfg.set("HK", key, v)
        
        self.logwrite(CMDLINE, self.cfg)
        self.logwrite(CMDLINE, self.ini_file)
        sc.SaveConfig(self.cfg, self.ini_file[0])   #IGRINS.ini


    def logwrite(self, option, event):
        '''
        Function that write to file for Logging
        event : Logging Sentence
        option :  LOGGING(1) - Write to File
                  CMDLINE(2) - Write to Command Line
                  BOTH(3) - Wrte to File and Command Line
        '''
        if option == CMDLINE:
            print(event)
        else:
            fname = strftime("%Y%m%d", localtime())+".log"
            f_p_name = self.mainlogpath+fname
            if os.path.isfile(f_p_name):
                file=open(f_p_name,'a+')
            else:
                file=open(f_p_name,'w')
            
            if option == LOGGING:
                file.write(strftime("[%Y-%m-%d %H:%M:%S]", localtime()) + ": " + event + "\n")
                file.close()
        
            elif option == BOTH:
                file.write(strftime("[%Y-%m-%d %H:%M:%S]", localtime()) + ": " + event + "\n")
                file.close()
                print(event)
    

