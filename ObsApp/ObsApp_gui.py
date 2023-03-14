# -*- coding: utf-8 -*-

"""
Created on Oct 21, 2022

Modified on Mar 10, 2023

@author: hilee
"""

import sys, os
from ui_ObsApp import *
from ObsApp_def import *

import threading

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Libs.MsgMiddleware import *
from Libs.logger import *
import Libs.SetConfig as sc

import subprocess

import time as ti

import numpy as np
import astropy.io.fits as fits 
import Libs.zscale as zs

#import glob

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

label_list = ["tmc1-a",
              "tmc1-b",
              "tmc2-a",
              "tmc2-b",
              "tmc3-a",
              "tmc3-b",
              "tm-1",
              "tm-2",
              "tm-3",
              "tm-4",
              "tm-5",
              "tm-6",
              "tm-7",
              "tm-8"]

class DtvalueFromLabel:
    def __init__(self, key_to_label, values_dict):
        self._key_to_label = key_to_label
        self._label_to_key = dict((v, k) for (k, v) in list(key_to_label.items()))
        self._values_dict = values_dict

    def __getitem__(self, label):
        k = self._label_to_key.get(label, None)
        return self._values_dict.get(k, DEFAULT_VALUE)

    def as_dict(self):
        return dict((l, float(self._values_dict.get(k, DEFAULT_VALUE)))
                    for l, k in list(self._label_to_key.items()) if l)
class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, simul):
        super().__init__()
        
        #cmd = "%sworkspace/ics/ObsApp/InstSeq.py" % WORKING_DIR
        #self.proc_InstSeq = subprocess.Popen(["python", cmd, simul])
        
        self.setFixedSize(844, 596)
        
        self.iam = "ObsApp"
        self.simulation = bool(int(simul))
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        self.setWindowTitle("ObsApp 0.1")     
        
        # canvas        
        self.image_ax = []
        self.image_canvas = []
        for i in range(4):
            _image_fig = Figure(figsize=(4, 4), dpi=100)
            self.image_ax.append(_image_fig.add_subplot(111))
            _image_fig.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99) 
            self.image_canvas.append(FigureCanvas(_image_fig))
            
        vbox_svc = QVBoxLayout(self.frame_svc)
        vbox_svc.addWidget(self.image_canvas[IMG_SVC])
        vbox_svc = QVBoxLayout(self.frame_expand)
        vbox_svc.addWidget(self.image_canvas[IMG_EXPAND])
        vbox_svc = QVBoxLayout(self.frame_fitting)
        vbox_svc.addWidget(self.image_canvas[IMG_FITTING])
        vbox_svc = QVBoxLayout(self.frame_profile)
        vbox_svc.addWidget(self.image_canvas[IMG_PROFILE])
        
        #---------------------------------------------------------
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
              
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.InstSeq_ObsApp_ex = cfg.get(MAIN, 'main_gui_exchange')
        self.InstSeq_ObsApp_q = cfg.get(MAIN, 'main_gui_routing_key')
        self.ObsApp_InstSeq_ex = cfg.get(MAIN, 'gui_main_exchange')     
        self.ObsApp_InstSeq_q = cfg.get(MAIN, 'gui_main_routing_key')
        
        self.ObsApp_sub_ex = cfg.get(MAIN, "hk_sub_exchange")     
        self.ObsApp_sub_q = cfg.get(MAIN, "hk_sub_routing_key")
                
        self.ObsApp_svc_ex = cfg.get(DT, 'dt_dcs_exchange')     
        self.ObsApp_svc_q = cfg.get(DT, 'dt_dcs_routing_key')
        
        self.Period = int(cfg.get(HK,'hk-monitor-intv'))
        
        self.logpath = cfg.get(HK,'hk-log-location')
        
        self.sub_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "uploader"]
        self.com_status = [False for _ in range(COM_CNT)]
        self.power_status = [OFF for _ in range(PDU_IDX)]
        
        key_to_label = {}
        self.temp_normal, self.temp_lower, self.temp_upper = {},{},{}
        for k in label_list:
            hk_list = cfg.get(HK, k).split(",")
            key_to_label[k] = hk_list[0]
            self.temp_lower[k] = hk_list[1]
            self.temp_normal[k] = hk_list[2]
            self.temp_upper[k] = hk_list[3]
            
        self.dtvalue = dict()
        self.dtvalue_from_label = DtvalueFromLabel(key_to_label, self.dtvalue)
        
        self.dpvalue = DEFAULT_VALUE
        for key in key_to_label:
            self.dtvalue[key] = DEFAULT_VALUE
            
        self.heatlabel = dict() #heat value
        for i in range(6):
            if i != 4:
                self.heatlabel[label_list[i]] = DEFAULT_VALUE
                
        self.uploade_start = 0
            
        self.producer = [None for _ in range(SERV_CONNECT_CNT)]    # for Inst. Sequencer, Sub, DCS 
        
        self.param_InstSeq = ""
        self.param_svc = ""
        
        self.alarm_status = ALM_OK
        self.alarm_status_back = None
        
        #--------------------------------
        # 0 - H_K, 1 - SVC
        
        self.dcss_ready = False
        self.cur_cnt = 0
        
        self.temp_cnt = 0
        
        self.svc_mode = SINGLE_MODE
        self.cal_waittime = [0, 0]
        self.stop_clicked = False   # for continuous mode
        
        self.svc_header = None
        self.svc_img = None
                
        # progress bar     
        self.prog_timer = [None, None]
        self.cur_prog_step = [None, None]
        
        # elapsed
        self.elapsed_obs_timer = None
        self.elapsed_obs = None
        self.measure_T = 0
        #--------------------------------
        
        self.init_events() 
        
        # Instrument Status
        self.label_is_health.setText("---")
        self.label_GDSN_connection.setText("---")
        self.label_GMP_connection.setText("---")
        self.label_state.setText("Idle")
        self.label_action_state.setText("---")        
        
        self.label_vacuum.setText("---")
        self.label_temp_detH.setText("---")
        self.label_temp_detK.setText("---")
        self.label_temp_detS.setText("---")
        self.label_heater_detH.setText("---")
        self.label_heater_detK.setText("---")
        self.label_heater_detS.setText("---")   
        
        # Science Observation
        self.label_data_label.setText("---")
        self.label_obs_state.setText("Idle")
        self.label_sampling_number.setText("---")
        self.label_exp_time.setText("---")
        self.label_time_left.setText("---")
        self.label_IPA.setText("---") 
        
        # Slit View Camera
        self.label_svc_filename.setText("---")
        self.label_svc_state.setText("---")
        self.e_svc_fowler_number.setText("16")
        self.e_svc_exp_time.setText("1.63")
        
        self.bt_single.setText("Single")    # Single/Abort
        self.bt_continuous.setText("Continuous")    #Continuous/Stop
        
        # temp
        fname = ti.strftime("SDCS_%02Y%02m%02d_", ti.localtime())
        self.e_repeat_file_name.setText(fname)
        self.e_repeat_number.setText("5")
        
        self.e_offset.setText("1")
        
        self.radio_raw.setChecked(True)
        self.radio_zscale.setChecked(True)
        
        self.label_zscale.setText("---")
        self.e_mscale_min.setText("1000")
        self.e_mscale_max.setText("5000")   
                
        # connect to rabbitmq
        self.connect_to_server_ObsApp_ex()
        self.connect_to_server_InstSeq_q()
        
        self.connect_to_server_hk_ex()
        self.connect_to_server_sub_q()
        
        self.connect_to_server_dt_ex()
        self.connect_to_server_svc_q()
        
        self.InstSeq_data_processing()
        
        self.monit_timer = QTimer(self)
        self.monit_timer.setInterval(self.Period)
        self.monit_timer.timeout.connect(self.LoggingFun)
        
        self.show_sub_timer = QTimer(self)
        self.show_sub_timer.setInterval(0.1)
        self.show_sub_timer.timeout.connect(self.InstSeq_data_processing)
        
        self.show_sub_timer = QTimer(self)
        self.show_sub_timer.setInterval(self.Period/2)
        self.show_sub_timer.timeout.connect(self.sub_data_processing)
        
        self.show_dcs_timer = QTimer(self)
        self.show_dcs_timer.setInterval(0.1)
        self.show_dcs_timer.timeout.connect(self.svc_data_processing)     
        self.show_dcs_timer.start()
                
        self.startup()
        
        
    def closeEvent(self, event: QCloseEvent) -> None:        
        
        self.monit_timer.stop()
        self.show_sub_timer.stop()
        
        self.log.send(self.iam, DEBUG, "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, DEBUG, "This may take several seconds waiting for threads to close")       

        pwr_list = [OFF, OFF, OFF, OFF, OFF, OFF, OFF, OFF]
        self.power_onoff(pwr_list)
        ti.sleep(5)
                
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.") 
        
        self.producer[INST_SEQ].send_message(self.ObsApp_InstSeq_q, EXIT)  

        for i in range(SERV_CONNECT_CNT):
            if self.producer[i] != None:
                self.producer[i].__del__()
        self.producer[HK_SUB] = None

        #if self.proc_InstSeq != None:
        #    self.proc_InstSeq.terminate()
        #    self.log.send(self.iam, INFO, str(self.proc_InstSeq.pid) + " exit")
                    
        self.log.send(self.iam, DEBUG, "Closed!") 
        
        return super().closeEvent(event)
    
    
    def init_events(self):
        self.bt_single.clicked.connect(self.single)
        self.bt_continuous.clicked.connect(self.continuous)
        
        self.bt_repeat_filesave.clicked.connect(self.repeat_filesave)
        
        self.bt_center.clicked.connect(self.set_center)
        self.bt_set_guide_star.clicked.connect(self.set_guide_star)
        
        self.bt_plus_p.clicked.connect(lambda: self.move_p(True))
        self.bt_minus_p.clicked.connect(lambda: self.move_p(False))
        self.bt_plus_q.clicked.connect(lambda: self.move_p(True))
        self.bt_minus_q.clicked.connect(lambda: self.move_p(False))
        
        self.bt_slow_guide.clicked.connect(self.slow_guide)
        self.bt_stop_guide.clicked.connect(self.stop_guide)
        
        self.bt_single.setEnabled(False)
        
        
    #--------------------------------------------------------
    # ObsApp -> Inst. Sequencer
    def connect_to_server_ObsApp_ex(self):
        self.producer[INST_SEQ] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_InstSeq_ex)      
        self.producer[INST_SEQ].connect_to_server()
        self.producer[INST_SEQ].define_producer()
    
    
    #--------------------------------------------------------
    # Inst. Sequencer -> ObsApp
    def connect_to_server_InstSeq_q(self):
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ObsApp_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.InstSeq_ObsApp_q, self.callback_InstSeq)       
        
        th = threading.Thread(target=consumer.start_consumer)
        th.daemon = True
        th.start()
    
    
    def callback_InstSeq(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        self.param_InstSeq = cmd
        
    
    #--------------------------------------------------------
    # ObsApp -> hardware subsystems
    def connect_to_server_hk_ex(self):
        self.producer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_sub_ex)      
        self.producer[HK_SUB].connect_to_server()
        self.producer[HK_SUB].define_producer()
    
    
    #--------------------------------------------------------
    # hardware subsystems -> ObsApp
    def connect_to_server_sub_q(self):
        sub_ObsApp_ex = [self.sub_list[i]+'.ex' for i in range(SUB_CNT)]
        consumer = [None for _ in range(SUB_CNT)]
        for idx in range(SUB_CNT):
            consumer[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_ObsApp_ex[idx])              
            consumer[idx].connect_to_server()
                
        consumer[TMC1].define_consumer(self.sub_list[TMC1]+'.q', self.callback_tmc1)       
        consumer[TMC2].define_consumer(self.sub_list[TMC2]+'.q', self.callback_tmc2)
        consumer[TMC3].define_consumer(self.sub_list[TMC3]+'.q', self.callback_tmc3)
        consumer[TM].define_consumer(self.sub_list[TM]+'.q', self.callback_tm)
        consumer[VM].define_consumer(self.sub_list[VM]+'.q', self.callback_vm)
        consumer[PDU].define_consumer(self.sub_list[PDU]+'.q', self.callback_pdu)
        consumer[UPLOADER].define_consumer(self.sub_list[UPLOADER]+'.q', self.callback_uploader)
        
        for idx in range(SUB_CNT):
            th = threading.Thread(target=consumer[idx].start_consumer)
            th.daemon = True
            th.start()
            
            
    def callback_tmc1(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TMC1] = bool(int(param[1]))            
        
        elif param[0] == HK_REQ_GETVALUE:
            self.dtvalue[label_list[0]] = self.judge_value(param[1])
            self.dtvalue[label_list[1]] = self.judge_value(param[2])
            
            self.heatlabel[label_list[0]] = self.judge_value(param[3])
            self.heatlabel[label_list[1]] = self.judge_value(param[4])

            
    
    def callback_tmc2(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TMC2] = bool(int(param[1]))            
        
        elif param[0] == HK_REQ_GETVALUE:
            self.dtvalue[label_list[2]] = self.judge_value(param[1])
            self.dtvalue[label_list[3]] = self.judge_value(param[2])
            self.heatlabel[label_list[2]] = self.judge_value(param[3])
            self.heatlabel[label_list[3]] = self.judge_value(param[4])
            
    
    def callback_tmc3(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TMC3] = bool(int(param[1]))            
        
        elif param[0] == HK_REQ_GETVALUE:
            self.dtvalue[label_list[4]] = self.judge_value(param[1])
            self.dtvalue[label_list[5]] = self.judge_value(param[2])
            self.heatlabel[label_list[5]] = self.judge_value(param[3])
            
            
    def callback_tm(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[TM] = bool(int(param[1]))            
        
        elif param[0] == HK_REQ_GETVALUE:
            for i in range(TM_CNT):
                self.dtvalue[label_list[TM_1+i]] = self.judge_value(param[i+1])

    
    def callback_vm(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        if len(cmd) < 80:
            self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[VM] = bool(int(param[1]))            
            
        elif param[0] == HK_REQ_GETVALUE:
            if len(param[1]) > 10 or param[1] == DEFAULT_VALUE:
                self.dpvalue = DEFAULT_VALUE
            else:
                self.dpvalue = param[1]
        
    
    def callback_pdu(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[PDU] = bool(int(param[1]))            
            
        elif param[0] == HK_REQ_PWR_STS:
            self.power_status[0] = param[1] 
            self.power_status[1] = param[2]
            if self.power_status[0] == OFF or self.power_status[1] == OFF:
                pass 
            
    
    def callback_uploader(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_UPLOAD_STS:
            pass            
        
    #--------------------------------------------------------
    # ObsApp -> DC core
    def connect_to_server_dt_ex(self):
        self.producer[DCSS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_svc_ex)      
        self.producer[DCSS].connect_to_server()
        self.producer[DCSS].define_producer()
    
    
    #--------------------------------------------------------
    # DC core -> ObsApp
    def connect_to_server_svc_q(self):
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, "DCSS.ex")      
        consumer.connect_to_server()
        consumer.define_consumer("DCSS.q", self.callback_svc)       
        
        th = threading.Thread(target=consumer.start_consumer)
        th.daemon = True
        th.start()
                
        
    def callback_svc(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        self.param_svc = cmd       
            

    #--------------------------------------------------------
    # sub process
    
    def sendTomain_status(self):        
        if self.alarm_status_back == self.alarm_status:            
            return
        msg = "%s %s" % (SUB_STATUS, self.alarm_status)
        self.producer[INST_SEQ].send_message(self.ObsApp_InstSeq_q, msg)
        self.alarm_status_back = self.alarm_status
        
            
    def startup(self):      
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, HK_REQ_PWR_STS) 
        
        pwr_list = [ON, ON, OFF, OFF, OFF, OFF, OFF, OFF]
        self.power_onoff(pwr_list)
                                            
        self.uploade_start = ti.time()   
        self.monit_timer.start()
        self.show_sub_timer.start()
        
        self.send_to_SVC(CMD_INIT2_DONE)
                                    
        
    def power_onoff(self, args):
        pwr_list = ""
        for i in range(PDU_IDX):
            pwr_list += args[i] + " "
        msg = "%s %s" % (HK_REQ_PWR_ONOFF, pwr_list)
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg)
        
        
    def LoggingFun(self):     
        fname = ti.strftime("%Y%m%d", ti.localtime())+".log"
        self.log.createFolder(self.logpath)
        f_p_name = self.logpath+fname
        if os.path.isfile(f_p_name):
            file=open(f_p_name,'a+')
        else:
            file=open(f_p_name,'w')

        hk_entries = [self.dpvalue,
                      self.dtvalue_from_label["bench"],     self.heatlabel["tmc1-a"],
                      self.dtvalue_from_label["grating"],   self.heatlabel["tmc1-b"],
                      self.dtvalue_from_label["detS"],      self.heatlabel["tmc2-a"],
                      self.dtvalue_from_label["detK"],      self.heatlabel["tmc2-b"],
                      self.dtvalue_from_label["camH"],    
                      self.dtvalue_from_label["detH"],      self.heatlabel["tmc3-b"],
                      self.dtvalue_from_label["benchcenter"],    
                      self.dtvalue_from_label["coldhead01"],
                      self.dtvalue_from_label["coldhead02"],    
                      self.dtvalue_from_label["coldstop"],    
                      self.dtvalue_from_label["charcoalBox"],
                      self.dtvalue_from_label["camK"],    
                      self.dtvalue_from_label["shieldtop"],  
                      self.dtvalue_from_label["air"]]  

        #alert_status = "On(T>%d)" % self.alert_temperature
        alert_status = "On"
        hk_entries.append(alert_status)

        # hk_entries to string
        updated_datetime = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
        str_log1 = "\t".join([updated_datetime] + list(map(str, hk_entries))) + "\n"    
        file.write(str_log1)
        file.close()

        upload = ti.time() - self.uploade_start
        #print("Logging time:", upload)
        if upload >= LOGGING_INTERVAL:            
            str_log = "    ".join([updated_datetime] + list(map(str, hk_entries)))     
            msg = "%s %s" % (HK_REQ_UPLOAD_DB, str_log)
            self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg)
            
            self.uploade_start = ti.time()


    def judge_value(self, input):
        if input != DEFAULT_VALUE:
            value = "%.2f" % float(input)
        else:
            value = input

        return value
    
    
    #--------------------------------------------------------
    # dcss command
    def send_to_SVC(self, cmd, param=""):
        msg = "%s %s %d" % (cmd, "DCSS", self.simulation)
        if param != "":
            msg += " " + param
        self.producer[DCSS].send_message(self.ObsApp_svc_q, msg) 
        
    
    def set_fs_param(self, first=False):     
        if not self.dcss_ready:
            return

        self.enable_dcss(False)  

        #setparam
        _exptime = float(self.e_svc_exp_time.text())
        _FS_number = int(self.e_svc_fowler_number.text())
        _fowlerTime = _exptime - T_frame * _FS_number
        _cal_waittime = T_br + (T_frame + _fowlerTime + (2 * T_frame * _FS_number))
            
        start_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())       
        
        self.label_svc_state.setText("Running")

        # progress bar 
        self.prog_timer[SVC] = QTimer(self)
        self.prog_timer[SVC].setInterval(int(_cal_waittime*10))   
        self.prog_timer[SVC].timeout.connect(lambda: self.show_progressbar(SVC))    

        self.cur_prog_step[SVC] = 0
        self.progressBar_svc.setValue(self.cur_prog_step[SVC])    
        self.prog_timer[SVC].start()    
        
        if first:
            cmd = CMD_SETFSPARAM_ICS
            msg = "%.3f 1 %d 1 %.3f 1" % (_exptime, _FS_number, _fowlerTime)
        else:
            cmd = CMD_ACQUIRERAMP_ICS
            msg = ""
        self.send_to_SVC(cmd, msg)

        
    def abort_acquisition(self):
        if self.cur_prog_step[SVC] > 0:
            self.prog_timer[SVC].stop()
              
        self.send_to_SVC(CMD_STOPACQUISITION)  
    
    
    def load_data(self, folder_name):
        
        self.label_svc_state.setText("Transfer")
        
        try:
            filepath = ""
            if self.simulation:
                filepath = "%sIGRINS/Demo/SDCS_demo.fits" % WORKING_DIR
            else:
                filepath = "%sIGRINS/dcss/Fowler/%s/Result/FowlerResult.fits" % (WORKING_DIR, folder_name)

            frm = fits.open(filepath)
            data = frm[0].data
            self.svc_header = frm[0].header
            _img = np.array(data, dtype = "f")
            #_img = np.flipud(np.array(data, dtype = "f"))
            self.svc_img = _img#[0:FRAME_Y, 0:FRAME_X]
            #self.img = _img
            
            self.zmin, self.zmax = zs.zscale(self.svc_img)
            range = "%d ~ %d" % (self.zmin, self.zmax)
            
            self.label_zscale.setText(range)
        
            self.mmin, self.mmax = np.min(self.svc_img[SVC]), np.max(self.svc_img[SVC])
            self.e_mscale_min.setText("%.1f" % self.mmin)
            self.e_mscale_max.setText("%.1f" % self.mmax)
                
            #if self.chk_autosave.isChecked():
            #    self.save_fits(dc_idx)
            
            self.reload_img()
        
        except:
            self.svc_img = None
            self.log.send(self.iam, WARNING, "No image")    
            
            
    def reload_img(self):
        
        try:
            #_img = np.flipud(self.img[dc_idx])
            #_img = np.fliplr(np.rot90(self.img[dc_idx])
            
            _img = self.svc_img
                            
            _min, _max = 0, 0
            if self.radio_zscale.isChecked():
                _min, _max = self.zmin, self.zmax
            elif self.radio_mscale.isChecked():
                _min, _max = self.mmin, self.mmax
                                
            self.image_ax[IMG_SVC].imshow(_img, vmin=_min, vmax=_max, cmap='gray', origin='lower')
            self.image_canvas[IMG_SVC].draw()
            
            self.label_svc_state.setText("Idle")
                
        except:
            self.svc_img = None
            self.log.send(self.iam, WARNING, "No image")
        
    
    #--------------------------------------------------------
    # gui set
    def QShowValue(self, widget, label, limit):
        value = self.dtvalue[label]
        if value == DEFAULT_VALUE:
            self.QWidgetLabelColor(widget, "dimgray")
            self.alarm_status = ALM_ERR
            msgbar = "%s is %s!!!" % (label, self.alarm_status)
            
        elif abs(float(self.temp_normal[label]) - float(value)) < limit:
            self.QWidgetLabelColor(widget, "green")
            self.alarm_status = ALM_OK
            msgbar = ""
            
        elif float(self.temp_lower[label]) <= float(value) <= float(self.temp_upper[label]):
            self.QWidgetLabelColor(widget, "gold")
            self.alarm_status = ALM_WARN
            msgbar = "%s temperature %s!!!" % (label, self.alarm_status)
            
        elif float(self.temp_upper[label]) < float(value):
            self.QWidgetLabelColor(widget, "red")
            self.alarm_status = ALM_FAT
            msgbar = "%s temperature is too high!!!" % label 
            
        widget.setText(value)
        self.label_messagebar.setText(msgbar)
        
    
    def QWidgetLabelColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QLabel {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QLabel {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
            
            
    def QWidgetBtnColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QPushButton {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QPushButton {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
          
    #--------------------------------------------------------
    # button, event
    def single(self):
        if self.bt_single.text() == "Single":
            self.svc_mode = SINGLE_MODE
            self.QWidgetBtnColor(self.bt_single, "yellow", "blue")
            self.bt_single.setText("Abort")
            
            self.set_fs_param(True)
            
        else:            
            self.abort_acquisition()         
    
    
    def continuous(self):
        if self.bt_continuous.text() == "Continuous":
            self.svc_mode = CONT_MODE
            self.QWidgetBtnColor(self.bt_continuous, "yellow", "blue")
            self.bt_continuous.setText("Stop")
            
            self.stop_clicked = False
            self.set_fs_param(True)
            
        else:            
            self.stop_clicked = True
            
        
        
    def repeat_filesave(self):
        pass
    
    
    def set_center(self):
        pass
    
    
    def set_guide_star(self):
        pass
        
        
    def move_p(self, north): #+:True, -:Minus 
        pass
    
    
    def move_q(self, west): #+:True, -:Minus 
        pass
    
    
    def slow_guide(self):
        pass
 
 
    def stop_guide(self):
        pass
    
    
    def show_progressbar(self, dc_idx):
        if self.cur_prog_step[dc_idx] >= 100:
            self.prog_timer[dc_idx].stop()
            return
        
        self.cur_prog_step[dc_idx] += 1
        if dc_idx == SVC:
            self.progressBar_svc.setValue(self.cur_prog_step[dc_idx])
        else:
            self.progressBar_obs.setValue(self.cur_prog_step[dc_idx])

    
    # for HK
    def show_elapsed(self):
        if self.elapsed_obs <= 0:
            self.elapsed_obs_timer.stop()
            return
        
        self.elapsed_obs -= 0.001
        msg = "%.3f sec" % self.elapsed_obs
        self.label_time_left.setText(msg)
        
        
    def enable_dcss(self, enable):
        self.e_svc_fowler_number.setEnabled(enable)
        self.e_svc_exp_time.setEnabled(enable)
        if self.svc_mode != SINGLE_MODE:
            self.bt_single.setEnabled(enable)
        if self.svc_mode != CONT_MODE:
            self.bt_continuous.setEnabled(enable)
        
        self.chk_auto_save.setEnabled(enable)
        self.e_repeat_file_name.setEnabled(enable)
        self.bt_repeat_filesave.setEnabled(enable)
        self.e_repeat_number.setEnabled(enable)
        
        self.bt_center.setEnabled(enable)
        self.bt_set_guide_star.setEnabled(enable)
        self.chk_off_slit.setEnabled(enable)
    
        self.bt_plus_p.setEnabled(enable)
        self.bt_plus_q.setEnabled(enable)
        self.bt_minus_p.setEnabled(enable)
        self.bt_minus_q.setEnabled(enable)
        self.e_offset.setEnabled(enable)
        
        self.bt_slow_guide.setEnabled(enable)
        self.bt_stop_guide.setEnabled(enable)
        
        
    
    
    #--------------------------------------------------------------
    # thread - with GUI
            
    def InstSeq_data_processing(self):        
        if self.param_InstSeq == "":
            return
        
        param = self.param_InstSeq.split()
            
        if param[0] == SHOW_TCS_INFO:
            pass
                    
        elif param[0] == CMD_SETFSPARAM_ICS:
            if param[1] == "DCSS":
                self.e_svc_exp_time.setText(param[3])
                self.e_svc_fowler_number.setText(param[5])
                _fowlerTime = float(param[7])
                self.cal_waittime[SVC] = T_br + (T_frame + _fowlerTime + (2 * T_frame * int(param[5])))
            else:
                self.label_exp_time.setText(param[3])
                self.label_sampling_number.setText(param[5])
                _fowlerTime = float(param[7])
                self.cal_waittime[H_K] = T_br + (T_frame + _fowlerTime + (2 * T_frame * int(param[5])))
                
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            if param[1] == "DCSS":
                #SVC progressbar
                self.prog_timer[SVC] = QTimer(self)
                self.prog_timer[SVC].setInterval(int(self.cal_waittime[SVC]*10))   
                self.prog_timer[SVC].timeout.connect(lambda: self.show_progressbar(SVC)) 
                
                self.cur_prog_step[SVC] = 0
                self.progressBar_obs.setValue(self.cur_prog_step[SVC])    
                self.prog_timer[SVC].start()   
            else:
                #H, K progressbar
                self.prog_timer[H_K] = QTimer(self)
                self.prog_timer[H_K].setInterval(int(self.cal_waittime[H_K]*10))   
                self.prog_timer[H_K].timeout.connect(lambda: self.show_progressbar(H_K)) 
                
                self.cur_prog_step[H_K] = 0
                self.progressBar_obs.setValue(self.cur_prog_step[H_K])    
                self.prog_timer[H_K].start() 
                
                # elapsed               
                self.elapsed_obs_timer = QTimer(self) 
                self.elapsed_obs_timer.setInterval(0.001)
                self.elapsed_obs_timer.timeout.connect(self.show_elapsed)

                self.elapsed_obs = self.cal_waittime[H_K]
                self.label_time_left.setText(self.elapsed_obs)    
                self.elapsed_obs_timer.start()
                
        elif param[0] == CMD_COMPLETED:
            if param[1] == "DCSS":
                self.prog_timer[SVC].stop()
            else:
                self.prog_timer[H_K].stop()
                self.elapsed_obs_timer.stop()
                
        self.param_InstSeq = "" 
                            
                        
    def sub_data_processing(self):
        # communication port error                       
        for idx in range(COM_CNT):
            if not self.com_status[idx]:
                self.alarm_status = ALM_ERR
                self.sendTomain_status()
            break 
                       
        # show value and color                    
        self.QShowValue(self.label_temp_detS, label_list[TMC2_A], 0.1)
        self.QShowValue(self.label_temp_detK, label_list[TMC2_B], 0.1)
        self.label_heater_detS.setText(self.heatlabel[label_list[TMC2_A]])
        self.label_heater_detK.setText(self.heatlabel[label_list[TMC2_B]])
        
        self.QShowValue(self.label_temp_detH, label_list[TMC3_B], 0.1)
        self.label_heater_detH.setText(self.heatlabel[label_list[TMC3_B]])
                        
        # from VM
        self.label_vacuum.setText(self.dpvalue)
        
            
    def svc_data_processing(self):        
        if self.param_svc == "":
            return
        
        param = self.param_svc.split()
        
        if param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS:
            self.dcss_ready = True
            self.bt_single.setEnabled(True)

        elif param[0] == CMD_SETFSPARAM_ICS or param[0] == CMD_ACQUIRERAMP_ICS:   
            
            #temp
            self.temp_cnt += 1
            fname = ti.strftime("SDCS_%02Y%02m%02d_", ti.localtime()) + str(self.temp_cnt)
            self.e_repeat_file_name.setText(fname)
            self.label_svc_filename.setText(fname)  
            
            self.cur_cnt += 1            
            self.label_svc_state.setText("Done")
            
            self.cur_prog_step[SVC] = 100
            self.progressBar_svc.setValue(self.cur_prog_step[SVC])
            
            self.load_data(param[2])
            
            if self.svc_mode == CONT_MODE:
                if self.stop_clicked:
                    self.stop_clicked = False
                    
                    self.cur_cnt = 0
                    self.QWidgetBtnColor(self.bt_continuous, "black", "white")
                    self.bt_continuous.setText("Continuous")
                    self.enable_dcss(True)
                    
                    self.param_svc = ""
                    return
            
                if self.cur_cnt < int(self.e_repeat_number.text()):
                    # calculate offset
                    pass
                
                self.set_fs_param()

            else:
                self.QWidgetBtnColor(self.bt_single, "black", "white")
                self.bt_single.setText("Single")
                self.enable_dcss(True)
                
        elif param[0] == CMD_STOPACQUISITION:   # for single mode
            self.QWidgetBtnColor(self.bt_single, "black", "white")
            self.bt_single.setText("Single")
            self.enable_dcss(True)
            
        self.param_svc = ""
    


if __name__ == "__main__":
    
    app = QApplication()
    ObsApp = MainWindow(sys.argv[1])
    ObsApp.show()
        
    app.exec()