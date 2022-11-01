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
from Libs.logger import *

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
        
        self.simulation_mode = True     #from EngTools
        self.output_channel = 32
           
        self.MQserver_connect_retry()
        
        
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
        
        self.bt_MQserver_retry.setEnabled(False)
        self.bt_MQserver_retry.clicked.connect(self.MQserver_connect_retry)
        
        self.bt_DCSS_check_stop.setEnabled(False)
        self.bt_DCSS_check.clicked.connect(lambda: self.DCSS_check(True))
        self.bt_DCSS_check_stop.clicked.connect(lambda: self.DCSS_check(False))
        self.bt_DCSS_init.clicked.connect(self.init)
        self.label_mode.setText("---")
        
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
        
        
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # sc -> main
    def connect_to_server_sc_ex(self):
        # RabbitMQ connect        
        self.connection_sc_ex, self.channel_sc_ex = serv.connect_to_server(IAM, self.sc.ics_ip_addr, self.sc.ics_id, self.sc.ics_pwd)

        if self.connection_sc_ex:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_sc_ex, "direct", self.sc.sc_main_ex)
        else:
            self.bt_MQserver_retry.setEnabled(True)
        
        
    def send_message_to_sc(self, message):
        serv.send_message(IAM, TARGET, self.channel_sc_ex, self.sc.sc_main_ex, self.sc.sc_main_q, message)
            
            
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # main -> sc
    def connect_to_server_main_q(self):
        # RabbitMQ connect
        self.connection_main_q, self.channel_main_q = serv.connect_to_server(IAM, self.sc.ics_ip_addr, self.sc.ics_id, self.sc.ics_pwd)

        if self.connection_main_q:
            
            if self.label_MQserver_sts.text() == "---":
                self.label_MQserver_sts.setText("main")
            else:
                txt = self.label_MQserver_sts.text()
                self.label_MQserver_sts.setText(txt + "/main")
                
            # RabbitMQ: define consumer
            self.queue_main = serv.define_consumer(IAM, self.connection_main_q, "direct", self.sc.main_sc_ex, self.sc.main_sc_q)

            th = threading.Thread(target=self.consumer_main)
            th.start()
        else:
            self.bt_MQserver_retry.setEnabled(True)
            
            
    # RabbitMQ communication    
    def consumer_main(self):
        try:
            self.connection_main_q.basic_consume(queue=self.queue_main, on_message_callback=self.callback_main, auto_ack=True)
            self.connection_main_q.start_consuming()
        except Exception as e:
            if self.connection_main_q:
                self.sc.logwrite(ERROR, "The communication of server was disconnected!")
                
    
    def callback_main(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.sc.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == CMD_SIMULATION:
            self.simulation_mode = int(param[1])
            if self.simulation_mode:
                self.label_mode.setText("Simulation")
            else:
                self.label_mode.setText("Reality")
                
            
            
            
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # dcss -> sc
    def connect_to_server_ics_q(self):
        # RabbitMQ connect
        self.connection_ics_q, self.channel_ics_q = serv.connect_to_server(IAM, self.sc.ics_ip_addr, self.sc.ics_id, self.sc.ics_pwd)

        if self.connection_ics_q:
            
            if self.label_MQserver_sts.text() == "---":
                self.label_MQserver_sts.setText("dcss")
            else:
                txt = self.label_MQserver_sts.text()
                self.label_MQserver_sts.setText(txt + "/dcss")
                
            # RabbitMQ: define consumer
            self.queue_ics = serv.define_consumer(IAM, self.channel_ics_q, "direct", self.sc.dcs_ex, self.sc.dcs_q)

            th = threading.Thread(target=self.consumer_ics)
            th.start()
                
        else:
            self.bt_MQserver_retry.setEnabled(True)
                        
            
    # RabbitMQ communication    
    def consumer_ics(self):
        try:
            self.channel_ics_q.basic_consume(queue=self.queue_ics, on_message_callback=self.callback_ics, auto_ack=True)
            self.channel_ics_q.start_consuming()
        except Exception as e:
            if self.channel_ics_q:
                self.sc.logwrite(ERROR, "The communication of server was disconnected!")


    def alive_check(self):
        self.sc.alive_check()
        
        self.dcss_sts = False
        timer = QTimer(self)
        timer.singleShot(self.sc.alive_check_interval*1000/2, self.show_alarm)
        

    def callback_ics(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.sc.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == "alive":
            self.dcss_sts = True  
        
        elif param[0] == CMD_INITIALIZE2:
            #downloadMCD
            self.sc.downloadMCD(self.simulation_mode)
            
        elif param[0] == CMD_DOWNLOAD:
            #setdetector
            self.sc.set_detector(self.simulation_mode, MUX_TYPE, self.output_channel)
            
        elif param[0] == CMD_SETDETECTOR:
            self.bt_DCSS_init.setEnabled(False)
            
        elif param[0] == CMD_SETFSPARAM:
            #acquire
            self.sc.acquireramp(self.simulation_mode, self.ROI_mode)

        elif param[0] == CMD_ACQUIRERAMP:
            pass
        
        elif param[0] == CMD_STOPACQUISITION:
            pass
            
            
    def show_alarm(self):
        textcolor = "black"
        if self.dcss_sts == True:
            textcolor = "green"
            self.label_dcss_sts.setText("Connected")
            self.dcss_sts = False
        else:
            textcolor = "red"
            self.label_dcss_sts.setText("Disconnected")
        
        label = "QLabel {color:%s}" % textcolor
        self.label_dcss_sts.setStyleSheet(label)
            
    #---------------------------------
    # buttons
    
    def MQserver_connect_retry(self):
        self.connect_to_server_sc_ex()
        self.connect_to_server_main_q()
        self.connect_to_server_ics_q()
        self.sc.connect_to_server_ics_ex()        
        
        
    def DCSS_check(self, start):
        if start:
            self.timer_alive.start()
            self.bt_DCSS_check.setEnabled(False)
            self.bt_DCSS_check_stop.setEnabled(True)
        else:
            self.timer_alive.stop()
            self.bt_DCSS_check.setEnabled(True)
            self.bt_DCSS_check_stop.setEnabled(False)
        
        
    def init(self):
        self.sc.initialize2(self.simulation_mode) 
        
        
    def single_exposure(self):
        #calculate!!!! self.fowler_exp from self.e_exptime
        self.sc.set_fs_param(self.simulation_mode, self.e_exptime)
        
        self.bt_acquisition.setEnabled(False)
        self.bt_stop.setEnabled(True)    
    
    
    def stop_acquisition(self):
        self.sc.stop_acquistion(self.simulation_mode)
        
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