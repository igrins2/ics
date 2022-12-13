# -*- coding: utf-8 -*-

"""
Created on Oct 26, 2022

Modified on , 2022

@author: hilee
"""

import os, sys
import time as ti
from time import localtime, strftime 
import Libs.SetConfig as sc
class LOG():

    def __init__(self, work_dir, iam):
                
        # load ini file
        cfg = sc.LoadConfig(work_dir + "/Config/IGRINS.ini")
        
        self.thatday = ti.strftime("%04Y%02m%02d.log", ti.localtime())
        self.path = "%s/Log/%s/" % (work_dir, iam)
        self.createFolder(self.path)
        
        
    def createFolder(self, dir):
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
        except OSError:
            print("Error: Creating directory. " + dir)
        

    def send(self, iam, level, message):
       
        fname = strftime("%Y%m%d", localtime())+".log"
        f_p_name = self.path + self.thatday
        if os.path.isfile(f_p_name):
            file=open(f_p_name,'a+')
        else:
            file=open(f_p_name,'w')
                
        msg = "[%s:%s] %s" % (iam, level, message)    
        data = strftime("%Y-%m-%d %H:%M:%S", localtime()) + ": " + msg + "\n"
        if level != "DEBUG":    
            file.write(data)
            file.close()
        print(data)