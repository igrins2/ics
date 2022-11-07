# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Non 7, 2022

@author: hilee
"""

import sys, os

from pytest import PytestAssertRewriteWarning
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from ui_DTP import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from DT_core import *
from Libs.logger import *

import time as ti
import threading
import math

import numpy as np
import astropy.io.fits as fits 
import Libs.zscale as zs
import qimage2ndarray

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Data Taking Package 0.1")
        
        self.dt = DT()
        
        self.init_events()
        
        self.label_dcsh_sts.setText("Disconnected")
        self.label_dcsk_sts.setText("Disconnected")
        self.dcs_sts = [False, False]
        self.label_mode.setText("---")
        
        self.e_exptimeH.setText("1.63")
        self.e_FSnumberH.setText("1")
        self.e_repeatH.setText("1")
        
        self.e_exptimeK.setText("1.63")
        self.e_FSnumberK.setText("1")
        self.e_repeatK.setText("1")
        
        self.label_prog_sts_H.setText("idle")
        self.label_prog_time_H.setText("---")
        self.label_prog_elapsed_H.setText("0.0 sec")
        
        self.label_prog_sts_K.setText("idle")
        self.label_prog_time_K.setText("---")
        self.label_prog_elapsed_K.setText("0.0 sec")
        
        today = ti.strftime("%04Y%02m%02d", ti.localtime())
        self.e_path.setText(self.dt.fits_path + today)
        self.cur_frame = 0
        filename = "dcsh_%04d.fits" % self.cur_frame
        self.e_filename_H.setText(filename)
        filename = "dcsk_%04d.fits" % self.cur_frame
        self.e_filename_K.setText(filename)
        
        self.cal_chk = [self.chk_dark, self.chk_flat_on, self.chk_flat_off, self.chk_ThAr, self.chk_pinhole_flat, self.chk_pinhole_ThAr, self.chk_USAF_on, self.chk_USAF_off, self.chk_parking]
        
        self.cal_e_exptime = [self.e_dark_exptime, self.e_flaton_exptime, self.e_flatoff_exptime, self.e_ThAr_exptime, self.e_pinholeflat_exptime, self.e_pinholeThAr_exptime, self.e_USAFon_exptime, self.e_USAFoff_exptime, self.e_parking_exptime]
        
        self.cal_e_repeat = [self.e_dark_repeat, self.e_flaton_repeat, self.e_flatoff_repeat, self.e_ThAr_repeat, self.e_pinholeflat_repeat, self.e_pinholeThAr_repeat, self.e_USAFon_repeat, self.e_USAFoff_repeat, self.e_parking_repeat]
        
        for i in range(CAL_CNT):
            self.cal_e_exptime[i].setText("1.63")
            self.cal_e_repeat[i].setText("1")
        
        self.e_utpos.setText("1")
        self.e_ltpos.setText("1")
        
        self.e_movinginterval.setText("1")        
        
        self.simulation_mode = True     #from EngTools
        
        self.cal_mode = False
        
        self.acquiring_h = False
        self.acquiring_k = False
        
        self.connection_ics_q = [None, None]
        self.channel_ics_q = [None, None]
        self.queue_ics = [None, None]
        
        self.timer_alive = [None, None]
        self.timer_alive[DCSH] = QTimer(self)
        self.timer_alive[DCSH].setInterval(self.dt.alive_chk_interval * 1000) 
        self.timer_alive[DCSH].timeout.connect(self.alive_check_h)  
        
        self.timer_alive[DCSK] = QTimer(self)
        self.timer_alive[DCSK].setInterval(self.dt.alive_chk_interval * 1000) 
        self.timer_alive[DCSK].timeout.connect(self.alive_check_k)      
        
        self.img = [None, None]
        
        self.cal_cur = 0
           
        for i in range(CAL_CNT):
            self.cal_use_parsing(self.cal_chk[i], self.cal_e_exptime[i], self.cal_e_repeat[i])
        
        self.MQserver_connect_retry()
        
        
        
    def init_events(self):
        self.bt_MQserver_retry.setEnabled(False)
        self.bt_MQserver_retry.clicked.connect(self.MQserver_connect_retry)
        
        self.bt_DCSH_check_stop.setEnabled(False)
        self.bt_DCSH_check.clicked.connect(lambda: self.DCS_monit(DCSH, True))
        self.bt_DCSH_check_stop.clicked.connect(lambda: self.DCS_monit(DCSH, False))
        self.bt_DCSH_init.clicked.connect(lambda: self.init(DCSH))
        
        self.bt_DCSK_check_stop.setEnabled(False)
        self.bt_DCSK_check.clicked.connect(lambda: self.DCS_monit(DCSK, True))
        self.bt_DCSK_check_stop.clicked.connect(lambda: self.DCS_monit(DCSK, False))
        self.bt_DCSK_init.clicked.connect(lambda: self.init(DCSK))
        
        self.label_mode.setText("---")
        
        self.radioButton_sync.setChecked(True)
        
        self.e_exptimeH.setEnabled(False)
        self.e_FSnumberH.setEnabled(False)
        self.e_repeatH.setEnabled(False)
        
        self.e_exptimeK.setEnabled(False)
        self.e_FSnumberK.setEnabled(False)
        self.e_repeatK.setEnabled(False)
        
        #for test
        #self.bt_acquisition.setEnabled(False)
        self.bt_abort.setEnabled(False)
        
        self.bt_acquisition.clicked.connect(self.single_exposure)   
        self.bt_abort.clicked.connect(self.stop_acquisition)
        
        self.bt_save.clicked.connect(self.save_fits)
        self.bt_path.clicked.connect(self.open_path)
        
        #------------------
        #calibration
        self.chk_whole.clicked.connect(self.cal_whole_check)
        self.bt_run.clicked.connect(self.cal_run)
        
        self.bt_ut_motor_init.clicked.connect(lambda: self.motor_init(UT))
        self.bt_lt_motor_init.clicked.connect(lambda: self.motor_init(LT))
                
        #for i in range(CAL_CNT):
        self.chk_dark.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[0], self.cal_e_exptime[0], self.cal_e_repeat[0]))
        self.chk_flat_on.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[1], self.cal_e_exptime[1], self.cal_e_repeat[1]))
        self.chk_flat_off.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[2], self.cal_e_exptime[2], self.cal_e_repeat[2]))
        self.chk_ThAr.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[3], self.cal_e_exptime[3], self.cal_e_repeat[3]))
        self.chk_pinhole_flat.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[4], self.cal_e_exptime[4], self.cal_e_repeat[4]))
        self.chk_pinhole_ThAr.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[5], self.cal_e_exptime[5], self.cal_e_repeat[5]))
        self.chk_USAF_on.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[6], self.cal_e_exptime[6], self.cal_e_repeat[6]))
        self.chk_USAF_off.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[7], self.cal_e_exptime[7], self.cal_e_repeat[7]))
        self.chk_parking.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[8], self.cal_e_exptime[8], self.cal_e_repeat[8]))
        
        self.bt_utpos_prev.clicked.connect(lambda: self.motor_move(UT, PREV))
        self.bt_utpos_next.clicked.connect(lambda: self.motor_move(UT, NEXT))
        
        self.bt_utpos_set1.clicked.connect(lambda: self.motor_pos_set(UT, 1))
        self.bt_utpos_set2.clicked.connect(lambda: self.motor_pos_set(UT, 2))
        
        self.bt_ltpos_prev.clicked.connect(lambda: self.motor_move(LT, PREV))
        self.bt_ltpos_next.clicked.connect(lambda: self.motor_move(LT, NEXT))
        
        self.bt_ltpos_set1.clicked.connect(lambda: self.motor_pos_set(LT, 1))
        self.bt_ltpos_set2.clicked.connect(lambda: self.motor_pos_set(LT, 2))
        self.bt_ltpos_set3.clicked.connect(lambda: self.motor_pos_set(LT, 3))
        self.bt_ltpos_set4.clicked.connect(lambda: self.motor_pos_set(LT, 4))
        
        self.bt_utpos_prev.setEnabled(False)
        self.e_utpos.setEnabled(False)
        self.bt_utpos_next.setEnabled(False)
                
        self.bt_utpos_set1.setEnabled(False)
        self.bt_utpos_set2.setEnabled(False)
                
        self.bt_ltpos_prev.setEnabled(False)
        self.e_ltpos.setEnabled(False)
        self.bt_ltpos_next.setEnabled(False)
                
        self.bt_ltpos_set1.setEnabled(False)
        self.bt_ltpos_set2.setEnabled(False)
        self.bt_ltpos_set3.setEnabled(False)
        self.bt_ltpos_set4.setEnabled(False)
        
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # dt -> main
    def connect_to_server_to_main_ex(self):
        # RabbitMQ connect        
        self.connection_to_main_ex, self.channel_to_main_ex = serv.connect_to_server(IAM, self.dt.ics_ip_addr, self.dt.ics_id, self.dt.ics_pwd)

        if self.connection_to_main_ex:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_to_main_ex, "direct", self.dt.dt_main_ex)
        else:
            self.bt_MQserver_retry.setEnabled(True)
        
        
    def send_message_to_main(self, message):
        serv.send_message(IAM, MAIN, self.channel_et_ex, self.dt.dt_main_ex, self.dt.dt_main_q, message)
        
        
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # main -> dt
    def connect_to_server_to_main_q(self):
        # RabbitMQ connect
        self.connection_main_q, self.channel_main_q = serv.connect_to_server(IAM, self.dt.ics_ip_addr, self.dt.ics_id, self.dt.ics_pwd)

        if self.connection_main_q:
            
            if self.label_MQserver_sts.text() == "---":
                self.label_MQserver_sts.setText("main")
            else:
                txt = self.label_MQserver_sts.text()
                self.label_MQserver_sts.setText(txt + "/main")
                
            # RabbitMQ: define consumer
            self.queue_main = serv.define_consumer(IAM, self.connection_main_q, "direct", self.dt.main_dt_ex, self.dt.main_dt_q)

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
                self.dt.logwrite(ERROR, "The communication of server was disconnected!")
                
    
    def callback_main(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.dt.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == CMD_SIMULATION:
            self.simulation_mode = int(param[1])
            if self.simulation_mode:
                self.label_mode.setText("Simulation")
            else:
                self.label_mode.setText("Reality")
                
                
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # dt -> hk
    def connect_to_server_to_hk_ex(self):
        # RabbitMQ connect        
        self.connection_dt_ex, self.channel_dt_ex = serv.connect_to_server(IAM, self.dt.ics_ip_addr, self.dt.ics_id, self.dt.ics_pwd)

        if self.connection_dt_ex:
            # RabbitMQ: define producer
            serv.define_producer(IAM, self.channel_dt_ex, "direct", self.dt.dt_hk_ex)
        else:
            self.bt_MQserver_retry.setEnabled(True)
        
        
    def send_message_to_hk(self, message):
        serv.send_message(IAM, MAIN, self.channel_dt_ex, self.dt.dt_hk_ex, self.dt.dt_hk_q, message)
                
                
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # hk -> dt
    def connect_to_server_to_hk_q(self):
        # RabbitMQ connect
        self.connection_hk_q, self.channel_hk_q = serv.connect_to_server(IAM, self.dt.ics_ip_addr, self.dt.ics_id, self.dt.ics_pwd)

        if self.connection_hk_q:
            
            if self.label_MQserver_sts.text() == "---":
                self.label_MQserver_sts.setText("hk")
            else:
                txt = self.label_MQserver_sts.text()
                self.label_MQserver_sts.setText(txt + "/hk")
                
            # RabbitMQ: define consumer
            self.queue_hk = serv.define_consumer(IAM, self.connection_hk_q, "direct", self.dt.hk_dt_ex, self.dt.hk_dt_q)

            th = threading.Thread(target=self.consumer_hk)
            th.start()
        else:
            self.bt_MQserver_retry.setEnabled(True)
            
            
    # RabbitMQ communication    
    def consumer_hk(self):
        try:
            self.connection_hk_q.basic_consume(queue=self.queue_hk, on_message_callback=self.callback_main, auto_ack=True)
            self.connection_hk_q.start_consuming()
        except Exception as e:
            if self.connection_hk_q:
                self.dt.logwrite(ERROR, "The communication of server was disconnected!")
                
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.dt.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == HK_FN_INITMOTOR:
            if param[1] == UT:
                self.bt_utpos_prev.setEnabled(True)
                self.bt_utpos_next.setEnabled(True)
                    
                self.bt_utpos_set1.setEnabled(True)
                self.bt_utpos_set2.setEnabled(True)
            elif param[1] == LT:
                self.bt_ltpos_prev.setEnabled(True)
                self.bt_ltpos_next.setEnabled(True)
                        
                self.bt_ltpos_set1.setEnabled(True)
                self.bt_ltpos_set2.setEnabled(True)
                self.bt_ltpos_set3.setEnabled(True)
                self.bt_ltpos_set4.setEnabled(True)
                
        elif param[0] == HK_FN_MOVEMOTOR:
            self.func_lamp(self.cal_cur)
            #start exposure~
        
        elif param[0] == HK_FN_LAMPCHANGE:
            pass
            #start exposure~
            
            
            
                
                
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # dcsh, dcsk -> dt
    def connect_to_server_ics_q(self, dc_idx):
        # RabbitMQ connect
        self.connection_ics_q[dc_idx], self.channel_ics_q[dc_idx] = serv.connect_to_server(IAM, self.dt.ics_ip_addr, self.dt.ics_id, self.dt.ics_pwd)

        if self.connection_ics_q[dc_idx]:
            
            if self.label_MQserver_sts.text() == "---":
                if dc_idx == DCSH:
                    self.label_MQserver_sts.setText("dcsh")
                else:
                    self.label_MQserver_sts.setText("dcsk")
            else:
                txt = self.label_MQserver_sts.text()
                if dc_idx == DCSH:
                    self.label_MQserver_sts.setText(txt + "/dcsh")
                else:
                    self.label_MQserver_sts.setText(txt + "/dcsk")
                
            # RabbitMQ: define consumer
            self.queue_ics[dc_idx] = serv.define_consumer(IAM, self.channel_ics_q[dc_idx], "direct", self.dt.dcs_ex[dc_idx], self.dt.dcs_q[dc_idx])

            th = threading.Thread(target=lambda: self.consumer_ics(dc_idx))
            th.start()
                
        else:
            self.bt_MQserver_retry.setEnabled(True)
                        
            
    # RabbitMQ communication    
    def consumer_ics(self, dc_idx):
        if dc_idx == DCSH:
            try:
                self.channel_ics_q[dc_idx].basic_consume(queue=self.queue_ics[dc_idx], on_message_callback=self.callback_ics_h, auto_ack=True)
                self.channel_ics_q[dc_idx].start_consuming()
            except Exception as e:
                if self.channel_ics_q[dc_idx]:
                    self.dt.logwrite(ERROR, "The communication of server was disconnected!")
        else:
            try:
                self.channel_ics_q[dc_idx].basic_consume(queue=self.queue_ics[dc_idx], on_message_callback=self.callback_ics_k, auto_ack=True)
                self.channel_ics_q[dc_idx].start_consuming()
            except Exception as e:
                if self.channel_ics_q[dc_idx]:
                    self.dt.logwrite(ERROR, "The communication of server was disconnected!")


    def alive_check_h(self):
        self.dt.alive_check(DCSH)
        
        self.dcs_sts[DCSH] = False
        timer = QTimer(self)
        timer.singleShot(self.dt.alive_chk_interval*1000/2, self.show_alarm_h)
        
    def alive_check_k(self):
        self.dt.alive_check(DCSK)
        
        self.dcs_sts[DCSK] = False
        timer = QTimer(self)
        timer.singleShot(self.dt.alive_chk_interval*1000/2, self.show_alarm_k)
        

    def callback_ics_h(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.dt.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == "alive":
            self.dcs_sts[DCSH] = True  
        
        elif param[0] == CMD_INITIALIZE2:
            #downloadMCD
            self.dt.downloadMCD(DCSH, self.simulation_mode)
            
        elif param[0] == CMD_DOWNLOAD:
            #setdetector
            self.dt.set_detector(DCSH, self.simulation_mode, MUX_TYPE, self.output_channel)
            
        elif param[0] == CMD_SETDETECTOR:
            self.bt_DCSH_init.setEnabled(False)
            
            self.e_exptimeH.setEnabled(True)
            self.e_FSnumberH.setEnabled(True)
        
            self.bt_acquisition.setEnabled(True)
            self.bt_abort.setEnabled(True)
            self.e_repeatH.setEnabled(True)            
            
        elif param[0] == CMD_SETFSPARAM:
            #acquire
            self.acquiring_h = True
            self.dt.acquireramp(DCSH, self.simulation_mode)

        elif param[0] == CMD_ACQUIRERAMP:
            # load data
            self.load_data()
            
            self.acquiring_h = False
            
            if self.acquiring_k == False and self.cal_mode:
                self.cal_run_cycle()
        
        elif param[0] == CMD_STOPACQUISITION:
            pass
        
        
    def callback_ics_k(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.dt.logwrite(INFO, msg)

        param = cmd.split()

        if param[0] == "alive":
            self.dcs_sts[DCSK] = True  
        
        elif param[0] == CMD_INITIALIZE2:
            #downloadMCD
            self.dt.downloadMCD(DCSK, self.simulation_mode)
            
        elif param[0] == CMD_DOWNLOAD:
            #setdetector
            self.dt.set_detector(DCSK, self.simulation_mode, MUX_TYPE, self.output_channel)
            
        elif param[0] == CMD_SETDETECTOR:
            self.bt_DCSK_init.setEnabled(False)
            
            self.e_exptimeK.setEnabled(True)
            self.e_FSnumberK.setEnabled(True)
        
            self.bt_acquisition.setEnabled(True)
            self.bt_abort.setEnabled(True)
            self.e_repeatK.setEnabled(True)            
            
        elif param[0] == CMD_SETFSPARAM:
            #acquire
            self.acquiring_k = True
            self.dt.acquireramp(DCSK, self.simulation_mode)

        elif param[0] == CMD_ACQUIRERAMP:
            # load data
            self.load_data()
            
            self.acquiring_k = False
            
            if self.acquiring_h == False and self.cal_mode:
                self.cal_run_cycle()
        
        elif param[0] == CMD_STOPACQUISITION:
            pass
            
            
    def show_alarm_h(self):
        textcolor = "black"
        if self.dcs_sts[DCSH] == True:
            textcolor = "green"
            self.label_dcsh_sts.setText("Connected")
            self.dcs_sts[DCSH] = False
        else:
            textcolor = "red"
            self.label_dcsh_sts.setText("Disconnected")
        
        label = "QLabel {color:%s}" % textcolor
        self.label_dcsh_sts.setStyleSheet(label)
            
            
    def show_alarm_k(self):
        textcolor = "black"
        if self.dcs_sts[DCSK] == True:
            textcolor = "green"
            self.label_dcsk_sts.setText("Connected")
            self.dcs_sts[DCSK] = False
        else:
            textcolor = "red"
            self.label_dcsk_sts.setText("Disconnected")
        
        label = "QLabel {color:%s}" % textcolor
        self.label_dcsk_sts.setStyleSheet(label)
        
        
    def load_data(self, ics_idx):
        filepath = ""
        if self.simulation_mode:
            if ics_idx == DCSH:
                filepath = WORKING_DIR + "IGRINS/demo/dt/SDCH_demo.fits"
            else:
                filepath = WORKING_DIR + "IGRINS/demo/dt/SDCK_demo.fits"
        
        frm = fits.open(filepath)
        data = frm[0].data
        header = frm[0].header
        _img = np.array(data, dtype = "f")
        #_img = np.flipud(np.array(data, dtype = "f"))
        self.img[ics_idx] = _img[0:FRAME_Y, 0:FRAME_X]
        #self.img = _img
        
        self.zmin, self.zmax = zs.zscale(self.img[ics_idx])
        range = "%d ~ %d" % (self.zmin, self.zmax)
                
        self.reload_img(ics_idx)
        
        
    def reload_img(self, ics_idx):   
        
        _img = np.flipud(self.img[ics_idx])
            
        scene = QGraphicsScene(self)
        
        if ics_idx == DCSH:
            scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(_img, (int(self.zmin), int(self.zmax)))).scaled(self.graphicsView_H.width(), self.graphicsView_H.height(), Qt.IgnoreAspectRatio, Qt.FastTransformation))
            self.graphicsView_H.setScene(scene) 
        else:
            scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(_img, (int(self.zmin), int(self.zmax)))).scaled(self.graphicsView_K.width(), self.graphicsView_K.height(), Qt.IgnoreAspectRatio, Qt.FastTransformation))
            self.graphicsView_K.setScene(scene)
        
    #---------------------------------
    # buttons

    def MQserver_connect_retry(self):
        #for with main, local
        self.connect_to_server_to_main_ex()
        self.connect_to_server_to_main_q()
        
        #for hk, local
        self.connect_to_server_to_hk_ex()
        self.connect_to_server_to_hk_q()
        
        #for dcsh, dcsk
        self.dt.connect_to_server_ics_ex(DCSH)        
        self.connect_to_server_ics_q(DCSH)
        self.dt.connect_to_server_ics_ex(DCSK)        
        self.connect_to_server_ics_q(DCSK)
        

    def DCS_monit(self, dc_idx, start):
        if start:
            self.timer_alive[dc_idx].start()
            if dc_idx == DCSH:
                self.bt_DCSH_check.setEnabled(False)
                self.bt_DCSH_check_stop.setEnabled(True)
            else:
                self.bt_DCSK_check.setEnabled(False)
                self.bt_DCSK_check_stop.setEnabled(True)
        else:
            self.timer_alive[dc_idx].stop()
            if dc_idx == DCSH:
                self.bt_DCSH_check.setEnabled(True)
                self.bt_DCSH_check_stop.setEnabled(False)
            else:
                self.bt_DCSK_check.setEnabled(True)
                self.bt_DCSK_check_stop.setEnabled(False)
                


    def init(self, dc_idx):
        self.dt.initialize2(dc_idx, self.simulation_mode) 
        
        
    def single_exposure(self):
        # for test
        if self.radioButton_sync.isChecked() or self.radioButton_H.isChecked():
            self.load_data(DCSH)
        if self.radioButton_sync.isChecked() or self.radioButton_K.isChecked(): 
            self.load_data(DCSK)
        return
    
        #calculate!!!! self.fowler_exp from self.e_exptime
        if self.radioButton_sync.isChecked() or self.radioButton_H.isChecked():
            self.dt.set_fs_param(DCSH, self.simulation_mode, self.e_exptimeH)
        if self.radioButton_sync.isChecked() or self.radioButton_K.isChecked():    
            self.dt.set_fs_param(DCSK, self.simulation_mode, self.e_exptimeK)
        
        self.bt_acquisition.setEnabled(False)
        self.bt_abort.setEnabled(True)  
    
    
    def stop_acquisition(self):
        if self.radioButton_sync.isChecked() or self.radioButton_H.isChecked():
            self.dt.stop_acquistion(DCSH, self.simulation_mode)
        if self.radioButton_sync.isChecked() or self.radioButton_K.isChecked():   
            self.dt.stop_acquistion(DCSK, self.simulation_mode)
        
        self.bt_acquisition.setEnabled(True)
        self.bt_abort.setEnabled(False)
    
    
    def save_fits(self):
        pass
    
    
    def open_path(self):
        pass
    

    
    #-------------------------------------------------
    # calibration
    def cal_whole_check(self):
        check = self.chk_whole.isChecked()
        
        for i in range(CAL_CNT):
            self.cal_chk[i].setChecked(check)
            
            self.cal_use_parsing(self.cal_chk[i], self.cal_e_exptime[i], self.cal_e_repeat[i])


    def cal_use_parsing(self, chkbox, exptime, repeat):
        use = chkbox.isChecked()
        exptime.setEnabled(use)
        repeat.setEnabled(use)
        
        
        
    def cal_run(self):
        
        self.cal_mode = True
        self.cal_cur = 0
        
        self.cal_run_cycle()   
        
            
    def cal_run_cycle(self):
        
        for i in range(self.cal_cur, CAL_CNT):
            if self.cal_chk[i].isChecked():
                self.cal_cur = i
                self.func_motor(i)   #need to check
                break
            
            
    def func_lamp(self, idx):        
        msg = "%s %d %d" % (HK_FN_LAMPCHANGE, FLAT, LAMP_FLAT[idx])
        self.send_message_to_hk(msg)
        msg = "%s %d %d" % (HK_FN_LAMPCHANGE, THAR, LAMP_THAR[idx])
        self.send_message_to_hk(msg)
            
            
    def func_motor(self, idx):
        msg = "%s %d %d" % (HK_FN_MOVEMOTOR, UT, MOTOR_UT[idx])
        self.send_message_to_hk(msg)
        msg = "%s %d %d" % (HK_FN_MOVEMOTOR, LT, MOTOR_LT[idx])
        self.send_message_to_hk(msg)
        
        
        
    
    def motor_init(self, motor):
        msg = "%s %d" % (HK_FN_INITMOTOR, motor)
        self.send_message_to_hk(msg)
            

    def move_motor_delta(self, motor, direction): #motor-UT/LT, direction-prev, next
        if motor == UT:
            if direction == PREV:
                curpos = int(self.e_utpos.text()) - int(self.e_movinginterval.text())
                self.e_utpos.setText(str(curpos))
            else:
                curpos = int(self.e_utpos.text()) + int(self.e_movinginterval.text())
                self.e_utpos.setText(str(curpos))
        else:
            if direction == PREV:
                curpos = int(self.e_ltpos.text()) - int(self.e_movinginterval.text())
                self.e_ltpos.setText(str(curpos))
            else:
                curpos = int(self.e_ltpos.text()) + int(self.e_movinginterval.text())
                self.e_ltpos.setText(str(curpos))
                
        msg = "%s %d %d" % (HK_FN_MOVEMOTORDELTA, motor, direction)
        self.send_message_to_hk(msg)
                
    
    def motor_pos_set(self, motor, position): #motor-UT/LT, direction-UT(1/2), LT(1-4)
        #hkp 
        pass
    
    

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
    app = QApplication(sys.argv)
        
    dt = MainWindow()
    dt.show()
        
    app.exec()