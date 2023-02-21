# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Dec 30, 2022

@author: hilee
"""

import sys, os
from matplotlib.figure import Figure

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_DTP import *
from DT_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import subprocess

import time as ti
import threading

import numpy as np
import astropy.io.fits as fits 
import Libs.zscale as zs

import glob

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.iam = DT
        
        self.log = LOG(WORKING_DIR + "IGRINS", "DTP")  
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        
        self.setGeometry(0, 0, 1030, 700)
        self.setWindowTitle("Data Taking Package 1.0")        
        
        # canvas
        self.image_fig = []
        self.image_ax = []
        self.image_canvas = []
        
        for i in range(DCS_CNT):
            self.image_fig.append(Figure(figsize=(4, 4), dpi=100))
            self.image_ax.append(self.image_fig[i].add_subplot(111))
            self.image_fig[i].subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99) 
            self.image_canvas.append(FigureCanvas(self.image_fig[i]))
        
        #self.addToolBar(NavigationToolbar(self.image_canvas, self))
        vbox_svc = QVBoxLayout(self.frame_svc)
        vbox_svc.addWidget(self.image_canvas[SVC])
        vbox_H = QVBoxLayout(self.frame_H)
        vbox_H.addWidget(self.image_canvas[H])
        vbox_K = QVBoxLayout(self.frame_K)
        vbox_K.addWidget(self.image_canvas[K])
        #vbox.addWidget(self.toolbar)
                
        # load ini file
        self.cfg = sc.LoadConfig(WORKING_DIR + "IGRINS/Config/IGRINS.ini")
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.dt_main_ex = self.cfg.get(MAIN, 'gui_main_exchange')     
        self.dt_main_q = self.cfg.get(MAIN, 'gui_main_routing_key')
        self.main_dt_ex = self.cfg.get(MAIN, 'main_gui_exchange')
        self.main_dt_q = self.cfg.get(MAIN, 'main_gui_routing_key')
        
        self.dt_sub_ex = self.cfg.get(MAIN, 'hk_sub_exchange')
        self.dt_sub_q = self.cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_dt_ex = self.cfg.get(MAIN, 'sub_hk_exchange')     
        self.sub_dt_q = self.cfg.get(MAIN, 'sub_hk_routing_key')
        
        self.dt_dcs_ex = self.cfg.get(DT, 'dt_dcs_exchange')     
        self.dt_dcs_q = self.cfg.get(DT, 'dt_dcs_routing_key')
        self.dcs_dt_ex = self.cfg.get(DT, 'dcs_dt_exchange')
        self.dcs_dt_q = self.cfg.get(DT, 'dcs_dt_routing_key')
        
        self.fits_path = self.cfg.get(DT, 'fits_path')
        self.alive_chk_interval = int(self.cfg.get(DT, 'alive-check-interval'))
        
        self.com_list = ["pdu", "lt", "ut"]
        self.dcs_list = ["DCSS", "DCSH", "DCSK"]
        
        self.init_events()
        
        self.bt_take_image.setText("Take Image")
        
        self.enable_dcs(SVC, False)
        self.enable_dcs(H, False)
        self.enable_dcs(K, False)
        
        self.label_zscale_range.setText("---")
        self.e_mscale_min.setText("1000")
        self.e_mscale_max.setText("5000")
        
        for i in range(DCS_CNT):
            self.e_exptime[i].setText("1.63")
            self.e_FS_number[i].setText("1")
            self.e_repeat[i].setText("1")

            self.label_prog_sts[i].setText("IDLE")
            self.label_prog_time[i].setText("---")
            self.label_prog_elapsed[i].setText("0.0 sec")
            
        self.today = ti.strftime("%04Y%02m%02d", ti.localtime())
        self.cur_frame = [0, 0, 0]
        
        for i in range(DCS_CNT):
            self.label_cur_num[i].setText("0 / 0")
            self.e_path[i].setText(self.fits_path + self.today)
            self.cur_frame[i] = self.new_seq(i)
            filename = "%s_%04d.fits" % (self.dcs_list[i], self.cur_frame[i])
            self.e_savefilename[i].setText(filename)
                    
        for i in range(CAL_CNT):
            self.cal_e_exptime[i].setText("1.63")
            self.cal_e_repeat[i].setText("1")
        
        self.e_utpos.setText("-")
        self.e_ltpos.setText("-")
        
        self.e_movinginterval.setText("1")        
        
        self.simulation_mode = False     #from EngTools
        self.mode = SINGLE_MODE
        self.continous = False
        
        self.cal_mode = False

        self.dcs_sts = [False for _ in range(DCS_CNT)]
        self.acquiring = [False for _ in range(DCS_CNT)]
                
        self.producer = [None for _ in range(SERV_CONNECT_CNT)]
        self.consumer = [None for _ in range(SERV_CONNECT_CNT)]       
        
        self.img = [None for _ in range(DCS_CNT)]
        
        self.output_channel = 32
        
        self.cur_cnt = [0 for _ in range(DCS_CNT)]
        self.measure_T = [0 for _ in range(DCS_CNT)]
        self.header = [None for _ in range(DCS_CNT)]
        
        self.sel_mode = MODE_HK
        self.radio_HK_sync.setChecked(True)
        self.set_HK_sync()
        
        self.stop_clicked = False
        self.cal_stop_clicked = False
        
        self.cal_cur = 0
        self.ut_moved = False
        self.lt_moved = False
        
        self.power_status = [OFF for _ in range(PDU_IDX)] # motor, FLAT, THAR
           
        for i in range(CAL_CNT):
            self.cal_use_parsing(self.cal_chk[i], self.cal_e_exptime[i], self.cal_e_repeat[i])         
        
        # progress bar     
        self.prog_timer = [None for _ in range(DCS_CNT)]
        self.cur_prog_step = [0 for _ in range(DCS_CNT)]
        for dc_idx in range(DCS_CNT):
            self.progressBar[dc_idx].setValue(0)
        
        # elapsed
        self.elapsed_timer = [None for _ in range(DCS_CNT)]
        self.elapsed = [0.0 for _ in range(DCS_CNT)]
        
        # connect to server
        self.connect_to_server_main_ex()
        self.connect_to_server_gui_q()
    
        self.connect_to_server_hk_ex()
        self.connect_to_server_sub_q()
        
        self.connect_to_server_dt_ex()
        self.connect_to_server_dcs_q() 
            
        #ti.sleep(5)
        self.get_pwr_sts()
        self.alive_check()                          
        
        
    def closeEvent(self, event: QCloseEvent) -> None:               
        self.log.send(self.iam, DEBUG, "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, DEBUG, "This may take several seconds waiting for threads to close")
            
        for idx in range(PDU_IDX):
            self.power_onoff(idx+1, OFF)

        ti.sleep(5)
                        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
                                                    
        for i in range(SERV_CONNECT_CNT):                
            if i == ENG_TOOLS:
                msg = "%s %s" % (EXIT, DT)
                self.producer[ENG_TOOLS].send_message(self.dt_main_q, msg)
            
            if self.producer[i] != None:
                self.producer[i].__del__()

        self.log.send(self.iam, DEBUG, "Closed!") 
                
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
        
        self.bt_take_image.clicked.connect(self.btn_click)   
        
        self.radio_exptime = [self.radio_exptime_svc, self.radio_exptime_H, self.radio_exptime_K]
        self.radio_N_fowler = [self.radio_number_fowler_svc, self.radio_number_fowler_H, self.radio_number_fowler_K]
                
        self.e_exptime = [self.e_exptime_svc, self.e_exptimeH, self.e_exptimeK]
        self.e_FS_number = [self.e_FS_number_svc, self.e_FSnumberH, self.e_FSnumberK]
        self.e_repeat = [self.e_repeat_number_svc, self.e_repeatH, self.e_repeatK]
                
        self.label_prog_sts = [self.label_prog_stats_svc, self.label_prog_sts_H, self.label_prog_sts_K]
        self.label_prog_time = [self.label_prog_time_svc, self.label_prog_time_H, self.label_prog_time_K]
        self.label_prog_elapsed = [self.label_prog_elapsed_svc, self.label_prog_elapsed_H, self.label_prog_elapsed_K]
        self.label_cur_num = [self.label_cur_num_svc, self.label_cur_num_H, self.label_cur_num_K]
        self.progressBar = [self.progressBar_svc, self.progressBar_H, self.progressBar_K]

        self.sts_com = [self.sts_svc, self.sts_H, self.sts_K]
        self.bt_init = [self.bt_init_SVC, self.bt_init_H, self.bt_init_K]
        self.chk_ds9 = [self.chk_ds9_svc, self.chk_ds9_H, self.chk_ds9_K]
        self.chk_autosave = [self.checkBox_autosave_svc, self.checkBox_autosave_H, self.checkBox_autosave_K]
        
        self.bt_save = [self.bt_save_svc, self.bt_save_H, self.bt_save_K]
        self.bt_path = [self.bt_path_svc, self.bt_path_H, self.bt_path_K]
                    
        self.e_path = [self.e_path_svc, self.e_path_H, self.e_path_K]
        self.e_savefilename = [self.e_savefilename_svc, self.e_savefilename_H, self.e_savefilename_K]
        
        for i in range(DCS_CNT):
            
            self.QWidgetLabelColor(self.sts_com[i], "gray")

            self.radio_exptime[i].setChecked(True)
            
            self.e_exptime[i].setEnabled(False)
            self.e_FS_number[i].setEnabled(False)
            self.e_repeat[i].setEnabled(False)
            
            self.chk_ds9[i].setEnabled(False)
            self.chk_autosave[i].setEnabled(False)
            
            self.bt_init[i].setEnabled(False)
            self.bt_save[i].setEnabled(False)
            self.bt_path[i].setEnabled(False)
            
            self.e_path[i].setEnabled(False)
            self.e_savefilename[i].setEnabled(False)               
            
        self.radio_exptime[SVC].clicked.connect(lambda: self.judge_exp_time(SVC)) 
        self.radio_N_fowler[SVC].clicked.connect(lambda: self.judge_FS_number(SVC))
        self.e_exptime[SVC].editingFinished.connect(lambda: self.judge_param(SVC))
        self.e_FS_number[SVC].editingFinished.connect(lambda: self.judge_param(SVC))
        self.e_repeat[SVC].editingFinished.connect(lambda: self.change_name(SVC))
        
        self.radio_exptime[H].clicked.connect(lambda: self.judge_exp_time(H)) 
        self.radio_N_fowler[H].clicked.connect(lambda: self.judge_FS_number(H))
        self.e_exptime[H].editingFinished.connect(lambda: self.judge_param(H))
        self.e_FS_number[H].editingFinished.connect(lambda: self.judge_param(H)) 
        self.e_repeat[H].editingFinished.connect(lambda: self.change_name(H))
        
        self.radio_exptime[K].clicked.connect(lambda: self.judge_exp_time(K)) 
        self.radio_N_fowler[K].clicked.connect(lambda: self.judge_FS_number(K))
        self.e_exptime[K].editingFinished.connect(lambda: self.judge_param(K))
        self.e_FS_number[K].editingFinished.connect(lambda: self.judge_param(K)) 
        self.e_repeat[K].editingFinished.connect(lambda: self.change_name(K)) 
        
        self.bt_init[SVC].clicked.connect(lambda: self.initialize2(SVC))    
        self.bt_save[SVC].clicked.connect(lambda: self.save_fits(SVC))
        self.bt_path[SVC].clicked.connect(lambda: self.open_path(SVC))
        
        self.bt_init[H].clicked.connect(lambda: self.initialize2(H))    
        self.bt_save[H].clicked.connect(lambda: self.save_fits(H))
        self.bt_path[H].clicked.connect(lambda: self.open_path(H))
        
        self.bt_init[K].clicked.connect(lambda: self.initialize2(K))    
        self.bt_save[K].clicked.connect(lambda: self.save_fits(K))
        self.bt_path[K].clicked.connect(lambda: self.open_path(K))
            
            
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
        
        self.bt_utpos_prev.clicked.connect(lambda: self.move_motor_delta(UT, PREV))
        self.bt_utpos_next.clicked.connect(lambda: self.move_motor_delta(UT, NEXT))
        
        self.bt_utpos_set1.clicked.connect(lambda: self.motor_pos_set(UT, 0))
        self.bt_utpos_set2.clicked.connect(lambda: self.motor_pos_set(UT, 1))
        
        self.bt_ltpos_prev.clicked.connect(lambda: self.move_motor_delta(LT, PREV))
        self.bt_ltpos_next.clicked.connect(lambda: self.move_motor_delta(LT, NEXT))
        
        self.bt_ltpos_set1.clicked.connect(lambda: self.motor_pos_set(LT, 0))
        self.bt_ltpos_set2.clicked.connect(lambda: self.motor_pos_set(LT, 1))
        self.bt_ltpos_set3.clicked.connect(lambda: self.motor_pos_set(LT, 2))
        self.bt_ltpos_set4.clicked.connect(lambda: self.motor_pos_set(LT, 3))
        
        self.protect_btn_ut(False)
        self.protect_btn_lt(False)        
        
    #-------------------------------
    # dt -> main
    def connect_to_server_main_ex(self):
        # RabbitMQ connect  
        self.producer[ENG_TOOLS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_main_ex)      
        self.producer[ENG_TOOLS].connect_to_server()
        self.producer[ENG_TOOLS].define_producer()
        
        msg = "%s %s" % (ALIVE, DT)
        self.producer[ENG_TOOLS].send_message(self.dt_main_q, msg)
    
         
    #-------------------------------
    # main -> dt
    def connect_to_server_gui_q(self):
        # RabbitMQ connect
        self.consumer[ENG_TOOLS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.main_dt_ex)      
        self.consumer[ENG_TOOLS].connect_to_server()
        self.consumer[ENG_TOOLS].define_consumer(self.main_dt_q, self.callback_main)       
        
        th = threading.Thread(target=self.consumer[ENG_TOOLS].start_consumer)
        th.daemon = True
        th.start()
        
        
    #-------------------------------
    # rev <- main        
    def callback_main(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[1] != self.iam:
            return
                
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        if param[0] == ALIVE:
            msg = "%s %s" % (ALIVE, DT)
            self.producer[ENG_TOOLS].send_message(self.dt_main_q, msg)
            
        elif param[0] == TEST_MODE:
            self.simulation_mode = bool(int(param[2]))        


    #-------------------------------
    # dt -> sub: use hk ex
    def connect_to_server_hk_ex(self):
        # RabbitMQ connect  
        self.producer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_sub_ex)      
        self.producer[HK_SUB].connect_to_server()
        self.producer[HK_SUB].define_producer()

    
         
    #-------------------------------
    # sub -> dt: use hk q
    def connect_to_server_sub_q(self):
        # RabbitMQ connect
        self.consumer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.sub_dt_ex)      
        self.consumer[HK_SUB].connect_to_server()
        self.consumer[HK_SUB].define_consumer(self.sub_dt_q, self.callback_sub)       
        
        th = threading.Thread(target=self.consumer[HK_SUB].start_consumer)
        th.daemon = True
        th.start()
                    
    
    #-------------------------------
    # rev <- sub        
    def callback_sub(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        com = False
        for i in range(COM_CNT):
            if param[1] == self.com_list[i]:
                com = True
                break
        if com == False:
            return
        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        # from PDU
        if param[0] == HK_REQ_PWR_STS and param[2] == DT:
            for i in range(PDU_IDX):
                self.power_status[i] = param[i+3]

            if self.power_status[MACIE-1] == OFF:
                self.power_onoff(MACIE, ON)

            '''                                        
            if self.dcs_sts[H] == False or self.dcs_sts[K] == False:
                self.bt_run.setText("RUN")
                self.QWidgetBtnColor(self.bt_run, "white", "red")
                self.cal_stop_clicked = False
                
                self.log.send(self.iam, WARNING, "Check DCS initializing")
            '''
        
        elif param[0] == DT_REQ_INITMOTOR:
            if param[2] == "TRY":
                msg = "%s - need to initialize" % param[1]
                self.log.send(self.iam, INFO, msg)
            
            elif param[2] == "OK":
                if param[1] == self.com_list[UT]:
                    self.protect_btn_ut(True)
                    self.e_utpos.setText("0")
                elif param[1] == self.com_list[LT]:
                    self.protect_btn_lt(True)
                    self.e_ltpos.setText("0")
            
            if param[1] == self.com_list[UT]:
                self.QWidgetBtnColor(self.bt_ut_motor_init, "white", "green")
            elif param[1] == self.com_list[LT]:
                self.QWidgetBtnColor(self.bt_lt_motor_init, "white", "green")
                
            self.bt_ut_motor_init.setEnabled(True)
            self.bt_lt_motor_init.setEnabled(True)
                
        elif param[0] == DT_REQ_MOVEMOTOR:
            if param[1] == self.com_list[UT]:
                self.ut_moved = True
                self.e_utpos.setText(param[2])
            elif param[1] == self.com_list[LT]:
                self.lt_moved = True
                self.e_ltpos.setText(param[2])
            
            if self.ut_moved and self.lt_moved:
                self.func_lamp(self.cal_cur)
                ti.sleep(1)
                
                self.cal_exposure()   
                
                # for test
                #self.func_lamp(self.cal_cur, OFF)
                #self.cal_cur += 1
                #self.cal_run_cycle()
        
        elif param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK:
            if param[1] == self.com_list[UT]:
                self.protect_btn_ut(True)
                self.e_utpos.setText(param[2])
            elif param[1] == self.com_list[LT]:
                self.protect_btn_lt(True)
                self.e_ltpos.setText(param[2])
        
        elif param[0] == DT_REQ_SETUT:
            pass
        
        elif param[0] == DT_REQ_SETLT:
            pass

    
    #-------------------------------
    # dt -> dcs    
    def connect_to_server_dt_ex(self):
        # RabbitMQ connect  
        self.producer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_dcs_ex)      
        self.producer[DCS].connect_to_server()
        self.producer[DCS].define_producer()
    
    #-------------------------------
    # dcs -> dt
    def connect_to_server_dcs_q(self):
        # RabbitMQ connect
        self.consumer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dcs_dt_ex)      
        self.consumer[DCS].connect_to_server()
        self.consumer[DCS].define_consumer(self.dcs_dt_q, self.callback_dcs)       
        
        th = threading.Thread(target=self.consumer[DCS].start_consumer)
        th.daemon = True
        th.start()
        
            
            
    #-------------------------------
    # rev <- dcs 
    def callback_dcs(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)

        param = cmd.split()
        dc_idx = self.dcs_list.index(param[1])

        if len(param) > 2 and param[2] == "TRY":
            self.dcs_sts[dc_idx] = False
            self.QWidgetBtnColor(self.bt_init[dc_idx], "white", "red")
            return
        
        if param[0] == ALIVE:
            self.dcs_sts[dc_idx] = True
            self.show_alive_sts()
            self.QWidgetBtnColor(self.bt_init[dc_idx], "black", "white")
            return
                        
        if param[0] == CMD_INITIALIZE2_ICS:
            self.enable_dcs(dc_idx, True)
            self.QWidgetBtnColor(self.bt_init[dc_idx], "white", "green")
            self.bt_init[dc_idx].setEnabled(True)

        elif param[0] == CMD_SETFSPARAM_ICS:            
            self.cur_cnt[dc_idx] += 1
            
            self.label_prog_sts[dc_idx].setText("END")
            
            end_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
            self.label_prog_time[dc_idx].setText(self.label_prog_time[dc_idx].text() + " / " + end_time)
                        
            #self.prog_timer[dc_idx].stop()
            self.cur_prog_step[dc_idx] = 100
            self.progressBar[dc_idx].setValue(self.cur_prog_step[dc_idx])           

            #self.elapsed_timer[dc_idx].stop()

            self.measure_T[dc_idx] = float(param[2])
            
            # load data
            self.load_data(dc_idx, param[3])
        
            self.acquiring[dc_idx] = False
            
            if self.cal_mode:
                show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.cal_e_repeat[self.cal_cur].text())
                self.label_cur_num[dc_idx].setText(show_cur_cnt)

                if self.cal_stop_clicked:
                    self.cur_cnt[dc_idx] = 0
                    self.bt_run.setText("RUN")
                    self.QWidgetBtnColor(self.bt_run, "black", "white")
                    self.cal_stop_clicked = False 
                                
                elif self.cur_cnt[dc_idx] < int(self.cal_e_repeat[self.cal_cur].text()):
                    self.continous = True
                    self.bt_take_image.click()
                
                else:
                    self.cur_cnt[dc_idx] = 0
                    self.bt_run.setText("RUN")
                    self.QWidgetBtnColor(self.bt_run, "black", "white")
                    self.cal_stop_clicked = False                   
            
                    if self.acquiring[H] == False and self.acquiring[K] == False:
                        self.func_lamp(self.cal_cur, OFF)
                        self.cal_cur += 1
                        self.cal_run_cycle()
                
            else:
                show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.e_repeat[dc_idx].text())
                self.label_cur_num[dc_idx].setText(show_cur_cnt)
                
                if self.stop_clicked:
                    self.cur_cnt[dc_idx] = 0
                    self.protect_btn(True) 
                    self.bt_take_image.setText("Continuous")
                    
                    self.QWidgetBtnColor(self.bt_take_image, "black", "white")
                    self.stop_clicked = False
                    self.enable_dcs(dc_idx, True)

                elif self.cur_cnt[dc_idx] < int(self.e_repeat[dc_idx].text()):
                    self.continous = True
                    self.bt_take_image.click()
                
                else:
                    self.cur_cnt[dc_idx] = 0
                    self.protect_btn(True) 
                                            
                    if self.mode == CONT_MODE:
                        self.bt_take_image.setText("Continuous")
                    else:
                        self.bt_take_image.setText("Take Image")
                        
                    self.QWidgetBtnColor(self.bt_take_image, "black", "white")
                    self.stop_clicked = False
                    self.enable_dcs(dc_idx, True)

        elif param[0] == CMD_STOPACQUISITION:
            
            end_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
            self.label_prog_time[dc_idx].setText(self.label_prog_time[dc_idx].text() + " / " + end_time)
                        
            self.protect_btn(True)                    
            self.bt_take_image.setText("Take Image")  
            self.QWidgetBtnColor(self.bt_take_image, "black", "white")
            self.stop_clicked = False  
            self.enable_dcs(dc_idx, True)
        
        
    #-------------------------------
    # dcs command
    def initialize2(self, dc_idx):
        if self.simulation_mode == False and self.dcs_sts[dc_idx] == False:
            return
        
        self.bt_init[dc_idx].setEnabled(False)
        self.QWidgetBtnColor(self.bt_init[dc_idx], "yellow", "blue")
        msg = "%s %s %d" % (CMD_INITIALIZE2_ICS, self.dcs_list[dc_idx], self.simulation_mode)
        self.producer[DCS].send_message(self.dt_dcs_q, msg)
            
        
    def set_fs_param(self, dc_idx):     

        if self.simulation_mode == False and self.dcs_sts[dc_idx] == False:
            return

        self.enable_dcs(dc_idx, False)
        
        show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.e_repeat[dc_idx].text())
        self.label_cur_num[dc_idx].setText(show_cur_cnt)   

        #setparam
        _exptime = float(self.e_exptime[dc_idx].text())
        _FS_number = int(self.e_FS_number[dc_idx].text())
        _fowlerTime = _exptime - T_frame * _FS_number
        _cal_waittime = T_br + (T_frame + _fowlerTime + (2 * T_frame * _FS_number))
            
        start_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())       
        
        self.label_prog_sts[dc_idx].setText("START")
        self.label_prog_time[dc_idx].setText(start_time)

        # progress bar 
        self.prog_timer[dc_idx] = QTimer(self)
        self.prog_timer[dc_idx].setInterval(int(_cal_waittime*10))   
        self.prog_timer[dc_idx].timeout.connect(lambda: self.show_progressbar(dc_idx))    

        self.cur_prog_step[dc_idx] = 0
        self.progressBar[dc_idx].setValue(self.cur_prog_step[dc_idx])    
        self.prog_timer[dc_idx].start()    
        
        # elapsed               
        self.elapsed_timer[dc_idx] = QTimer(self) 
        self.elapsed_timer[dc_idx].setInterval(0.001)
        self.elapsed_timer[dc_idx].timeout.connect(lambda: self.show_elapsed(dc_idx))

        self.elapsed[dc_idx] = ti.time()
        self.label_prog_elapsed[dc_idx].setText("0.0")    
        self.elapsed_timer[dc_idx].start()

        if self.cur_cnt[dc_idx] == 0:
            msg = "%s %s %d %.3f 1 %d 1 %.3f 1" % (CMD_SETFSPARAM_ICS, self.dcs_list[dc_idx], self.simulation_mode, _exptime, _FS_number, _fowlerTime)
        else:
            msg = "%s %s %d" % (CMD_ACQUIRERAMP_ICS, self.dcs_list[dc_idx], self.simulation_mode)
        self.producer[DCS].send_message(self.dt_dcs_q, msg)


        self.acquiring[dc_idx] = True

          
    def alive_check(self):  

        for idx in range(DCS_CNT):
            self.dcs_sts[idx] = False
        
        self.producer[DCS].send_message(self.dt_dcs_q, ALIVE)
        #print("alive check")

        #timer = QTimer()
        #timer.singleShot(self.alive_chk_interval*1000, self.alive_check)
        #threading.Timer(self.alive_chk_interval, self.alive_check).start()
        
    
    def show_alive_sts(self):
        for idx in range(DCS_CNT):
            if self.dcs_sts[idx]:
                self.QWidgetLabelColor(self.sts_com[idx], "green")
            else:
                self.QWidgetLabelColor(self.sts_com[idx], "gray")

        
    def stop_acquistion(self, dc_idx):        
        if self.cur_prog_step[dc_idx] > 0:
            self.prog_timer[dc_idx].stop()
            self.elapsed_timer[dc_idx].stop()
                
        msg = "%s %s %d" % (CMD_STOPACQUISITION, self.dcs_list[dc_idx], self.simulation_mode)
        self.producer[DCS].send_message(self.dt_dcs_q, msg)
    
        
    
    def load_data(self, dc_idx, folder_name):
        
        self.label_prog_sts[dc_idx].setText("TRANSFER")
        
        try:
            filepath = ""
            if self.simulation_mode:
                if dc_idx == SVC:
                    filepath = "%sIGRINS/Demo/SDCS_demo.fits" % WORKING_DIR
                elif dc_idx == H:
                    filepath = "%sIGRINS/Demo/SDCH_demo.fits" % WORKING_DIR
                elif dc_idx == K:
                    filepath = "%sIGRINS/Demo/SDCK_demo.fits" % WORKING_DIR
            else:
                if dc_idx == SVC:
                    filepath = "%sIGRINS/dcss/Fowler/%s/Result/FowlerResult.fits" % (WORKING_DIR, folder_name)
                elif dc_idx == H:
                    filepath = "%sIGRINS/dcsh/Fowler/%s/Result/FowlerResult.fits" % (WORKING_DIR, folder_name)
                elif dc_idx == K:
                    filepath = "%sIGRINS/dcsk/Fowler/%s/Result/FowlerResult.fits" % (WORKING_DIR, folder_name)
            
            frm = fits.open(filepath)
            data = frm[0].data
            self.header[dc_idx] = frm[0].header
            _img = np.array(data, dtype = "f")
            #_img = np.flipud(np.array(data, dtype = "f"))
            self.img[dc_idx] = _img#[0:FRAME_Y, 0:FRAME_X]
            #self.img = _img
            
            self.zmin, self.zmax = zs.zscale(self.img[dc_idx])
            range = "%d ~ %d" % (self.zmin, self.zmax)
            
            if dc_idx == SVC:
                self.label_zscale_range.setText(range)
            
                self.mmin, self.mmax = np.min(self.img[SVC]), np.max(self.img[SVC])
                self.e_mscale_min.setText("%.1f" % self.mmin)
                self.e_mscale_max.setText("%.1f" % self.mmax)
                    
            if self.chk_ds9[dc_idx].isChecked():
                ds9 = WORKING_DIR + 'IGRINS/ds9'
                subprocess.Popen([ds9, filepath])
                
            if self.chk_autosave[dc_idx].isChecked():
                self.save_fits(dc_idx)
            
            self.reload_img(dc_idx)
        
        except:
            self.img[dc_idx] = None
            self.log.send(self.iam, WARNING, "No image")
            
        
    def reload_img(self, dc_idx):   
        
        try:
            #_img = np.flipud(self.img[dc_idx])
            #_img = np.fliplr(np.rot90(self.img[dc_idx])
            
            _img = self.img[dc_idx]
                            
            if dc_idx == SVC:
                _min, _max = 0, 0
                if self.radioButton_zscale.isChecked():
                    _min, _max = self.zmin, self.zmax
                elif self.radioButton_mscale.isChecked():
                    _min, _max = self.mmin, self.mmax
            else:
                _min, _max = self.zmin, self.zmax
                                
            self.image_ax[dc_idx].imshow(_img, vmin=_min, vmax=_max, cmap='gray', origin='lower')
            self.image_canvas[dc_idx].draw()
            
            self.label_prog_sts[dc_idx].setText("DONE")
                
        except:
            self.img[dc_idx] = None
            self.log.send(self.iam, WARNING, "No image")
                        
            
    def enable_dcs(self, dc_idx, enable):
        self.radio_exptime[dc_idx].setEnabled(enable)
        self.e_exptime[dc_idx].setEnabled(enable)

        self.radio_N_fowler[dc_idx].setEnabled(enable)
        self.e_FS_number[dc_idx].setEnabled(enable)

        self.e_repeat[dc_idx].setEnabled(enable)
        
        self.chk_ds9[dc_idx].setEnabled(enable)
        self.chk_autosave[dc_idx].setEnabled(enable)
        
        self.bt_save[dc_idx].setEnabled(enable)
        self.bt_path[dc_idx].setEnabled(enable)
        
        self.e_path[dc_idx].setEnabled(enable)
        self.e_savefilename[dc_idx].setEnabled(enable)        
        
        if self.radio_exptime[dc_idx].isChecked() and enable == True:
            self.judge_exp_time(dc_idx)
        elif self.radio_N_fowler[dc_idx].isChecked() and enable == True:
            self.judge_FS_number(dc_idx)
            
            
    def show_elapsed(self, dc_idx):
        cur_elapsed = ti.time() - self.elapsed[dc_idx]
        if self.measure_T[dc_idx] > 0 and cur_elapsed >= self.measure_T[dc_idx] or (self.mode == SINGLE_MODE and self.stop_clicked):
            self.elapsed_timer[dc_idx].stop()
            return
        
        msg = "%.3f sec" % (ti.time() - self.elapsed[dc_idx])
        self.label_prog_elapsed[dc_idx].setText(msg)


    def show_progressbar(self, dc_idx):
        if self.cur_prog_step[dc_idx] >= 100 or (self.mode == SINGLE_MODE and self.stop_clicked):
            self.prog_timer[dc_idx].stop()
            #self.log.send(self.iam, INFO, "progress bar end!!!")
            return
        
        self.cur_prog_step[dc_idx] += 1
        self.progressBar[dc_idx].setValue(self.cur_prog_step[dc_idx])


    def protect_btn(self, enable):
        self.radio_HK_sync.setEnabled(enable)
        self.radio_whole_sync.setEnabled(enable)
        self.radio_SVC.setEnabled(enable)
        self.radio_H.setEnabled(enable)
        self.radio_K.setEnabled(enable)
        
        #if enable == False and self.bt_take_image.text() == "Stop":
        #    self.bt_take_image.setEnabled(True)
        #else:
        #    self.bt_take_image.setEnabled(enable)

        for dc_idx in range(DCS_CNT):
            self.bt_init[dc_idx].setEnabled(enable)
            
    
    def protect_btn_ut(self, enable):
        self.bt_utpos_prev.setEnabled(enable)
        self.e_utpos.setEnabled(enable)
        self.bt_utpos_next.setEnabled(enable)
                
        self.bt_utpos_set1.setEnabled(enable)
        self.bt_utpos_set2.setEnabled(enable)
        
    
    def protect_btn_lt(self, enable):
        self.bt_ltpos_prev.setEnabled(enable)
        self.e_ltpos.setEnabled(enable)
        self.bt_ltpos_next.setEnabled(enable)
                
        self.bt_ltpos_set1.setEnabled(enable)
        self.bt_ltpos_set2.setEnabled(enable)
        self.bt_ltpos_set3.setEnabled(enable)
        self.bt_ltpos_set4.setEnabled(enable)
        
    
    def cal_exposure(self):
        self.set_fs_param(H)
        self.set_fs_param(K)
                
        
    def QWidgetEditColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QLineEdit {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QLineEdit {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
        
        
    def QWidgetCheckBoxColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QCheckBox {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QCheckBox {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
            
            
    def QWidgetBtnColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QPushButton {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QPushButton {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
            
        
    def last_seq(self, dc_idx):
        fpath = self.e_path[dc_idx].text()
        
        if fpath[-1] != "/":
            fpath += "/"
            
        sfiles = glob.glob(fpath + "%s_????.fits" % self.dcs_list[dc_idx])
        print(sfiles)
        max_seq = 0
        if sfiles:
            max_seq = int(max(sfiles).split("_")[1][:4])
        else:
            max_seq = 0
            
        return max_seq
    
    
    def new_seq(self, dc_idx):
        return self.last_seq(dc_idx) + 1
                                
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
        self.sel_mode = MODE_HK
        self.bt_init[SVC].setEnabled(False)
        self.bt_init[H].setEnabled(True)
        self.bt_init[K].setEnabled(True)
        
        self.enable_dcs(SVC, False)
            
    
    def set_whole_sync(self):
        self.sel_mode = MODE_WHOLE
        self.bt_init[SVC].setEnabled(True)
        self.bt_init[H].setEnabled(True)
        self.bt_init[K].setEnabled(True)
                    
    
    def set_svc(self):
        self.sel_mode = MODE_SVC
        self.bt_init[SVC].setEnabled(True)
        self.bt_init[H].setEnabled(False)
        self.bt_init[K].setEnabled(False)
        
        self.enable_dcs(H, False)
        self.enable_dcs(K, False)
    
    
    def set_H(self):
        self.sel_mode = MODE_H
        self.bt_init[SVC].setEnabled(False)
        self.bt_init[H].setEnabled(True)
        self.bt_init[K].setEnabled(False)
        
        self.enable_dcs(SVC, False)
        self.enable_dcs(K, False)
    
    
    def set_K(self):
        self.sel_mode = MODE_K
        self.bt_init[SVC].setEnabled(False)
        self.bt_init[H].setEnabled(False)
        self.bt_init[K].setEnabled(True)
        
        self.enable_dcs(SVC, False)
        self.enable_dcs(H, False)
        
        
    def btn_click(self):
        if self.mode == CONT_MODE:
            if self.continous:
                self.single_exposure()
                self.continous = False
            else:
                btn_name = self.bt_take_image.text()
                self.stop_clicked = False
                if btn_name == "Stop":
                    self.stop_clicked = True
                else:
                    self.single_exposure()
        else:
            btn_name = self.bt_take_image.text()
            self.stop_clicked = False
            if btn_name == "Stop":
                self.stop_clicked = True
            elif btn_name == "Abort":
                self.stop_acquisition()
            else:
                self.single_exposure()
            
        
    def single_exposure(self):    
        self.QWidgetBtnColor(self.bt_take_image, "yellow", "blue")
        
        if int(self.e_repeat[SVC].text()) > 1 or int(self.e_repeat[H].text()) > 1 or int(self.e_repeat[K].text()) > 1:
            self.bt_take_image.setText("Stop")
        else:
            self.bt_take_image.setText("Abort")
                    
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.set_fs_param(H)            
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.set_fs_param(K)
        if self.radio_whole_sync.isChecked() or self.radio_SVC.isChecked():
            self.set_fs_param(SVC)
        
        self.protect_btn(False)
                    
    
    def stop_acquisition(self):        
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.stop_acquistion(H)
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.stop_acquistion(K)
        if self.radio_whole_sync.isChecked() or self.radio_SVC.isChecked():
            self.stop_acquistion(SVC)
                    
    
    def judge_exp_time(self, dc_idx):
        self.e_exptime[dc_idx].setEnabled(True)
        self.e_FS_number[dc_idx].setEnabled(False)
        
        
    def judge_FS_number(self, dc_idx):
        self.e_exptime[dc_idx].setEnabled(False)
        self.e_FS_number[dc_idx].setEnabled(True)
        
        
    def judge_param(self, dc_idx):
        if self.e_exptime[dc_idx].text() == "" or self.e_FS_number[dc_idx].text() == "":
            return
        
        # calculation fowler number & exp time
        _expTime = float(self.e_exptime[dc_idx].text())
        _fowler_num = int(self.e_FS_number[dc_idx].text())

        _fowler_time = T_exp

        if self.radio_exptime[dc_idx].isChecked():
            _max_fowler_number = int((_expTime - T_minFowler) / T_frame)
            if _fowler_num > _max_fowler_number:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'exposure time'!")
                self.log.send(self.iam, WARNING, "please change 'exposure time'!")
                return

        elif self.radio_N_fowler[dc_idx].isChecked():
            _fowler_time = _expTime - T_frame * _fowler_num
            if _fowler_time < T_minFowler:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'fowler sampling number'!")
                self.log.send(self.iam, WARNING, "please change 'fowler sampling number'!")
                return        
            
    
    def change_name(self, dc_idx):
        if int(self.e_repeat[dc_idx].text()) > 1:
            self.bt_take_image.setText("Continuous")
            self.mode = CONT_MODE
        else:
            self.bt_take_image.setText("Take Image")
            self.mode = SINGLE_MODE
        self.QWidgetBtnColor(self.bt_take_image, "black", "white")
        self.stop_clicked = False
        
    
    def save_fits(self, dc_idx):
        
        fpath = "%s" % self.e_path[dc_idx].text()
        self.log.createFolder(fpath)
        
        self.cur_frame[dc_idx] = self.new_seq(dc_idx)
        filename = "%s_%04d.fits" % (self.dcs_list[dc_idx], self.cur_frame[dc_idx])
        self.e_savefilename[dc_idx].setText(filename)
        
        fpath += "/%s" % filename
        fits.writeto(fpath, self.img[dc_idx], self.header[dc_idx], overwrite=True, output_verify="ignore")
    
    
    def open_path(self, dc_idx):
        loader = self.e_path[dc_idx].text()
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", loader)
        if folder:
            self.e_path[dc_idx].setText(folder)
    
    
    def open_calilbration(self):
        if self.chk_open_calibration.isChecked():
            self.setGeometry(0, 0, 1315, 700)
        else:
            self.setGeometry(0, 0, 1030, 700)
            
        self.power_onoff(MOTOR, ON)
    

    def QWidgetLabelColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QLabel {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QLabel {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)    

    
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
        btn_name = self.bt_run.text()
        self.cal_stop_clicked = False
        if btn_name == "STOP":
            self.cal_stop_clicked = True
            self.cal_mode = False
        elif btn_name == "RUN":
            self.cal_mode = True
            self.cal_cur = 0
            self.bt_run.setText("STOP")
            self.QWidgetBtnColor(self.bt_run, "yellow", "blue")
        
            self.cal_run_cycle()   
        
            
    def cal_run_cycle(self):
        
        cal_cnt = 0
        for cal_cnt in range(self.cal_cur, CAL_CNT):
            if self.cal_chk[cal_cnt].isChecked():
                self.cal_cur = cal_cnt
                self.func_motor(cal_cnt)   #need to check
                if cal_cnt > 0 and self.cal_chk[cal_cnt-1].isChecked:
                    self.QWidgetCheckBoxColor(self.cal_chk[cal_cnt-1], "black")                    
                    self.QWidgetEditColor(self.cal_e_exptime[cal_cnt-1], "black")
                    self.QWidgetEditColor(self.cal_e_repeat[cal_cnt-1], "black")
                self.QWidgetCheckBoxColor(self.cal_chk[cal_cnt], "blue") 
                self.QWidgetEditColor(self.cal_e_exptime[cal_cnt], "blue")
                self.QWidgetEditColor(self.cal_e_repeat[cal_cnt], "blue")
                break
        
        if cal_cnt >= CAL_CNT-1 or self.cal_cur >= CAL_CNT:
            self.bt_run.setText("RUN")
            self.QWidgetBtnColor(self.bt_run, "black", "white")
            self.QWidgetCheckBoxColor(self.cal_chk[self.cal_cur-1], "black") 
            self.QWidgetEditColor(self.cal_e_exptime[self.cal_cur-1], "black")
            self.QWidgetEditColor(self.cal_e_repeat[self.cal_cur-1], "black")
            
            self.cal_mode = False
            
            
    def get_pwr_sts(self):
        msg = "%s %s %s" % (HK_REQ_PWR_STS, self.com_list[PDU], DT)
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg, True)


    def power_onoff(self, idx, onoff):
        msg = "%s %s %s %d %s" % (HK_REQ_PWR_ONOFF, self.com_list[PDU], DT, idx, onoff)
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg, True) 


    def func_lamp(self, idx, off=False):  
        if off:
            self.power_onoff(FLAT, OFF)
        else:
            self.power_onoff(FLAT, LAMP_FLAT[idx])
        
        if off:
            self.power_onoff(THAR, OFF)
        else:
            self.power_onoff(THAR, LAMP_FLAT[idx])
                        
            
    def func_motor(self, idx):
        self.ut_moved = False
        msg = "%s %s %d" % (DT_REQ_MOVEMOTOR, self.com_list[UT], MOTOR_UT_POS[idx])
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
                
        self.lt_moved = False
        msg = "%s %s %d" % (DT_REQ_MOVEMOTOR, self.com_list[LT], MOTOR_LT_POS[idx])
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
        
        
    def motor_init(self, motor):
        if motor == UT:
            self.protect_btn_ut(False)
            self.QWidgetBtnColor(self.bt_ut_motor_init, "yellow", "blue")
            self.bt_ut_motor_init.setEnabled(False)
        elif motor == LT:
            self.protect_btn_lt(False)
            self.QWidgetBtnColor(self.bt_lt_motor_init, "yellow", "blue")
            self.bt_lt_motor_init.setEnabled(False)
            
        msg = "%s %s" % (DT_REQ_INITMOTOR, self.com_list[motor])
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
            

    def move_motor_delta(self, motor, direction): #motor-UT/LT, direction-prev, next
        if motor == UT:
            if direction == PREV:
                curpos = int(self.e_utpos.text()) - int(self.e_movinginterval.text())
                self.e_utpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORBACK, self.com_list[motor], curpos)
            else:
                curpos = int(self.e_utpos.text()) + int(self.e_movinginterval.text())
                self.e_utpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORGO, self.com_list[motor], curpos)
                
            self.protect_btn_ut(False)
            
        elif motor == LT:
            if direction == PREV:
                curpos = int(self.e_ltpos.text()) - int(self.e_movinginterval.text())
                self.e_ltpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORBACK, self.com_list[motor], curpos)
            else:
                curpos = int(self.e_ltpos.text()) + int(self.e_movinginterval.text())
                self.e_ltpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORGO, self.com_list[motor], curpos)
                
            self.protect_btn_lt(False)
                
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
                
    
    def motor_pos_set(self, motor, position): #motor-UT/LT, direction-UT(0/1), LT(0-3)
        if motor == UT:
            msg = "%s %s %d" % (DT_REQ_SETUT, self.com_list[motor], position)
        elif motor == LT:
            msg = "%s %s %d" % (DT_REQ_SETLT, self.com_list[motor], position)
            
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
    
    

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
        
    dt = MainWindow()
    dt.show()
        
    app.exec()