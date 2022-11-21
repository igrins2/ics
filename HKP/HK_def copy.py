# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on Nov 8, 2022

@author: hilee
"""
CLASS_NAME = "House Keeping Package"

# -----------------------------------------------------------
# definition: constant
COM_CNT = 8
TM_CNT = 8  #will remove
PDU_IDX = 8
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
MAIN = "MAIN"
IAM = "HK"
TARGET = "HK"

# will remove
LOGGING = 1
CMDLINE = 2
BOTH = 3

#RETRY_CNT = 5
# ---------------------------
# components
TMC1 = 0
TMC2 = 1
TMC3 = 2
TM = 3
VMC = 4
LT = 5
UT = 6
PDU = 7

# ---------------------------
ON = "on"
OFF = "off"

# ---------------------------
# temperature
TMC1_A = 0
TMC1_B = 1
TMC2_A = 2
TMC2_B = 3
TMC3_A = 4
TMC3_B = 5
TM_1 = 6

#
# ---------------------------
# motor
RELATIVE_DELTA_L = 100000
RELATIVE_DETLA_S = 10
VELOCITY_200 = "VT=109226"
VELOCITY_1 = "VT=546"
MOTOR_ERR = 100

NOT_PRESSED = 0
PRESSED = 1

HK_REQ_GETSETPOINT = "GetSetPoint"  #temp_ctrl
HK_REQ_GETHEATINGPOWER = "GetHeatingPower"  #temp_ctrl
HK_REQ_GETVALUE = "GetValue"    #temp_ctrl, monitor, vm
HK_REQ_PWR_ONOFF = "PowerOnOff" #pdu
HK_REQ_UPLOAD_DB = "UploadDB"   #uploader

HK_REQ_INITMOTOR = "InitMotor"  #motor  
HK_REQ_MOVEMOTOR = "MoveMotor"  #motor
HK_REQ_MOTORGO = "MotorGo"      #motor
HK_REQ_MOTORBACK = "MotorBack"  #motor

HK_REQ_SETUT = "SetUT"          #motor
HK_REQ_SETLT = "SetLT"          #motor

HK_REQ_EXIT = "Exit"

