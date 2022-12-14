# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on Nov 26, 2021

@author: hilee
"""

import os

dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"

MAIN = "MAIN"
HK = "HK"
DT = "DT"

COM_CNT = 9

TMC3 = 2
TM = 3
VM = 4
PDU = 5
LT = 6
UT = 7
UPLOADER = 8

SERV_CONNECT_CNT = 2    #HKP, DTP
HKP = 0
DTP = 1

MODE_SIMUL = 0
MODE_REAL = 1

REQ_CHK = "AliveCheck"

EXIT = "Exit"
ALIVE = "Alive"
TEST_MODE = "TestMode"

