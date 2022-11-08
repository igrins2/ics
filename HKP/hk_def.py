# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on Nov 8, 2022

@author: hilee
"""


# -----------------------------------------------------------
# definition: constant
CLASS_NAME = "[House Keeping Package]"
COM_CNT = 8
TM_CNT = 8
PDU_IDX = 8
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
MAIN = "MAIN"
IAM = "HW"
TARGET = "HK"

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
'''
TM_2 = 7
TM_3 = 8
TM_4 = 9
TM_5 = 10
TM_6 = 11
TM_7 = 12
TM_8 = 13
'''
#
# ---------------------------
# motor
MOTOR_LT = 0
MOTOR_UT = 1
RELATIVE_DELTA_L = 100000
RELATIVE_DETLA_S = 10
VELOCITY_200 = "VT=109226"
VELOCITY_1 = "VT=546"
MOTOR_ERR = 100

# ---------------------------
# LOG option
LOGGING = 1
CMDLINE = 2
BOTH = 3

# ---------------------------
#  button
NOT_PRESSED = 0
PRESSED = 1

