# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Jun 28, 2022

@author: hilee
"""


# -----------------------------------------------------------
# definition: constant
CLASS_NAME = "[Slit Camera Package]"

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
MAIN = "MAIN"
IAM = "SC"
TARGET = "DCSS"

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

CMD_SIMULATION = "Simulation"
CMD_INITIALIZE1 = "Initialize1"
CMD_INITIALIZE2 = "Initialize2"
CMD_DOWNLOAD = "DownloadMCD"
CMD_SETDETECTOR = "SetDetector"
CMD_SETFSMODE = "SETFSMODE"
CMD_SETWINPARAM = "SetWinParam"
CMD_SETRAMPPARAM = "SetRampParam"
CMD_SETFSPARAM = "SetFSParam"
CMD_ACQUIRERAMP = "ACQUIRERAMP"
CMD_STOPACQUISITION = "STOPACQUISITION"

