"""
... from uploader.py from IGRINS

Modified on Dec 15, 2022

@author: hilee, JJLee
"""

import os, sys
import time as ti
import datetime
import pytz

import pyrebase
import threading

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.HK_def import *
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

#HKLogPath = WORKING_DIR + "IGRINS/Log/Web/tempweb.dat"

FieldNames = [('date', str), ('time', str),
              ('pressure', float),
              ('bench', float), ('bench_tc', float),
              ('grating', float), ('grating_tc', float),
              ('detS', float), ('detS_tc', float),
              ('detK', float), ('detK_tc', float),
              ('camH', float),
              ('detH', float), ('detH_tc', float),
              ('benchcenter', float), ('coldhead01', float), 
              ('coldhead02', float), ('coldstop', float), 
              ('charcoalBox', float), ('camK', float), 
              ('shieldtop', float), ('air', float), 
              ('alert_status', str)]

class uploader():
    
    def __init__(self):
        
        self.iam = "uploader"
        
        self.log = LOG(WORKING_DIR + "/IGRINS", "EngTools")    
        self.log.send(self.iam, INFO, "start")
        
        # load ini file
        self.ini_file = WORKING_DIR + "/IGRINS/Config/"
        cfg = sc.LoadConfig(self.ini_file + "IGRINS.ini")
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_sub_ex = cfg.get(MAIN, "hk_sub_exchange")     
        self.hk_sub_q = cfg.get(MAIN, "hk_sub_routing_key")
                
        firebase = self.get_firebase()
        self.db = firebase.database()
    
        #-------
        #for test
        #self.start_upload_to_firebase(self.db)
        #self.log.send(self.iam, INFO, "Uploaded " + ti.strftime("%Y-%m-%d %H:%M:%S"))
        #-------
        
        self.consumer = None
        #self.connect_to_server_hk_q()
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, DEBUG, th.name + " exit.")
            
        #self.consumer.stop_consumer()
        self.consumer.__del__()
                        

    def get_firebase(self):
        '''
        config = {
            "apiKey": "AIzaSyCDUZO9ejB8LzKPtGB0_5xciByJvYI4IzY",
            "authDomain": "igrins2-hk.firebaseapp.com",
            "databaseURL": "https://igrins2-hk-default-rtdb.firebaseio.com",
            "storageBucket": "igrins2-hk.appspot.com",
            "serviceAccount": "igrins2-hk-firebase-adminsdk-qtt3q-073f6caf5b.json"
            }
        '''
        
        # for test
        config={
            "apiKey": "AIzaSyDSt_O0KmvB5MjrDXuGJCABAOVNp8Q3ZB8",
            "authDomain": "hkp-db-37e0f.firebaseapp.com",
            "databaseURL": "https://hkp-db-37e0f-default-rtdb.firebaseio.com",
            "projectId": "hkp-db-37e0f",
            "storageBucket": "hkp-db-37e0f.appspot.com",
            "messagingSenderId": "1059665885507",
            "appId": "1:1059665885507:web:c4d5dbd322c1c0ff4e17f6",
            "measurementId": "G-450KS9WJF1"
        }

        firebase = pyrebase.initialize_app(config)

        return firebase
    

    def start_upload_to_firebase(self, HK_list):
        HK_dict = self.read_item_to_upload(HK_list)
        if HK_dict is None:
            self.log.send(self.iam, WARNING, "No data ")

        else:
            HK_dict["utc_upload"] = datetime.datetime.now(pytz.utc).isoformat()                
            self.push_hk_entry(self.db, HK_dict)
            self.log.send(self.iam, INFO, HK_dict)


    def read_item_to_upload(self, HK_list):
        #HK_list = open(HKLogPath).read().split()
        # print(len(HK_list), len(FieldNames))
        #HK_list = _hk_list.split()

        if len(HK_list) != len(FieldNames):
            return None

        HK_dict = dict((k, t(v)) for (k, t), v in zip(FieldNames, HK_list))

        HK_dict["datetime"] = HK_dict["date"] + "T" + HK_dict["time"] + "+00:00"

        return HK_dict
    
    
    def push_hk_entry(self, entry):
        self.db.child("BasicHK").push(entry)
        
        
    #-------------------------------
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex, "direct")      
        self.consumer.connect_to_server()
        self.consumer.define_consumer(self.hk_sub_q, self.callback_hk)
        
        th = threading.Thread(target=self.consumer.start_consumer)
        th.start()
            
            
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        #print("uploader:", param)
        if len(param) < 2:
            return
        
        if param[1] != self.iam:
            return
        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)

        if param[0] == HK_REQ_UPLOAD_DB:
            db = param[2:]
            self.start_upload_to_firebase(db)
            
        #elif param[0] == HK_REQ_EXIT:
        #    self.__del__()


if __name__ == "__main__":
    
    fb = uploader()
    
    fb.connect_to_server_hk_q()
    
    
    
    
