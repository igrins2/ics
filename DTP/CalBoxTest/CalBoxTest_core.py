# -*- coding: utf-8 -*-

"""
Created on Jan 4, 2022

Modified...

@author: hilee
"""

import os
import sys
from DTP.CalBoxTest.CalBoxTest_def import *

sys.path.append("..")
from DTP.DT import *    #for CLI

sys.path.append("..")
import Libs.SetConfig as sc

class CalBoxTest():
    def __init__(self, gui=False):
        
        self.gui = gui
        self.dt = DT()
        print("start Calibration Box Test!!!")
        
        self.fExpTime, self.nRepeat = [DEFAULT_EXPTIME], [DEFAULT_REPEAT]
        
        self.config_dir = "/IGRINS/TEST/Config"
        os.environ["IGRINS_CONFIG"] = ",".join([os.path.join(self.config_dir,
                                                         "IGRINS.ini"),
                                            os.path.join(self.config_dir,
                                                         "IGRINS_test.ini")])
        self.ini_file = sc.get_ini_files(
            env_name="IGRINS_CONFIG", default_file=""
        )
        #print(ini_file)
        self.cfg = sc.LoadConfig(self.ini_file)
        
        self.UT_POS = self.cfg.get("HK", "ut-pos").split(",")
        self.LT_POS = self.cfg.get("HK", "lt-pos").split(",")


    def RunMode(self, *args):
        # self.hDt.CalBox_ChangeMode(mode, fExpTime, nRepeat)
        print(CLASS_NAME + " RunMode:", args)
        if self.gui:    #message com
            pass
        else:
            for list in args:
                mode = list[0]
                fExptime = list[1]
                nRepeat = list[2]
                
                self.dt.CalBox_Mode(mode, fExptime, nRepeat)
                


    def MoveDelta(self, motor, nDelta):
        # self.hDt.CalBox_MoveDelta(motor, fDelta)
        print(CLASS_NAME + " MoveDelta:", motor, nDelta)
        if self.gui:    #message com    
            pass
        else:
            self.dt.CalBox_MoveDelta(motor, nDelta)


    def SetPosition(self, motor, nPosition, nValue):
        # self.hDt.CalBox_SetPosition(motor, position, fValue)
        print(CLASS_NAME + " SetPosition:", motor, nPosition, nValue)
        
        if motor == MOTOR_UT:
            self.UT_POS[nPosition] = nValue
            utpos = self.UT_POS[0]+","+self.UT_POS[1]
            self.cfg.set("HK", "ut-pos", utpos )
            sc.SaveConfig(self.cfg, self.ini_file[0])
        
        elif motor == MOTOR_LT:
            self.LT_POS[nPosition] = nValue
            ltpos = ""
            for i in range(5):
                ltpos += self.LT_POS[i]
                ltpos += ","
            self.cfg.set("HK", "lt-pos", ltpos)
            sc.SaveConfig(self.cfg, self.ini_file[0])
        
        
