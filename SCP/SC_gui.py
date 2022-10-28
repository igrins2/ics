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

from SC_core import *
#import Libs.ics_server as serv

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
        
        self.e_boxsize.setText("64")
        self.label_cur_cursor.setText("( 1024 , 1024 )")
        self.label_ROI_center.setText(" (1024 , 1024 )")
        self.e_exptime.setText("1.63")
        self.e_FS_number.setText("1")
        self.e_repeat_number.setText("1")
        
        self.label_prog_stats.setText("idle")
        self.label_prog_time.setText("---")
        self.label_prog_elapsed.setText("0.0 sec")
        
        today = ti.strftime("%04Y%02m%02d", ti.localtime())
        self.e_savepath.setText(self.sc.fits_path + today)
        self.cur_frame = 0
        filename = "sc_%04d.fits" % self.cur_frame
        self.e_savefilename.setText(filename)
        
        self.label_zscale_range.setText("0 ~ 1000")
        self.e_mscale_min.setText("1000")
        self.e_mscale_max.setText("5000")
        
        self.timer_alive = QTimer(self)
        self.timer_alive.setInterval(self.sc.alive_chk_interval * 1000) 
        self.timer_alive.timeout.connect(self.alive_check)
        
        self.fowler_exp = 0.0       # need to cal
    
        
        self.sc.initialize2()     
        
        
        
    def closeEvent(self, *args, **kwargs):
        self.timer_alive.stop()
        
        print("Closing %s : " % sys.argv[0])
        
        for th in threading.enumerate():
            print(th.name + " exit.")
            
        if self.queue:
            self.channel.stop_consuming()
            self.connection.close()
        
        return QMainWindow.closeEvent(self, *args, **kwargs)
    
    
    def init_events(self):
        self.e_boxsize.setEnabled(False)
        self.bt_ROI_SET.setEnabled(False)
        
        self.e_exptime.setEnabled(False)
        self.e_FS_number.setEnabled(False)
        
        self.bt_acquisition.setEnabled(False)
        self.bt_stop.setEnabled(False)
        self.e_repeat_number.setEnabled(False)
        
        self.bt_acquisition.clicked.connect(self.single_exposure)   
        self.bt_stop.clicked.connect(self.stop_acquisition)
        
        self.bt_save.clicked.connect(self.save_fits)
        self.bt_path.clicked.connect(self.open_path)
        
        self.radioButton_zscale.clicked.connect(self.auto_scale)
        self.bt_scale_apply.clicked.connect(self.scale_apply)
        
    
    def connect_to_server(self):
        # RabbitMQ connect        
        self.connection, self.channel = serv.connect_to_server(TITLE, self.sc.ics_ip_addr, self.sc.ics_id, self.sc.ics_pwd)

        if self.connection:
            # RabbitMQ: define consumer
            self.queue = serv.define_consumer(TITLE, self.channel, self.sc.dcs_ex, "direct", self.sc.dcs_q)
    
            th = threading.Thread(target=self.consumer)
            th.start()
            #th.join()
            
            self.timer_alive.start()
            
            
            
    
    # RabbitMQ communication    
    def consumer(self):
        try:
            self.channel.basic_consume(queue=self.queue,on_message_callback=self.callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            if self.channel:
                self.sc.logwrite(BOTH, "The communication of server was disconnected!")


    def alive_check(self):
        self.sc.alive_check()
        
        self.dcss_sts = False
        timer = QTimer(self)
        timer.singleShot(self.sc.alive_check_interval*1000/2, self.show_alarm)
        

    def callback(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        print(msg)     

        '''    
        elif cmd == CMD_SETFSMODE + " OK":            
            self.e_exptime.setEnabled(True)
            self.e_FS_number.setEnabled(True)
        
            self.bt_acquisition.setEnabled(True)
            self.bt_stop.setEnabled(False)
            self.e_repeat_number.setEnabled(True)
            
        elif cmd == CMD_SETFSPARAM + " OK":
            self.sc.acquireramp()
            
        elif cmd == CMD_ACQUIRERAMP + " OK":
            print(CMD_ACQUIRERAMP, "OK") # for test
            #show image!!!
        
        elif cmd == CMD_STOPACQUISITION + " OK":
            print(CMD_STOPACQUISITION, "OK") # for test
        '''
            
            
            
    def show_alarm(self):
        textcolor = "black"
        if self.dcss_sts == True:
            textcolor = "green"
            self.label_dcss_sts.setText("Connected")
        else:
            textcolor = "red"
            self.label_dcss_sts.setText("Disconnected")
        
        label = "QLabel {color:%s}" % textcolor
        self.label_dcss_sts.setStyleSheet(label)
    
     
    def init_detector(self):
        self.sc.initialize2()    
        
    #---------------------------------
    # buttons
    def single_exposure(self):
        #calculate!!!! self.fowler_exp from self.e_exptime
        self.sc.set_fs_param(1, 1, 1, self.e_exptime, 1)
        
        self.bt_acquisition.setEnabled(False)
        self.bt_stop.setEnabled(True)    
    
    
    def stop_acquisition(self):
        self.sc.send_message(self.simulation_mode, CMD_STOPACQUISITION)
        
        self.bt_acquisition.setEnabled(True)
        self.bt_stop.setEnabled(False)
        
    
    def save_fits(self, filename):
        pass
    
    def open_path(self):
        pass
    
    def auto_scale(self):
        pass
    
    def scale_apply(self):
        pass    
    
    #---------------------------------
        
    
    
    
    
    
    
            
    
    
        
        
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    
    app = QApplication(sys.argv)
        
    sc = MainWindow()
    sc.show()
        
    app.exec()