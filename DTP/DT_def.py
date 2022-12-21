# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Dec 15, 2022

@author: hilee
"""


# -----------------------------------------------------------
# definition: constant

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
MAIN = "MAIN"
DT = "DT"
HK = "HK"

# LOG option
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

PDU_IDX = 8

SERV_CONNECT_CNT = 4 #Inst.sequencer / EngTools / DCS / hk Sub
INST_SEQ = 0
ENG_TOOLS = 1
DCS = 2
HK_SUB = 3

DCS_CNT = 3
SVC = 0
H = 1
K = 2

MODE_HK = 0
MODE_WHOLE = 1
MODE_SVC = 2
MODE_H = 3
MODE_K = 4

T_frame = 1.45479
T_exp = 1.63
T_minFowler = 0.168
T_br = 2

# for cal motor moving position
COM_CNT = 3
PDU = 0
LT = 1
UT = 2

PREV = 0
NEXT = 1

CAL_CNT = 9

EMPTY = 0
FOLD_MIRROR = 1
MOTOR_UT = [EMPTY, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, EMPTY]

EMPTY = 0
DARK_MIRROR = 1
PINHOLE = 2
USAF = 3
MOTOR_LT = [DARK_MIRROR, EMPTY, EMPTY, EMPTY, PINHOLE, FOLD_MIRROR, USAF, USAF, EMPTY]

FLAT = 3
THAR = 4
OFF = 0
ON = 1
LAMP_FLAT = [OFF, ON, OFF, OFF, ON, OFF, OFF, OFF, OFF]
LAMP_THAR = [OFF, OFF, OFF, ON, OFF, ON, OFF, OFF, OFF]

MUX_TYPE = 2

FRAME_X = 2048
FRAME_Y = 2048

DT_REQ_INITMOTOR = "InitMotor"  #motor  
DT_REQ_MOVEMOTOR = "MoveMotor"  #motor
DT_REQ_MOTORGO = "MotorGo"      #motor
DT_REQ_MOTORBACK = "MotorBack"  #motor

DT_REQ_SETUT = "SetUT"          #motor
DT_REQ_SETLT = "SetLT"          #motor

EXIT = "Exit"
ALIVE = "Alive"
TEST_MODE = "TestMode"

#HK_FN_LAMPCHANGE = "LampChange"
HK_REQ_PWR_STS = "PowerStatus"  #pdu
HK_REQ_PWR_ONOFF = "PowerOnOff" #pdu

CMD_SIMULATION = "Simulation"
CMD_INITIALIZE1 = "Initialize1"
CMD_INITIALIZE2 = "Initialize2"

CMD_RESETASIC = "ResetASIC"
CMD_DOWNLOAD = "DownloadMCD"
CMD_SETDETECTOR = "SetDetector"
CMD_SETFSMODE = "SETFSMODE"

CMD_SETFSPARAM = "SetFSParam"
CMD_ACQUIRERAMP = "ACQUIRERAMP"
CMD_STOPACQUISITION = "STOPACQUISITION"

#REQ_CHK = "AliveCheck"
