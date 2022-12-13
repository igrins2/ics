# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Dec 8, 2022

@author: hilee
"""

import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_DTP import *
from DT_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import time as ti
import threading

import numpy as np
import astropy.io.fits as fits 
import Libs.zscale as zs
import qimage2ndarray

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        
        self.iam = DT
        
        self.log = LOG(WORKING_DIR + "/IGRINS", MAIN)  
        self.log.send(self.iam, "INFO", "start")
        
        self.setupUi(self)
        self.setGeometry(0, 0, 1030, 690)
        self.setWindowTitle("Data Taking Package 0.3")
        
        # load ini file
        self.cfg = sc.LoadConfig(WORKING_DIR + "IGRINS/Config/IGRINS.ini")
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.dt_sub_ex = self.cfg.get(MAIN, 'hk_sub_exchange')
        self.dt_sub_q = self.cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_dt_ex = self.cfg.get(MAIN, 'sub_hk_exchange')     
        self.sub_dt_q = self.cfg.get(MAIN, 'sub_hk_routing_key')
        
        self.dt_dcs_ex = self.cfg.get(DT, 'dt_dcs_exchange')     
        self.dt_dcs_q = self.cfg.get(DT, 'dt_dcs_routing_key')
        self.dcs_dt_ex = self.cfg.get(DT, 'dcs_dt_exchange')
        self.dcs_dt_q = self.cfg.get(DT, 'dcs_dt_exchange')
        
        self.fits_path = self.cfg.get(DT, 'fits_path')
        self.alive_chk_interval = int(self.cfg.get(DT, 'alive-check-interval'))
        
        self.com_list = ["pdu", "lt", "ut"]
        self.dcs_list = ["svc", "h-band", "k-band"]
        
        self.init_events()
        
        self.radio_HK_sync.setChecked(True)
        self.set_HK_sync()
        
        self.label_zscale_range.setText("---")
        self.e_mscale_min.setText("1000")
        self.e_mscale_max.setText("5000")
        
        for i in range(DCS_CNT):
            self.e_exptime[i].setText("1.63")
            self.e_FS_number[i].setText("1")
            self.e_repeat[i].setText("1")

            self.label_prog_stats[i].setText("idle")
            self.label_prog_time[i].setText("---")
            self.label_prog_elapsed[i].setText("0.0 sec")
        
        today = ti.strftime("%04Y%02m%02d", ti.localtime())
        self.cur_frame = [0, 0, 0]
        
        for i in range(DCS_CNT):
            self.e_path[i].setText(self.fits_path + today)
            filename = "%s_%04d.fits" % (TARGET[i], self.cur_frame[i])
            self.e_savefilename[i].setText(filename)
                    
        for i in range(CAL_CNT):
            self.cal_e_exptime[i].setText("1.63")
            self.cal_e_repeat[i].setText("1")
        
        self.e_utpos.setText("1")
        self.e_ltpos.setText("1")
        
        self.e_movinginterval.setText("1")        
        
        self.simulation_mode = True     #from EngTools
        
        self.cal_mode = False
        
        self.dcs_sts = [False for _ in range(DCS_CNT)]
        self.acquiring = [False for _ in range(DCS_CNT)]
        
        self.take_imaging = [False for _ in range(DCS_CNT)]
        
        self.producer = [None for _ in range(SERV_CONNECT_CNT)]
        self.consumer = [None for _ in range(SERV_CONNECT_CNT)]       

        self.timer_alive = [None for _ in range(DCS_CNT)] 
        
        self.img = [None for _ in range(DCS_CNT)]
        
        self.output_channel = 32
        
        self.cal_cur = 0
           
        for i in range(CAL_CNT):
            self.cal_use_parsing(self.cal_chk[i], self.cal_e_exptime[i], self.cal_e_repeat[i])
                
        self.connect_to_server_hk_ex()
        self.connect_to_server_sub_q()
        self.connect_to_server_dt_ex()
        self.connect_to_server_dcs_q()
        
        
    def closeEvent(self, event: QCloseEvent) -> None:
               
        self.log.send(self.iam, "INFO", "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, "INFO", "This may take several seconds waiting for threads to close")
            
        for idx in range(PDU_IDX):
            msg = "%s %d %s" % (HK_REQ_PWR_ONOFF, idx+1, OFF)
            self.producer[HK_SUB].send_message(self.com_list[PDU], self.dt_sub_q, msg) 
        
        self.producer[HK_SUB].send_message("all", self.dt_sub_q, HK_REQ_EXIT)                               
                
        for th in threading.enumerate():
            self.log.send(self.iam, "DEBUG", th.name + " exit.")
                
        self.log.send(self.iam, "INFO", "Closed!")
                            
        for i in range(SERV_CONNECT_CNT):
            if self.consumer[i] != None:
                self.consumer[i].stop_consumer()
                ti.sleep(3)
            
            if self.producer[i] != None:
                self.producer[i].__del__()
            if self.consumer[i] != None:
                self.consumer[i].__del__()
                
        return super().closeEvent(event)          

        
        
    def init_events(self):
                
        self.radioButton_zscale.clicked.connect(self.auto_scale)
        self.radioButton_mscale.clicked.connect(self.manual_scale)
        self.bt_scale_apply.clicked.connect(self.scale_apply)
        
        self.radio_HK_sync.clicked.connect(self.set_HK_sync)
        self.radio_whole_sync.clicked.connect(self.set_whole_sync)
        self.radio_SVC.clicked.connect(self.set_svc)
        self.radio_H.clicked.connect(self.set_H)
        self.radio_K.clicked.connect(self.set_K)
        
        self.radioButton_zscale.setChecked(True)
        self.radioButton_mscale.setChecked(False)
        self.bt_scale_apply.setEnabled(False)
        
        self.bt_take_image.clicked.connect(self.single_exposure)   
        
        self.e_exptime = [self.e_exptime_svc, self.e_exptimeH, self.e_exptimeK]
        self.e_FS_number = [self.e_FS_number_svc, self.e_FSnumberH, self.e_FSnumberK]
        self.e_repeat = [self.e_repeat_number_svc, self.e_repeatH, self.e_repeatK]
                
        self.label_prog_stats = [self.label_prog_stats_svc, self.label_prog_sts_H, self.label_prog_sts_K]
        self.label_prog_time = [self.label_prog_time_svc, self.label_prog_time_H, self.label_prog_time_K]
        self.label_prog_elapsed = [self.label_prog_elapsed_svc, self.label_prog_elapsed_H, self.label_prog_elapsed_K]
        self.label_cur_num = [self.label_cur_num_svc, self.label_cur_num_H, self.label_cur_num_K]
        
        self.chk_ds9 = [self.chk_ds9_svc, self.chk_ds9_H, self.chk_ds9_K]
        self.chk_autosave = [self.checkBox_autosave_svc, self.checkBox_autosave_H, self.checkBox_autosave_K]
        
        self.bt_save = [self.bt_save_svc, self.bt_save_H, self.bt_save_K]
        self.bt_path = [self.bt_path_svc, self.bt_path_H, self.bt_path_K]
                    
        self.e_path = [self.e_path_svc, self.e_path_H, self.e_path_K]
        self.e_savefilename = [self.e_savefilename_svc, self.e_savefilename_H, self.e_savefilename_K]
        
        for i in range(DCS_CNT):
            self.e_exptime[i].setEnabled(False)
            self.e_FS_number[i].setEnabled(False)
            self.e_repeat[i].setEnabled(False)
            
            self.bt_save[i].clicked.connect(lambda: self.save_fits(i))
            self.bt_path[i].clicked.connect(lambda: self.open_path(i))
            
            self.chk_ds9[i].setEnabled(False)
            self.chk_autosave[i].setEnabled(False)
            
            self.bt_save[i].setEnabled(False)
            self.bt_path[i].setEnabled(False)
            
            self.e_path[i].setEnabled(False)
            self.e_savefilename[i].setEnabled(False)               
            
        
        #------------------
        #calibration
        
        self.chk_open_calibration.clicked.connect(self.open_calilbration)
        
        self.cal_chk = [self.chk_dark, self.chk_flat_on, self.chk_flat_off, self.chk_ThAr, self.chk_pinhole_flat, self.chk_pinhole_ThAr, self.chk_USAF_on, self.chk_USAF_off, self.chk_parking]
        
        self.cal_e_exptime = [self.e_dark_exptime, self.e_flaton_exptime, self.e_flatoff_exptime, self.e_ThAr_exptime, self.e_pinholeflat_exptime, self.e_pinholeThAr_exptime, self.e_USAFon_exptime, self.e_USAFoff_exptime, self.e_parking_exptime]
        
        self.cal_e_repeat = [self.e_dark_repeat, self.e_flaton_repeat, self.e_flatoff_repeat, self.e_ThAr_repeat, self.e_pinholeflat_repeat, self.e_pinholeThAr_repeat, self.e_USAFon_repeat, self.e_USAFoff_repeat, self.e_parking_repeat]
        
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
        

    #-------------------------------
    # dt -> sub: use hk ex
    def connect_to_server_hk_ex(self):
        # RabbitMQ connect  
        self.producer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_sub_ex, "direct", True)      
        self.producer[HK_SUB].connect_to_server()
        self.producer[HK_SUB].define_producer()
    
         
    #-------------------------------
    # sub -> dt: use hk q
    def connect_to_server_sub_q(self):
        # RabbitMQ connect
        self.consumer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.sub_dt_ex, "direct")      
        self.consumer[HK_SUB].connect_to_server()
        self.consumer[HK_SUB].define_consumer(self.sub_dt_q, self.callback_sub)       
        
        th = threading.Thread(target=self.consumer[HK_SUB].start_consumer)
        th.start()
                    
    
    #-------------------------------
    # rev <- sub        
    def callback_sub(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, "INFO", msg)

        param = cmd.split()
        
        # from PDU
        if param[0] == HK_REQ_PWR_STS:
            self.single_exposure()
        
        if param[0] == HK_REQ_INITMOTOR:
            if param[2] == "TRY":
                msg = "%s - need to initialize" % param[1]
                self.log.send(self.iam, "INFO", msg)
            
            elif param[2] == "OK":
                if param[1] == self.com_list[UT]:
                    self.bt_utpos_prev.setEnabled(True)
                    self.bt_utpos_next.setEnabled(True)
                        
                    self.bt_utpos_set1.setEnabled(True)
                    self.bt_utpos_set2.setEnabled(True)
                elif param[1] == self.com_list[LT]:
                    self.bt_ltpos_prev.setEnabled(True)
                    self.bt_ltpos_next.setEnabled(True)
                            
                    self.bt_ltpos_set1.setEnabled(True)
                    self.bt_ltpos_set2.setEnabled(True)
                    self.bt_ltpos_set3.setEnabled(True)
                    self.bt_ltpos_set4.setEnabled(True)
                
        elif param[0] == HK_REQ_MOVEMOTOR:
            self.func_lamp(self.cal_cur)
        
        elif param[0] == HK_REQ_MOTORGO:
            pass
            
        elif param[0] == HK_REQ_MOTORBACK:
            pass

    
    #-------------------------------
    # dt -> dcs    
    def connect_to_server_dt_ex(self):
        # RabbitMQ connect  
        self.producer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_dcs_ex, "direct", True)      
        self.producer[DCS].connect_to_server()
        self.producer[DCS].define_producer()
                
    
    #-------------------------------
    # dcs -> dt
    def connect_to_server_dcs_q(self):
        # RabbitMQ connect
        self.consumer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dcs_dt_ex, "direct")      
        self.consumer[DCS].connect_to_server()
        
        self.consumer[DCS].define_consumer(self.dcs_dt_q, self.callback_dcs)       
        th = threading.Thread(target=self.consumer[DCS].start_consumer)
        th.start()
            
            
    #-------------------------------
    # rev <- dcs 
    def callback_dcs(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, "INFO", msg)

        param = cmd.split()
        dcs = int(param[1]) #COMMAND, iam, paramerter...
        
        if param[0] == CMD_INITIALIZE1:
            connected = bool(param[2])
            self.dcs_sts[dcs] = connected
        
        elif param[0] == CMD_INITIALIZE2:
            #downloadMCD
            self.downloadMCD(dcs, self.simulation_mode)
            
        elif param[0] == CMD_DOWNLOAD:
            #setdetector
            self.set_detector(dcs, self.simulation_mode, MUX_TYPE, self.output_channel)
            
        elif param[0] == CMD_SETDETECTOR:
            
            '''
            if dcs == SVC:
                self.e_exptime_svc.setEnabled(True)
                self.e_FS_number_svc.setEnabled(True)
                self.e_repeat_number_svc.setEnabled(True)  
            elif dcs == H:
                self.e_exptimeH.setEnabled(True)
                self.e_FSnumberH.setEnabled(True)
                self.e_repeatH.setEnabled(True)            
            elif dcs == K:
                self.e_exptimeK.setEnabled(True)
                self.e_FSnumberK.setEnabled(True)
                self.e_repeatK.setEnabled(True)
            '''
                
        elif param[0] == CMD_SETFSPARAM:
            #acquire
            self.acquiring[dcs] = True
            self.acquireramp(dcs, self.simulation_mode)

        elif param[0] == CMD_ACQUIRERAMP:
            # load data
            self.load_data()
            
            self.acquiring[dcs] = False
            
            if self.acquiring[dcs] == False and self.cal_mode:
                self.cal_run_cycle()
        
        elif param[0] == CMD_STOPACQUISITION:
            pass    
        
        
    #-------------------------------
    # dcs command
    def initialize2(self, dc_idx, simul_mode):
        msg = "%s %s %d" % (CMD_INITIALIZE2, self.dcs_list[dc_idx], simul_mode)
        self.producer[DCS].send_message(self.dcs_list[dc_idx], self.dt_dcs_q, msg)
        
        
    def downloadMCD(self, dc_idx, simul_mode):
        msg = "%s %s %d" % (CMD_DOWNLOAD, self.dcs_list[dc_idx], simul_mode)
        self.producer[DCS].send_message(self.dcs_list[dc_idx], self.dt_dcs_q, msg)
                
    
    def set_detector(self, dc_idx, simul_mode, type, channel):
        msg = "%s %d %d %d" % (CMD_SETDETECTOR, self.dcs_list[dc_idx], MUX_TYPE, channel)
        self.producer[DCS].send_message(self.dcs_list[dc_idx], self.dt_dcs_q, msg)
            
          
    def set_fs_param(self, dc_idx, simul_mode, exptime):
        #fsmode        
        msg = "%s %d %d" % (CMD_SETFSMODE, self.dcs_list[dc_idx], simul_mode)
        self.producer[DCS].send_message(self.dcs_list[dc_idx], self.dt_dcs_q, msg)
        
        #setparam
        msg = "%s %d %d 1 1 1 %f 1" % (CMD_SETFSPARAM, self.dcs_list[dc_idx], simul_mode, exptime)
        self.producer[DCS].send_message(self.dcs_list[dc_idx], self.dt_dcs_q, msg)
            
    
    def acquireramp(self, dc_idx, simul_mode):        
        msg = "%s %d %d" % (CMD_ACQUIRERAMP, self.dcs_list[dc_idx], simul_mode)
        self.producer[DCS].send_message(self.dcs_list[dc_idx], self.dt_dcs_q, msg)
        
          
    #def alive_check(self, dc_idx, slmul_mode):
    #    self.send_message_to_ics(dc_idx, slmul_mode, "alive?")
        
        
    def stop_acquistion(self, dc_idx, simul_mode):        
        msg = "%s %d %d" % (CMD_STOPACQUISITION, self.dcs_list[dc_idx], simul_mode)
        self.producer[DCS].send_message(self.dcs_list[dc_idx], self.dt_dcs_q, msg)
                        
            
                       
        
    def load_data(self, ics_idx):
        filepath = ""
        if self.simulation_mode:
            if ics_idx == SVC:
                filepath = WORKING_DIR + "IGRINS/demo/sc/SDCS_demo.fits"
            elif ics_idx == H:
                filepath = WORKING_DIR + "IGRINS/demo/dt/SDCH_demo.fits"
            elif ics_idx == K:
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
        
        if ics_idx == SVC:
            self.label_zscale_range.setText(range)
        
            self.mmin, self.mmax = np.min(self.img[SVC]), np.max(self.img[SVC])
            self.e_mscale_min.setText("%.1f" % self.mmin)
            self.e_mscale_max.setText("%.1f" % self.mmax)
                
        self.reload_img(ics_idx)
        
        
    def reload_img(self, ics_idx):   
        
        try:
            _img = np.flipud(self.img[ics_idx])
                
            scene = QGraphicsScene(self)
            
            if ics_idx == SVC:
                min, max = 0, 0
                if self.radioButton_zscale.isChecked():
                    min, max = self.zmin, self.zmax
                elif self.radioButton_mscale.isChecked():
                    min, max = self.mmin, self.mmax
                
                scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(_img, (int(min), int(max)))).scaled(self.graphicsView_H.width(), self.graphicsView_H.height(), Qt.IgnoreAspectRatio, Qt.FastTransformation))
                self.graphicsView_SVC.setScene(scene) 
                
            elif ics_idx == H:
                scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(_img, (int(self.zmin), int(self.zmax)))).scaled(self.graphicsView_K.width(), self.graphicsView_K.height(), Qt.IgnoreAspectRatio, Qt.FastTransformation))
                self.graphicsView_H.setScene(scene)
                
            elif ics_idx == K:
                scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(_img, (int(self.zmin), int(self.zmax)))).scaled(self.graphicsView_K.width(), self.graphicsView_K.height(), Qt.IgnoreAspectRatio, Qt.FastTransformation))
                self.graphicsView_K.setScene(scene)
        
        except:
            self.log.send(self.iam, "WARNING", "No image")
            
            
    def enable_dcs(self, dcs, enable):
        self.e_exptime[dcs].setEnabled(enable)
        self.e_FS_number[dcs].setEnabled(enable)
        self.e_repeat[dcs].setEnabled(enable)
        
        self.chk_ds9[dcs].setEnabled(enable)
        self.chk_autosave[dcs].setEnabled(enable)
        
        self.bt_save[dcs].setEnabled(enable)
        self.bt_path[dcs].setEnabled(enable)
        
        self.e_path[dcs].setEnabled(enable)
        self.e_savefilename[dcs].setEnabled(enable)        
            
        
    #---------------------------------
    # button 
    
    def auto_scale(self):
        self.reload_img(SVC)
        self.bt_scale_apply.setEnabled(False)
    
    
    def manual_scale(self):
        self.reload_img(SVC)
        self.bt_scale_apply.setEnabled(True)
    
    
    def scale_apply(self):
        self.mmin = float(self.e_mscale_min.text())
        self.mmax = float(self.e_mscale_max.text())
        
        self.reload_img(SVC)
    
    
    def set_HK_sync(self):
        self.enable_dcs(SVC, False)
        self.enable_dcs(H, True)
        self.enable_dcs(K, True)
    
    
    def set_whole_sync(self):
        self.enable_dcs(SVC, True)
        self.enable_dcs(H, True)
        self.enable_dcs(K, True)
    
    
    def set_svc(self):
        self.enable_dcs(SVC, True)
        self.enable_dcs(H, False)
        self.enable_dcs(K, False)
    
    
    def set_H(self):
        self.enable_dcs(SVC, False)
        self.enable_dcs(H, True)
        self.enable_dcs(K, False)
    
    
    def set_K(self):
        self.enable_dcs(SVC, False)
        self.enable_dcs(H, False)
        self.enable_dcs(K, True)
        
    
    def take_image(self):

        if self.take_imaging:
            #if repeat > 1 -> stop
            #if single > abort
            
            self.take_imaging = False
            
        else:
            
            self.single_exposure()
            #if repeat > 1 -> start
            #if signel > start
            
            self.take_imaging = True
        
        
        
    def single_exposure(self):
        
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.load_data(H)
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.load_data(K)
        if self.radio_whole_sync.isChecked() or self.radio_SVC.isChecked():
            self.load_data(SVC)
        return
    
        #calculate!!!! self.fowler_exp from self.e_exptime
        if self.radioButton_sync.isChecked() or self.radioButton_H.isChecked():
            self.dt.set_fs_param(DCSH, self.simulation_mode, self.e_exptimeH)
        if self.radioButton_sync.isChecked() or self.radioButton_K.isChecked():    
            self.dt.set_fs_param(DCSK, self.simulation_mode, self.e_exptimeK)
            
    
    def stop_acquisition(self):
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.stop_acquistion(H, self.simulation_mode)
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.stop_acquistion(K, self.simulation_mode)
        if self.radio_whole_sync.isChecked() or self.radio_SVC.isChecked():
            self.stop_acquistion(SVC, self.simulation_mode)
            
    
    def save_fits(self):
        pass
    
    
    def open_path(self):
        pass
    
    
    def open_calilbration(self):
        if self.chk_open_calibration.isChecked():
            self.setGeometry(0, 0, 1315, 690)
        else:
            self.setGeometry(0, 0, 1030, 690)
    

    
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
        msg = "%s %d %d" % (HK_REQ_PWR_ONOFF, FLAT, LAMP_FLAT[idx])
        self.producer[HK_SUB].send_message(self.com_list[PDU], self.dt_sub_q, msg)
        
        msg = "%s %d %d" % (HK_REQ_PWR_ONOFF, THAR, LAMP_THAR[idx])
        self.producer[HK_SUB].send_message(self.com_list[PDU], self.dt_sub_q, msg)
            
            
    def func_motor(self, idx):
        msg = "%s %s %d" % (HK_REQ_MOVEMOTOR, self.com_list[UT], MOTOR_UT[idx])
        self.producer[HK_SUB].send_message(self.com_list[UT], self.dt_sub_q, msg)
        
        msg = "%s %d %d" % (HK_REQ_MOVEMOTOR, self.com_list[LT], MOTOR_LT[idx])
        self.producer[HK_SUB].send_message(self.com_list[LT], self.dt_sub_q, msg)
        
        
    def motor_init(self, motor):
        msg = "%s %d" % (HK_REQ_INITMOTOR, motor)
        self.producer[HK_SUB].send_message(self.com_list[motor], self.dt_sub_q, msg)
            

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
                
        #msg = "%s %d %d" % (HK_FN_MOVEMOTORDELTA, motor, direction)
        #self.send_message_to_hk(msg)
                
    
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