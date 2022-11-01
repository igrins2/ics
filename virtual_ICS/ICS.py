# -*- coding: utf-8 -*-

"""
Created on Aug 29, 2022

Modified on Sep 8, 2022

@author: hilee

virtual ICS for testing with RabbitMQ Server
"""

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_ICS import *

import sys

import threading
import pika

UTR_MODE = 0    #single frame
CDS_MODE = 1
CDSNOISE_MODE = 2
FOWLER_MODE = 3

T_frame = 1.45479
T_exp = 1.63
T_minFowler = 0.168
T_br = 2

FRAME_X = 2048
FRAME_Y = 2048

# command
CMD_INITIALIZE1 = "Initialize1"
CMD_INITIALIZE2 = "Initialize2"
CMD_DOWNLOAD = "DownloadMCD"
CMD_SETDETECTOR = "SetDetector"
CMD_SETFSMODE = "SETFSMODE"
CMD_SETRAMPPARAM = "SetRampParam"
CMD_SETFSPARAM = "SetFSParam"
CMD_SETWINPARAM = "SetWinParam"
CMD_ACQUIRERAMP = "ACQUIRERAMP"
CMD_STOPACQUISITION = "STOPACQUISITION"


class MainWindow(Ui_Dialog, QMainWindow):

    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Virtual ICS 0.1")

        self.label_connection_sts.setText("DCS")

        self.samplingmode = UTR_MODE

        self.x_start, self.x_stop, self.y_start, self.y_stop = 0, FRAME_X-1, 0, FRAME_Y
        self.resets, self.reads, self.ramps, self.groups, self.drops = 1, 1, 1, 1, 1

        self.com_sts = False
        self.dcs_sts = False

        self.set_samplingmode(self.samplingmode)
        self.set_param_ui(1, 1, 1, 1, 1)

        #self.radio_exp_time.setChecked(True)
        #self.radio_fowler_number.setChecked(False)

        self.init_events()

        self.timer_alive = QTimer(self)
        self.timer_alive.setInterval(60 * 1000)  #after 60sec
        self.timer_alive.timeout.connect(self.alive_check)

        self.connect_to_server()

    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.timer_alive.stop()

        for th in threading.enumerate():
            print(th.name + " exit.")

        if self.com_sts:
            self.channel.stop_consuming()
            self.connection.close()  

        return super().closeEvent(event)


    def set_samplingmode(self, mode):
        if mode == UTR_MODE:
            self.radio_UTR.setChecked(True)
        elif mode == CDS_MODE:
            self.radio_CDS.setChecked(True)
        elif mode == CDSNOISE_MODE:
            self.radio_CDSNoise.setChecked(True)
        elif mode == FOWLER_MODE:
            self.radio_Fowler.setChecked(True)


    def set_param_ui(self, resets, reads, groups, drops, ramps):
        if self.samplingmode == UTR_MODE:
            self.e_reads.setEnabled(True)
            self.e_groups.setEnabled(True)
            self.e_drops.setEnabled(True)
            self.e_ramps.setEnabled(True)

            self.radio_exp_time.hide()
            self.radio_fowler_number.hide()

            self.e_exp_time.setEnabled(False)
            self.e_fowler_number.setEnabled(False)

            self.drops = drops
            self.label_drops.setText("Drops")

        else:
            self.e_reads.setEnabled(False)
            self.e_groups.setEnabled(False)
            self.e_drops.setEnabled(False)
            self.e_ramps.setEnabled(False)

            self.fowlerTime = drops
            self.label_drops.setText("T.Fowler")

            self.e_fowler_number.setText(str(reads))

            if self.samplingmode == FOWLER_MODE:
                self.e_exp_time.setEnabled(True)
                self.e_fowler_number.setEnabled(True)

                self.radio_exp_time.show()
                self.radio_fowler_number.show()

            else: 
                self.e_exp_time.setEnabled(False)
                self.e_fowler_number.setEnabled(False)

                self.radio_exp_time.hide()
                self.radio_fowler_number.hide()
            

        self.e_resets.setText(str(resets))
        self.e_reads.setText(str(reads))
        self.e_groups.setText(str(groups))
        self.e_drops.setText(str(drops))
        self.e_ramps.setText(str(ramps))

        self.resets = resets
        self.reads = reads
        self.groups = groups
        self.ramps = ramps


    def init_events(self):

        self.btn_initialize1.clicked.connect(self.initialize1)
        self.btn_initialize2.clicked.connect(self.initialize2)
        self.btn_download_MCD.clicked.connect(self.downloadMCD)
        self.btn_set_detector.clicked.connect(self.set_detector)

        self.radio_UTR.clicked.connect(self.click_UTR)
        self.radio_CDS.clicked.connect(self.click_CDS)
        self.radio_CDSNoise.clicked.connect(self.click_CDSNoise)
        self.radio_Fowler.clicked.connect(self.click_Fowler)

        self.radio_exp_time.clicked.connect(self.judge_exp_time)
        self.radio_fowler_number.clicked.connect(self.judge_fowler_number)

        self.btn_set_param.clicked.connect(self.set_parameter)

        self.chk_ROI_mode.clicked.connect(self.click_ROImode)

        self.btn_acquireramp.clicked.connect(self.acquireramp)
        self.btn_stop.clicked.connect(self.stop_acquistion)


    # ----------------------------------------------------------------------
    # RabbitMQ communication
    def connect_to_server(self):

        try:
            id_pwd = pika.PlainCredentials('igos2n', 'kasi2023')                
        
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='100.40.3.103', port=5672, credentials=id_pwd))
            self.channel = self.connection.channel()

            # as producer
            self.channel.exchange_declare(exchange="ics.dcss.ex", exchange_type="direct")

            # as consumer
            self.channel.exchange_declare(exchange="dcss.ics.ex", exchange_type="direct")
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.queue = result.method.queue
            self.channel.queue_bind(exchange='dcss.ics.ex', queue=self.queue, routing_key='dcss.ics.q')
        
            th = threading.Thread(target=self.consumer)
            th.start()

            self.timer_alive.start()

            self.show_alarm()

            self.com_sts = True
        
        except:
            self.com_sts = False
  

    
    def consumer(self):
        try:
            self.channel.basic_consume(queue=self.queue,on_message_callback=self.callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            if self.channel:
                self.com_sts = False


    def callback(self, ch, method, properties, body):
        msg = "receive: %s" % body.decode()
        print(msg)

        if body.decode() == "alive":
            self.dcs_sts = True
        #else:
            


    def alive_check(self):
        self.send_message("alive?")


    def show_alarm(self):
        textcolor = "black"
        if self.dcs_sts is True:
            textcolor = "green"
        else:
            textcolor = "red"
        
        label = "QLabel {color:%s}" % textcolor
        self.label_connection_sts.setStyleSheet(label)

        self.dcs_sts = False
        timer = QTimer(self)
        timer.singleShot(180*1000, self. show_alarm)     #after 180sec


    def send_message(self, message):
        self.channel.basic_publish(exchange='ics.dcss.ex', routing_key='ics.dcss.q', body=message.encode())
        print('[send->dcs] ' + message)

    # ----------------------------------------------------------------------
    # Buttons
    def initialize1(self):
        self.send_message(CMD_INITIALIZE1)


    def initialize2(self):
        self.send_message(CMD_INITIALIZE2)


    def downloadMCD(self):
        self.send_message(CMD_DOWNLOAD)


    def set_detector(self):
        self.send_message(CMD_SETDETECTOR)


    def set_FS_mode(self, mode):
        cmd = "%s %d" % (CMD_SETFSMODE, mode)
        self.send_message(cmd)

   
    def click_UTR(self):
        self.samplingmode = UTR_MODE
        self.set_param_ui(1, 1, 1, 1, 1)
        self.set_FS_mode(0)


    def click_CDS(self):
        self.samplingmode = CDS_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)
        self.set_FS_mode(1)


    def click_CDSNoise(self):
        self.samplingmode = CDSNOISE_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 2)
        self.set_FS_mode(2)


    def click_Fowler(self):
        self.samplingmode = FOWLER_MODE
        self.set_param_ui(1, 1, 1, T_minFowler, 1)
        self.set_FS_mode(3)


    def judge_exp_time(self):
        self.e_exp_time.setEnabled(True)
        self.e_fowler_number.setEnabled(False)


    def judge_fowler_number(self):
        self.e_exp_time.setEnabled(False)
        self.e_fowler_number.setEnabled(True)


    def judge_param(self):
        _exp_time = float(self.e_exp_time.text())
        _fowler_num = int(self.e_fowler_number.text())

        _fowler_time = float(self.e_drops.text())

        if self.radio_exp_time.isChecked():
            _max_fowler_number = int((_exp_time - T_minFowler) / T_frame)
            if _fowler_num > _max_fowler_number:
                #dialog box
                print("please change 'exposure time'!")
                return False

        elif self.radio_fowler_number.isChecked():
            _fowler_time = _exp_time - T_frame * _fowler_num
            if _fowler_time < T_minFowler:
                #dialog box
                print("please change 'fowler sampling number'!")
                return False            

        else:
            print("Please select 'Exp. Time' or 'N. Fowler' for judgement!")
            return False

        return True


    def set_parameter(self):      

        if self.samplingmode == FOWLER_MODE and self.judge_param() == False:
            return

        self.resets = int(self.e_resets.text())
        self.reads = int(self.e_reads.text())
        self.groups = int(self.e_groups.text())
        self.ramps = int(self.e_ramps.text())

        _exp_time, cal_waittime = 0.0, 0.0

        if self.samplingmode == UTR_MODE:
            self.drops = int(self.e_drops.text())

            _exp_time = (T_frame * self.reads * self.groups) + (T_frame * self.drops * (self.groups -1 ))
            cal_waittime = T_br + ((T_frame * self.resets) + _exp_time) * self.ramps
            
            cmd = "%s %d %d %d %d %d" % (CMD_SETRAMPPARAM, self.resets, self.reads, self.groups, self.drops, self.ramps)
            self.send_message(cmd)

            str_exp_time = "%.3f" % _exp_time
            self.e_exp_time.setText(str_exp_time)

        else:
            #self.fowlerTime = float(self.e_drops.text())
            #exptime = self.fowlerTime + T_frame * self.reads

            _exp_time = float(self.e_exp_time.text())
            if self.samplingmode == FOWLER_MODE:
                if self.radio_fowler_number.isChecked():
                    self.e_reads.setText(self.e_fowler_number.text())
                    self.reads = int(self.e_reads.text())

                self.fowlerTime = _exp_time - T_frame * self.reads

                str_fowlerTime = "%.3f" % self.fowlerTime
                self.e_drops.setText(str_fowlerTime)
            
            else:
                _exp_time = self.fowlerTime + T_frame * self.reads

                str_exp_time = "%.3f" % _exp_time
                self.e_exp_time.setText(str_exp_time)

            cal_waittime = T_br + ((T_frame * self.resets) + self.fowlerTime + (2 * T_frame * self.reads)) * self.ramps
            
            cmd = "%s %d %d %d %.3f %d" % (CMD_SETFSPARAM, self.resets, self.reads, self.groups, self.fowlerTime, self.ramps)
            self.send_message(cmd)          
        
        str_caltime = "%.5f" % cal_waittime
        self.label_calculated_time.setText(str_caltime)


    def click_ROImode(self):
        if self.chk_ROI_mode.isChecked():
            cmd = "%s %s %s %s %s" % (CMD_SETWINPARAM, self.e_x_start.text(), self.e_x_stop.text(), self.e_y_start.text(), self.e_y_stop.text())
            self.send_message(cmd)
        else:
            self.send_message(CMD_SETWINPARAM)

    def acquireramp(self):
        self.send_message(CMD_ACQUIRERAMP)


    def stop_acquistion(self):
        self.send_message(CMD_STOPACQUISITION)


    
    # ----------------------------------------------------------------------


if __name__ == "__main__":

    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False

    app = QApplication(sys.argv)

    dc = MainWindow()
    dc.show()

    app.exec()