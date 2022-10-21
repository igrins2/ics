# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Jun 28, 2022

@author: hilee
"""

import sys
from ui_SCP import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Libs.rabbitmq_server import *
from SC_core import *

import time as ti
import threading

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Slit Camera Package 0.1")
        
        
        self.sc = SC()
        
        self.init_events()
        
        self.label_dcss_sts.setText("Disconnected")
        self.dcss_sts = False
        
        self.e_exptime.setText("1.63")
        self.e_FS_number.setText("1")
        self.e_repeat_number.setText("1")
        
        self.label_prog_stats.setText("idle")
        self.label_prog_time.setText("---")
        self.label_prog_elapsed.setText("0.0 sec")
        
        today = ti.strftime("/%04Y%02m%02d", ti.localtime())
        self.e_savepath.setText(self.sc.fits_path + today)
        self.cur_frame = 0
        filename = "sc_%04d.fits" % self.cur_frame
        self.e_savefilename.setText(filename)
        
        self.label_zscale_range.setText("0 ~ 1000")
        self.e_mscale_min.setText("1000")
        self.e_mscale_max.setText("5000")
        
        self.connect_to_server()
        
        self.init_detector()
        
        self.fowler_exp = 0.0       # need to cal
        
        
        
    def closeEvent(self, *args, **kwargs):
        print("Closing %s : " % sys.argv[0])
        
        for th in threading.enumerate():
            print(th.name + " exit.")
            
        if self.queue:
            self.channel.stop_consuming()
            self.connection.close()
        
        return QMainWindow.closeEvent(self, *args, **kwargs)
    
    
    def init_events(self):
        self.bt_acquisition.clicked.connect(self.single_exposure)   
        self.bt_stop.clicked.connect(self.stop_acquisition)
        
        self.bt_save.clicked.connect(self.save_fits)
        self.bt_path.clicked.connect(self.open_path)
        
        self.radioButton_zscale.clicked.connect(self.auto_scale)
        self.bt_scale_apply.clicked.connect(self.scale_apply)
        
    
    def connect_to_server(self):
        # RabbitMQ connect
        self.serv = ICS_SERVER(self.sc.ics_ip_addr, self.sc.ics_id, self.sc.ics_pwd, self.sc.ics_ex, self.sc.ics_q, "direct", self.sc.dcs_ex, self.sc.dcs_q)
        self.connection, self.channel = self.serv.connect_to_server(TITLE)

        if self.connection:
            # RabbitMQ: define consumer
            self.queue = self.serv.define_consumer(self.channel, TITLE)
    
            th = threading.Thread(target=self.consumer)
            th.start()
            #th.join()

            self.show_alarm()
            
    
    # RabbitMQ communication    
    def consumer(self):
        try:
            self.channel.basic_consume(queue=self.queue,on_message_callback=self.callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            if self.channel:
                self.sc.logwrite(BOTH, "The communication of server was disconnected!")


    def callback(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        print(msg)

        if cmd == "alive?":
            self.dcss_sts = True
            self.sc.send_message("alive")  
        
        elif cmd == CMD_INITIALIZE2 + " OK":
            self.sc.send_message(CMD_DOWNLOAD)
            
        elif cmd == CMD_DOWNLOAD + " OK":
            self.sc.send_message(CMD_SETDETECTOR)
            
        elif cmd == CMD_SETDETECTOR + " OK":
            self.sc.send_message(CMD_SETFSMODE + " 1")
            
        elif cmd == CMD_SETFSMODE + " OK":
            print(CMD_SETFSMODE, "OK") # for test
            
        elif cmd == CMD_SETFSPARAM + " OK":
            self.sc.send_message(CMD_ACQUIRERAMP)
            
        elif cmd == CMD_ACQUIRERAMP + " OK":
            print(CMD_ACQUIRERAMP, "OK") # for test
        
        elif cmd == CMD_STOPACQUISITION + " OK":
            print(CMD_STOPACQUISITION, "OK") # for test
            
            
            
    def show_alarm(self):
        textcolor = "black"
        if self.dcss_sts == True:
            textcolor = "green"
        else:
            textcolor = "red"
        
        label = "QLabel {color:%s}" % textcolor
        self.label_dcss_sts.setStyleSheet(label)

        self.dcss_sts = False
        timer = QTimer(self)
        timer.singleShot(180*1000, self.show_alarm)  #after 180sec
     
        
        
    #---------------------------------
    # buttons
    def single_exposure(self):
        param = " 1 1 1 %f 1" % self.fowler_exp
        self.sc.send_message(CMD_SETFSPARAM + param)        
    
    def stop_acquisition(self):
        self.sc.send_message(CMD_STOPACQUISITION)
    
    def save_fits(self, filename):
        pass
    
    def open_path(self):
        pass
    
    def auto_scale(self):
        pass
    
    def scale_apply(self):
        pass    
    
    #---------------------------------
        
    def init_detector(self):
        self.sc.initialize2()
    
    
    
    
    
            
    
    
        
        
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    
    app = QApplication(sys.argv)
        
    sc = MainWindow()
    sc.show()
        
    app.exec_()