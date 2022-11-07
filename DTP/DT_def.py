# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Nov 7, 2022

@author: hilee
"""


# -----------------------------------------------------------
# definition: constant
CLASS_NAME = "[Data Taking Package]"

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
MAIN = "MAIN"
IAM = "DT"
TARGET = ["DCSH", "DCSK"]

# for list index
DCSH = 0
DCSK = 1

# for cal motor moving position
UT = 0
LT = 1

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

# ---------------------------
# LOG option
DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3

# ---------------------------
#  button
#NOT_PRESSED = 0
#PRESSED = 1

MUX_TYPE = 2

FRAME_X = 2048
FRAME_Y = 2048

HK_FN_INITMOTOR = "InitMotor"
HK_FN_MOVEMOTORDELTA = "MoveMotorDelta"
HK_FN_MOVEMOTOR = "MoveMotor"
HK_FN_LAMPCHANGE = "LampChange"

CMD_SIMULATION = "Simulation"
CMD_INITIALIZE1 = "Initialize1"
CMD_INITIALIZE2 = "Initialize2"
CMD_DOWNLOAD = "DownloadMCD"
CMD_SETDETECTOR = "SetDetector"
CMD_SETFSMODE = "SETFSMODE"
CMD_SETFSPARAM = "SetFSParam"
CMD_ACQUIRERAMP = "ACQUIRERAMP"
CMD_STOPACQUISITION = "STOPACQUISITION"