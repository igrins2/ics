# -*- coding: utf-8 -*-

"""
Created on Oct 21, 2022

Modified on , 2022

@author: hilee
"""

import sys, os
from ui_ObsApp import *
from ObsApp_def import *

from concurrent import futures

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Libs.hk_field_definition import hk_entries_to_dict

from Libs.MsgMiddleware import *
from Libs.logger import *
import Libs.SetConfig as sc

import subprocess

import time as ti

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
    
    def __init__(self, simul='0'):
        super().__init__()
        
        cmd = "%sworkspace/ics/ObsApp/InstSeq.py" % WORKING_DIR
        self.proc_InstSeq = subprocess.Popen(["python", cmd, simul])
        
        self.iam = "ObsApp"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        self.setWindowTitle("ObsApp 0.1")
        
        self.init_events()      
        
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
        self.sub_ObsApp_ex = cfg.get(MAIN, "sub_hk_exchange")
        self.sub_ObsApp_q = cfg.get(MAIN, "sub_hk_routing_key")
        
        self.alert_temperature = int(cfg.get(HK, "hk-alert-temperature"))
        
        self.ObsApp_svc_ex = cfg.get(DT, 'dt_dcs_exchange')     
        self.ObsApp_svc_q = cfg.get(DT, 'dt_dcs_routing_key')
        self.svc_ObsApp_ex = cfg.get(DT, 'dcs_dt_exchange')
        self.svc_ObsApp_q = cfg.get(DT, 'dcs_dt_routing_key')
        
        self.Period = int(cfg.get(HK,'hk-monitor-intv'))
        
        self.logpath = cfg.get(HK,'hk-log-location')
        
        self.com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "uploader"]
        self.power_status = [OFF for _ in range(PDU_IDX)]
        
        self.key_to_label = {}
        for k in label_list:
            self.key_to_label[k] = cfg.get(HK, k)
            
        self.dtvalue = dict()
        self.dtvalue_from_label = DtvalueFromLabel(self.key_to_label, self.dtvalue)
        
        self.dpvalue = DEFAULT_VALUE
        for key in self.key_to_label:
            self.dtvalue[key] = DEFAULT_VALUE
            
        self.heatlabel = dict() #heat value
        for i in range(6):
            if i != 4:
                self.heatlabel[label_list[i]] = DEFAULT_VALUE
                
        self.uploade_start = 0
            
        self.producer = [None for _ in range(SERV_CONNECT_CNT)]
        self.consumer = [None for _ in range(SERV_CONNECT_CNT)]
        
        self.param = ["" for _ in range(SERV_CONNECT_CNT)]
        
        #--------------------------------
        # 0 - H_K, 1 - SVC
        self.cal_waittime = [0, 0]
                
        # progress bar     
        self.prog_timer = [None, None]
        self.cur_prog_step = [None, None]
        
        # elapsed
        self.elapsed_obs_timer = None
        self.elapsed_obs = None
        self.measure_T = 0
        #--------------------------------
        
        self.InstSeq_ready = False
        
        self.label_vacuum.setText("---")
        self.label_temp_detH.setText("---")
        self.label_temp_detK.setText("---")
        self.label_temp_detS.setText("---")
        self.label_heater_detH.setText("---")
        self.label_heater_detK.setText("---")
        self.label_heater_detS.setText("---")    
                
        # connect to rabbitmq
        self.connect_to_server_ObsApp_ex()
        self.connect_to_server_InstSeq_q()
        
        self.connect_to_server_hk_ex()
        self.connect_to_server_sub_q()
        
        self.connect_to_server_dt_ex()
        self.connect_to_server_svc_q()
        
        #from Inst.Seq
        th = threading.Thread(target=self.InstSeq_data_processing)
        th.daemon = True
        th.start()
        
        #from subsystems
        th = threading.Thread(target=self.sub_data_processing)
        th.daemon = True
        th.start()
        
        #from SVC
        th = threading.Thread(target=self.svc_data_processing)
        th.daemon = True
        th.start()

        self.startup()
        
        
        
    def closeEvent(self, event: QCloseEvent) -> None:        
        
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, HK_STOP_MONITORING) 
        self.InstSeq_ready = False
        ti.sleep(2)

        self.log.send(self.iam, DEBUG, "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, DEBUG, "This may take several seconds waiting for threads to close")       

        for idx in range(PDU_IDX):
            if self.power_status[idx] == ON:
                self.power_onoff(idx+1)
                
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.") 
        
        self.producer[INST_SEQ].send_message(self.ObsApp_InstSeq_q, EXIT)  

        for i in range(SERV_CONNECT_CNT):
            if self.producer[i] != None:
                self.producer[i].__del__()
        self.producer[HK_SUB] = None
        
        if self.proc_InstSeq != None:
            self.proc_InstSeq.terminate()
            self.log.send(self.iam, INFO, str(self.proc_InstSeq.pid) + " exit")

        self.log.send(self.iam, DEBUG, "Closed!") 
        
        return super().closeEvent(event)
    
    
    def init_events(self):
        self.pushButton_single.clicked.connect(self.single)
        self.pushButton_continuous.clicked.connect(self.continous)
        
        self.pushButton_repeat_filesave.clicked.connect(self.repeat_filesave)
        
        self.pushButton_center.clicked.connect(self.set_center)
        self.pushButton_set_guide_star.clicked.connect(self.set_guide_star)
        
        self.pushButton_plus_p.clicked.connect(lambda: self.move_p(True))
        self.pushButton_minus_p.clicked.connect(lambda: self.move_p(False))
        self.pushButton_plus_q.clicked.connect(lambda: self.move_p(True))
        self.pushButton_minus_q.clicked.connect(lambda: self.move_p(False))
        
        self.pushButton_slow_guide.clicked.connect(self.slow_guide)
        self.pushButton_stop_guide.clicked.connect(self.stop_guide)
        
        
    #--------------------------------------------------------
    # ObsApp -> Inst. Sequencer
    def connect_to_server_ObsApp_ex(self):
        self.producer[INST_SEQ] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_InstSeq_ex)      
        self.producer[INST_SEQ].connect_to_server()
        self.producer[INST_SEQ].define_producer()
    
    
    #--------------------------------------------------------
    # Inst. Sequencer -> ObsApp
    def connect_to_server_InstSeq_q(self):
        self.consumer[INST_SEQ] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ObsApp_ex)      
        self.consumer[INST_SEQ].connect_to_server()
        self.consumer[INST_SEQ].define_consumer(self.InstSeq_ObsApp_q, self.callback_InstSeq)       
        
        th = threading.Thread(target=self.consumer[INST_SEQ].start_consumer)
        th.daemon = True
        th.start()
    
    
    def callback_InstSeq(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
    
        self.param[INST_SEQ] = cmd
        param = cmd.split()
        
        
    
    #--------------------------------------------------------
    # ObsApp -> hardware subsystems
    def connect_to_server_hk_ex(self):
        self.producer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_sub_ex)      
        self.producer[HK_SUB].connect_to_server()
        self.producer[HK_SUB].define_producer()
    
    
    #--------------------------------------------------------
    # hardware subsystems -> ObsApp
    def connect_to_server_sub_q(self):
        self.consumer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.sub_ObsApp_ex)      
        self.consumer[HK_SUB].connect_to_server()
        self.consumer[HK_SUB].define_consumer(self.sub_ObsApp_q, self.callback_sub)       
        
        th = threading.Thread(target=self.consumer[HK_SUB].start_consumer)
        th.daemon = True
        th.start()
        
        
    def callback_sub(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        if len(cmd) < 80:
            self.log.send(self.iam, INFO, msg)

        self.param[HK_SUB] = cmd
        param = cmd.split()
        
        if param[0] == HK_REQ_COM_STS:
            connected = bool(int(param[2]))
            if connected is False:   
                if param[1] == self.com_list[TMC1]:
                    pass
                elif param[1] == self.com_list[TMC2]:
                    pass
                elif param[1] == self.com_list[TMC3]:
                    pass
                elif param[1] == self.com_list[TM]:
                    pass
                elif param[1] == self.com_list[VM]:
                    pass
                elif param[1] == self.com_list[PDU]:
                    pass   

            ready_cnt = 0
            for i in range(COM_CNT-1):
                if self.com_list[i]:
                    ready_cnt += 1
            if ready_cnt == 6:
                self.InstSeq_ready = True

        elif param[0] == HK_REQ_GETVALUE:
            if param[1] == self.com_list[TMC1]:
                self.dtvalue[label_list[0]] = self.judge_value(param[2])
                self.dtvalue[label_list[1]] = self.judge_value(param[3])
                
                self.heatlabel[label_list[0]] = self.judge_value(param[4])
                self.heatlabel[label_list[1]] = self.judge_value(param[5])
            
            elif param[1] == self.com_list[TMC2]:
                self.dtvalue[label_list[2]] = self.judge_value(param[2])
                self.dtvalue[label_list[3]] = self.judge_value(param[3])
                self.heatlabel[label_list[2]] = self.judge_value(param[4])
                self.heatlabel[label_list[3]] = self.judge_value(param[5])
                
            elif param[1] == self.com_list[TMC3]:
                self.dtvalue[label_list[4]] = self.judge_value(param[2])
                self.dtvalue[label_list[5]] = self.judge_value(param[3])
                self.heatlabel[label_list[5]] = self.judge_value(param[4])
                
            elif param[1] == self.com_list[TM]:
                # for all
                for i in range(TM_CNT):
                    self.dtvalue[label_list[TM_1+i]] = self.judge_value(param[2+i])
                    
            elif param[1] == self.com_list[VM]:
                if len(param[2]) > 10 or param[2] == DEFAULT_VALUE:
                    self.dpvalue = DEFAULT_VALUE
                else:
                    self.dpvalue = param[2]

        # from PDU
        elif param[0] == HK_REQ_PWR_STS:
            self.power_status[0] = param[3] 
            self.power_status[1] = param[4]
            if self.power_status[0] == OFF or self.power_status[1] == OFF:
                pass 
            
        
    #--------------------------------------------------------
    # ObsApp -> DC core
    def connect_to_server_dt_ex(self):
        self.producer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_svc_ex)      
        self.producer[DCS].connect_to_server()
        self.producer[DCS].define_producer()
    
    
    #--------------------------------------------------------
    # DC core -> ObsApp
    def connect_to_server_svc_q(self):
        self.consumer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.svc_ObsApp_ex)      
        self.consumer[DCS].connect_to_server()
        self.consumer[DCS].define_consumer(self.svc_ObsApp_q, self.callback_svc)       
        
        th = threading.Thread(target=self.consumer[DCS].start_consumer)
        th.daemon = True
        th.start()
        
        
    def callback_svc(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        
        self.param[DCS] = cmd
    

    
    def startup(self):      
        print('startup')
        if self.InstSeq_ready == False:
            threading.Timer(1, self.startup).start()
            return            
        
        # power on
        self.get_pwr_sts() 
            
        for idx in range(PDU_IDX):
            if idx < 2:
                if self.power_status[idx] == OFF:
                    self.power_onoff(idx+1)
            else:
                if self.power_status[idx] == ON:
                    self.power_onoff(idx+1)                
                    
        print('start monitoring!!!')
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, HK_START_MONITORING)
        
        self.st_time = ti.time()
        self.uploade_start = ti.time()    

        self.GetValue()               
        self.PeriodicFunc()
        
        
    def PeriodicFunc(self):      
        
        #if self.producer[HK_SUB] == None:
        #    return
        if self.InstSeq_ready == False:
            return
        
        _t = ti.time() - self.st_time
        if _t < self.Period:
            threading.Timer(0.5, self.PeriodicFunc).start()
            return

        self.st_time = ti.time()
        self.GetValue()
        self.st = ti.time()            
    
        threading.Timer(0.5, self.PeriodicFunc).start()
        self.log.send(self.iam, INFO, "PeriodicFunc")

        threading.Timer(2, self.LoggingFun).start()
        
        
    def GetValue(self):

        if self.InstSeq_ready == False:
            return
        
        with futures.ThreadPoolExecutor() as executor:
            try:
                executor.submit(self.get_value_fromTMC())
                executor.submit(self.get_value_fromTM())
                executor.submit(self.get_value_fromVM())
                
            except RuntimeError as e:
                self.log.send(self.iam, ERROR, e)
            except Exception as e:
                self.log.send(self.iam, ERROR, e)
                 
                 
    def get_value_fromTMC(self):
        for i in range(3):
            msg = "%s %s" % (HK_REQ_GETVALUE, self.com_list[i])
            self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg) 

    
    def get_value_fromTM(self):
        msg = "%s %s 0" % (HK_REQ_GETVALUE, self.com_list[TM])
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg) 
            
            
    def get_value_fromVM(self):
        msg = "%s %s" % (HK_REQ_GETVALUE, self.com_list[VM])
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg)           

        
    def get_pwr_sts(self):
        msg = "%s %s %s" % (HK_REQ_PWR_STS, self.com_list[PDU], HK)
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg, True) 
        
        
    def power_onoff(self, idx):
        if self.power_status[idx-1] == ON:
            msg = "%s %s %s %d %s" % (HK_REQ_PWR_ONOFF, self.com_list[PDU], HK, idx, OFF)
        else:
            msg = "%s %s %s %d %s" % (HK_REQ_PWR_ONOFF, self.com_list[PDU], HK, idx, ON)
        self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg, True)
        
        
    def LoggingFun(self):     

        if self.InstSeq_ready == False:
            return

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

        alert_status = "On(T>%d)" % self.alert_temperature

        hk_entries.append(alert_status)

        # hk_entries to string
        updated_datetime = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
        str_log1 = "\t".join([updated_datetime] + list(map(str, hk_entries))) + "\n"    #by hilee
        file.write(str_log1)
        file.close()

        upload = ti.time() - self.uploade_start
        #print("Logging time:", upload)
        if upload >= LOGGING_INTERVAL:
            self.uploade_status = False
            
            str_log = "    ".join([updated_datetime] + list(map(str, hk_entries)))     
            msg = "%s %s %s" % (HK_REQ_UPLOAD_DB, self.com_list[UPLOADER], str_log)
            self.producer[HK_SUB].send_message(self.ObsApp_sub_q, msg)
            
            self.uploade_start = ti.time()
        
        # update log_time with Z0
        log_date, log_time = updated_datetime.split()
        hk_dict = hk_entries_to_dict(log_date, log_time, hk_entries)
        hk_dict.update(self.dtvalue_from_label.as_dict())


    def judge_value(self, input):
        if input != DEFAULT_VALUE:
            value = "%.2f" % float(input)
        else:
            value = input

        return value
          
    #--------------------------------------------------------
    # button, event
    def single(self):
        pass
    
    
    def continous(self):
        pass
        
        
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
        self.progressBar_obs.setValue(self.cur_prog_step[dc_idx])
    
    def show_elapsed(self):
        if self.elapsed_obs <= 0:
            self.elapsed_obs_timer.stop()
            return
        
        self.elapsed_obs -= 0.001
        msg = "%.3f sec" % self.elapsed_obs
        self.label_time_left.setText(msg)
    
    #--------------------------------------------------------------
    # thread - with GUI
            
    def InstSeq_data_processing(self):
        while True:
            if self.param[INST_SEQ] == "":
                continue
            
            param = self.param[INST_SEQ].split()
                
            if param[0] == SHOW_TCS_INFO:
                pass
                        
            elif param[0] == CMD_SETFSPARAM_ICS:
                if param[1] == "DCSS":
                    self.lineEdit_svc_exp_time.setText(param[3])
                    self.label_svc_sampling_number.setText(param[5])
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
                    
            self.param[INST_SEQ] = ""                    
                    
            
            
    def svc_data_processing(self):
        while True:
            if self.param[DCS] == "":
                continue
            
            self.param[DCS] = ""
    
    
    def sub_data_processing(self):
        while True:
            if self.param[HK_SUB] == "":
                continue
            
            param = self.param[HK_SUB].split()
              
            if param[0] == HK_REQ_GETVALUE:
                if param[1] == self.com_list[TMC2]:                
                    self.label_temp_detS.setText(self.dtvalue[label_list[2]])
                    self.label_temp_detK.setText(self.dtvalue[label_list[3]])
                    self.label_heater_detS.setText(self.heatlabel[label_list[2]])
                    self.label_heater_detK.setText(self.heatlabel[label_list[3]])
                    
                elif param[1] == self.com_list[TMC3]:
                    self.label_temp_detH.setText(self.dtvalue[label_list[5]])
                    self.label_heater_detH.setText(self.heatlabel[label_list[5]])
                    
                elif param[1] == self.com_list[VM]:                    
                    self.label_vacuum.setText(self.dpvalue)
            
            self.param[HK_SUB] = ""
                

if __name__ == "__main__":
    
    app = QApplication()
        
    sys.argv.append('1')
    ObsApp = MainWindow(sys.argv[1])
    ObsApp.show()
        
    app.exec()