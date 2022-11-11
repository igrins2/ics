from email.utils import localtime
import os, sys
import time as ti
import datetime
import pytz

import pyrebase
import threading

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.HK_def import *
import Libs.SetConfig as sc
import Libs.rabbitmq_server as serv
from Libs.logger import *

HKLogPath = WORKING_DIR + "/IGRINS/Log/Web/tempweb.dat"

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
        
        self.log = LOG(WORKING_DIR + "IGRINS", TARGET)
        
        self.iam = "uplader"
        self.log.logwrite(self.iam, INFO, "start")
        
        # load ini file
        self.ini_file = WORKING_DIR + "/IGRINS/Config/"
        cfg = sc.LoadConfig(self.ini_file + "IGRINS.ini")
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_sub_ex = cfg.get(MAIN, "hk_sub_exchange")     
        self.hk_sub_q = cfg.get(MAIN, "hk_sub_routing_key")
        self.sub_hk_ex = cfg.get(MAIN, "sub_hk_exchange")
        self.sub_hk_q = cfg.get(MAIN, "sub_hk_routing_key")
        
        firebase = self.get_firebase()
        self.db = firebase.database()
        
        #-------
        #for test
        self.start_upload_to_firebase(self.db)
        self.log.logwrite(self.iam, INFO, "Uploaded " + ti.strftime("%Y-%m-%d %H:%M:%S"))
        #-------
        
        self.connect_to_server_hk_ex()  #when error occurs!
        self.connect_to_server_hk_q()
        
    
    def __del__(self):
        self.exit()
        
        
    def exit(self):
        print("Closing %s" % self.iam)
        
        for th in threading.enumerate():
            print(th.name + " exit.")
                        

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
    

    def start_upload_to_firebase(self, db):

        HK_dict = self.read_item_to_upload()
        if HK_dict is None:
            self.log.logwrite(self.iam, WARNING, "No data ")

        else:
            HK_dict["utc_upload"] = datetime.datetime.now(pytz.utc).isoformat()                
            self.push_hk_entry(db, HK_dict)
            self.log.logwrite(self.iam, INFO, HK_dict)


    def read_item_to_upload(self):
        HK_list = open(HKLogPath).read().split()
        # print(len(HK_list), len(FieldNames))

        if len(HK_list) != len(FieldNames):
            return None

        HK_dict = dict((k, t(v)) for (k, t), v in zip(FieldNames, HK_list))

        HK_dict["datetime"] = HK_dict["date"] + "T" + HK_dict["time"] + "+00:00"

        return HK_dict
    
    
    def push_hk_entry(self, db, entry):
        db.child("BasicHK").push(entry)
        
        
    #-------------------------------
    # sub -> hk    
    def connect_to_server_hk_ex(self):
        # RabbitMQ connect        
        self.connection_hk_ex, self.channel_hk_ex = serv.connect_to_server(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_hk_ex:
            # RabbitMQ: define producer
            serv.define_producer(self.iam, self.channel_hk_ex, "direct", self.sub_hk_ex)
        
        
    def send_message_to_hk(self, message):
        serv.send_message(self.iam, TARGET, self.channel_hk_ex, self.sub_hk_ex, self.sub_hk_q, message)    

                  
            
    #-------------------------------
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.connection_hk_q, self.channel_hk_q = serv.connect_to_server(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd)

        if self.connection_hk_q:
            # RabbitMQ: define consumer
            self.queue_hk = serv.define_consumer(self.iam, self.connection_hk_q, "direct", self.hk_sub_ex, self.hk_sub_q)

            th = threading.Thread(target=self.consumer_hk)
            th.start()
            
            
    # RabbitMQ communication    
    def consumer_hk(self):
        try:
            self.connection_hk_q.basic_consume(queue=self.queue_hk, on_message_callback=self.callback_hk, auto_ack=True)
            self.connection_hk_q.start_consuming()
        except Exception as e:
            if self.connection_hk_q:
                self.log.logwrite(self.iam, ERROR, "The communication of server was disconnected!")
                
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.logwrite(self.iam, INFO, msg)

        param = cmd.split()

        if param[0] == HK_REQ_UPLOAD_DB:
            self.start_upload_to_firebase(self.db)
            tm = ti.localtime()
            self.log.logwrite(self.iam, INFO, "Uploaded " + ti.strftime("%Y-%m-%d %H:%M:%S"))
            
        elif param[0] == HK_REQ_EXIT:
            self.exit()


if __name__ == "__main__":
    
    fb = uploader()
    
    
    
    
