# -*- coding: utf-8 -*-

"""
Created on Jan 27, 2022

Modified on Nov 10, 2022

@author: hilee
"""

import sys, os

from ui_SCP import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

#import pyautogui as pa

from SC_core import *
from Libs.logger import *
import Libs.zscale as zs

import time as ti
import threading
import math

import numpy as np
import astropy.io.fits as fits 
import zscale as zs

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import qimage2ndarray

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self, autostart=False):
        super().__init__()
        
        self.setupUi(self)
        self.setWindowTitle("Slit Camera Package 0.1")
        
        self.sc = SC()
        
        self.init_events()
        
        #---------------------
        # graph
        self.fig_radial = plt.figure()
        self.fig_radial_ax = self.fig_radial.add_subplot(111)
        self.fig_radial.subplots_adjust(left=0.035,right=0.96,bottom=0.043,top=0.96)
        self.fig_radial_ax.tick_params(axis='x', labelsize=6, pad=-12)
        self.fig_radial_ax.tick_params(axis='y', labelsize=6, pad=-14)
        
        self.canvas_radial = FigureCanvas(self.fig_radial)
        self.graph_vertical_radial.addWidget(self.canvas_radial)
        #---------------------        
        
        self.label_dcss_sts.setText("Disconnected")
        self.dcss_sts = False
        self.label_mode.setText("---")
        
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
        
        self.label_zscale_range.setText("---")
        self.e_mscale_min.setText("1000")
        self.e_mscale_max.setText("5000")
        
        self.timer_alive = QTimer(self)
        self.timer_alive.setInterval(self.sc.alive_chk_interval * 1000) 
        self.timer_alive.timeout.connect(self.alive_check)
        
        self.main_rect = self.graphicsView_main.geometry()
        self.img_st = 370
        self.pixel_scale_x = (FRAME_X - (self.img_st*2)) / self.main_rect.width()
        self.pixel_scale_y = (FRAME_Y - (self.img_st*2)) / self.main_rect.height()
        #self.pixel_scale_x = FRAME_X / self.main_rect.width()
        #self.pixel_scale_y = FRAME_Y / self.main_rect.height()

        self.roi_center_x = FRAME_X/2
        self.roi_center_y = FRAME_Y/2
        
        self.fowler_exp = 0.0       # need to cal
        
        self.simulation_mode = True     #from EngTools
        self.output_channel = 32
        
        self.img = None
        self.img_roi = None
        self.img_load = False
        self.show_radial = True
        
        self.zmin, self.zmax = 0, 0
           
        self.MQserver_connect_retry()

                
        
    def closeEvent(self, *args, **kwargs):
        self.timer_alive.stop()
        self.OnkillTimer()
        
        print("Closing %s : " % sys.argv[0])
        
        for th in threading.enumerate():
            print(th.name + " exit.")
            
        if self.queue:
            self.channel.stop_consuming()
            self.connection.close()
        
        return QMainWindow.closeEvent(self, *args, **kwargs)
    
    
    def init_events(self):
        
        self.setMouseTracking(True)
    
        #same position: label_graph_radial, graph_vertical_radial
        self.label_graph_radial.mousePressEvent = self.mousePress_onRadial 
        self.graphicsView_main.mousePressEvent = self.mousePress_onMain
        
        self.bt_MQserver_retry.setEnabled(False)
        self.bt_MQserver_retry.clicked.connect(self.MQserver_connect_retry)
        
        self.bt_DCSS_check_stop.setEnabled(False)
        self.bt_DCSS_check.clicked.connect(lambda: self.DCSS_monit(True))
        self.bt_DCSS_check_stop.clicked.connect(lambda: self.DCSS_monit(False))
        self.bt_DCSS_init.clicked.connect(self.init)
        
        self.chk_ROI_mode.clicked.connect(self.Use_ROI_mode)
        self.e_boxsize.setEnabled(False)
        self.bt_ROI_SET.setEnabled(False)
        self.bt_ROI_SET.clicked.connect(self.ROI_set)

        self.e_exptime.setEnabled(False)
        self.e_FS_number.setEnabled(False)
        
        #for test 
        #self.bt_acquisition.setEnabled(False)
        
        self.bt_stop.setEnabled(False)
        self.e_repeat_number.setEnabled(False)
        
        self.bt_acquisition.clicked.connect(self.single_exposure)   
        self.bt_stop.clicked.connect(self.stop_acquisition)
        
        self.bt_save.clicked.connect(self.save_fits)
        self.bt_path.clicked.connect(self.open_path)
        
        self.radioButton_zscale.clicked.connect(self.auto_scale)
        self.radioButton_mscale.clicked.connect(self.manual_scale)
        self.bt_scale_apply.clicked.connect(self.scale_apply)
        
        self.radioButton_zscale.setChecked(True)
        self.radioButton_mscale.setChecked(False)
        self.bt_scale_apply.setEnabled(False)

        
        
        
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
        
        
    def send_message_to_main(self, message):
        serv.send_message(IAM, MAIN, self.channel_sc_ex, self.sc.sc_main_ex, self.sc.sc_main_q, message)
            
            
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
                self.sc.log.logwrite("gui", ERROR, "The communication of server was disconnected!")
                
    
    def callback_main(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.sc.log.logwrite("gui", INFO, msg)

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
                self.sc.log.logwrite("gui", ERROR, "The communication of server was disconnected!")


    def alive_check(self):
        self.sc.alive_check()
        
        self.dcss_sts = False
        timer = QTimer(self)
        timer.singleShot(self.sc.alive_chk_interval*1000/2, self.show_alarm)
        

    def callback_ics(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.sc.log.logwrite("gui", INFO, msg)

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
            
            self.e_exptime.setEnabled(True)
            self.e_FS_number.setEnabled(True)
        
            self.bt_acquisition.setEnabled(True)
            self.bt_stop.setEnabled(True)
            self.e_repeat_number.setEnabled(True)            
            
        elif param[0] == CMD_SETFSPARAM:
            #acquire
            self.sc.acquireramp(self.simulation_mode, self.ROI_mode)

        elif param[0] == CMD_ACQUIRERAMP:
            # load data
            self.load_data()
        
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
        
        
    def load_data(self):
        filepath = ""
        if self.simulation_mode:
            filepath = WORKING_DIR + "IGRINS/demo/sc/demo0.fits"
        
        frm = fits.open(filepath)
        data = frm[0].data
        header = frm[0].header
        _img = np.array(data, dtype = "f")
        #_img = np.flipud(np.array(data, dtype = "f"))
        self.img = _img[self.img_st:FRAME_Y-self.img_st, self.img_st:FRAME_X-self.img_st]
        #self.img = _img
        
        if self.img_load == False:
            self.OnStartTimer()
            self.img_load = True
        
        self.zmin, self.zmax = zs.zscale(self.img)
        range = "%d ~ %d" % (self.zmin, self.zmax)
        self.label_zscale_range.setText(range)
        
        self.mmin, self.mmax = np.min(self.img), np.max(self.img)
        self.e_mscale_min.setText("%.1f" % self.mmin)
        self.e_mscale_max.setText("%.1f" % self.mmax)
        
        self.reload_img()
        
        
    def reload_img(self):      
        
        if self.img_load == False:          
            return
        
        _img = np.flipud(self.img)

        min, max = 0, 0
        if self.radioButton_zscale.isChecked():
            min, max = self.zmin, self.zmax
        elif self.radioButton_mscale.isChecked():
            min, max = self.mmin, self.mmax
            
        scene = QGraphicsScene(self)
        scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(_img, (int(min), int(max)))).scaled(self.graphicsView_main.width(), self.graphicsView_main.height(), Qt.IgnoreAspectRatio, Qt.FastTransformation))
        self.graphicsView_main.setScene(scene)   
                
    
    def show_roi(self):
        boxsize = int(self.e_boxsize.text())/2
                
        roi_center_y = self.roi_center_y - self.img_st
        roi_center_x = self.roi_center_x - self.img_st
        self.img_roi = self.img[int(roi_center_y - boxsize):int(roi_center_y + boxsize), int(roi_center_x - boxsize):int(roi_center_x + boxsize)]
        
        zmin, zmax = zs.zscale(self.img_roi)
        mmin, mmax = np.min(self.img_roi), np.max(self.img_roi)
       
        min, max = 0, 0
        if self.radioButton_zscale.isChecked():
            min, max = zmin, zmax
        elif self.radioButton_mscale.isChecked():
            min, max = mmin, mmax
        
        _img = np.flipud(self.img_roi)
        scene = QGraphicsScene(self)
        scene.addPixmap(QPixmap.fromImage(qimage2ndarray.array2qimage(_img, (int(min), int(max)))).scaled(self.graphicsView_roi.width(), self.graphicsView_roi.height(), Qt.IgnoreAspectRatio))
        self.graphicsView_roi.setScene(scene)
        
        self.show_GaussianFitting()
        
        
    def show_GaussianFitting(self):
        
        if self.img_load == False:          
            return
        
        self.clean_ax(self.fig_radial_ax, ticks_off=False)
        if self.show_radial:
            self.radial_plot()
        else:
            self.contour_plot()
            
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # test        
    def clean_ax(self, ax, ticks_off = True):
        '''
        Clean the canvases with ticks and ...
        - receive a axes object and clean axes
        - ticks_off option use for radial profile fitting
        '''
        ax.cla()
        if (ticks_off == True):
            ax.set_xticklabels([])
            ax.set_yticklabels([])

            ax.set_frame_on(False)
            ax.set_xticks([])
            ax.set_yticks([])
            
            
    def radial_plot(self):       
        boxsize = int(self.e_boxsize.text())
        radialprofile = self.radial_profile(self.img_roi, boxsize/2, boxsize/2)
                
        self.fig_radial_ax.plot(self.img_roi, "r.", markersize=7)
        
        self.fig_radial_ax.set_xlim(-0.5, 15)
        self.fig_radial_ax.set_frame_on(True)
        self.fig_radial_ax.tick_params(direction='in')
        self.fig_radial_ax.ticklabel_format(axis='y',style='sci')
        self.fig_radial_ax.set_aspect('auto','datalim')

        self.canvas_radial.draw()
        print("profile")
                            
        
    def radial_profile(self, image, xcen, ycen):

        y, x = np.indices(image.shape)
        r = np.sqrt( (x - xcen)**2 + (y - ycen)**2 )
        ind = np.argsort(r.flat)

        sr = r.flat[ind]
        sim = image.flat[ind]
        ri = sr.astype(int)

        deltar = ri[1:] - ri[:-1]
        rind = np.where(deltar)[0]
        nr = rind[1:] - rind[:-1]
        csim = np.cumsum(sim, dtype = np.float64)
        tbin = csim[rind[1:]] - csim[rind[:-1]]
        profile = tbin/nr

       # Add 0-th value to the array
        radialprofile = np.concatenate((np.array([image[int(ycen), int(xcen)]]), profile), )

        return radialprofile
        
        
    def contour_plot(self):
        
        zmin, zmax = zs.zscale(self.img_roi)
        clevel = np.linspace(zmin, zmax*1.2, 15)[2:]

        scontour = self.fig_radial_ax.contour(self.img_roi, levels=clevel)

        scontour.set_clim(self.zmin, self.zmax)
        self.fig_radial_ax.set_aspect('equal','datalim')

        self.fig_radial_ax.set_frame_on(True)
        strtmp = "X=%6.1f Y=%6.1f" % (self.roi_center_x, self.roi_center_y)
        self.fig_radial_ax.text(0.5, +0.95, strtmp, \
           color='black', ha='center', va='top', \
           transform=self.fig_radial_ax.transAxes, fontsize=8)
        
        self.canvas_radial.draw()
        print("contour")
        
        
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
            
        
    
    #---------------------------------
    # mouse event    
    def mousePress_onRadial(self, event:QMouseEvent) -> None:
                
        if event.button() == Qt.LeftButton:
            
            if self.img_load == False:
                return
        
            if self.show_radial:
                self.show_radial = False
            else:
                self.show_radial = True
        
            self.show_GaussianFitting()
        
        return super().mousePressEvent(event)
    
    
    def mousePress_onMain(self, event:QMouseEvent) -> None:        
        
        if event.button() == Qt.LeftButton:
            
            if self.img_load == False:
                return
        
            cur_cursor = "(%.1f,%.1f)" % (self.roi_center_x, self.roi_center_y)
            self.label_ROI_center.setText(cur_cursor)
            
            self.show_roi()
        
        return super().mousePressEvent(event)
            
    
    def OnStartTimer(self):
        self.timerId = self.startTimer(10)
        
        
    def OnKillTimer(self):
        self.killTimer(self.timerId)

    
    #mouse
    def timerEvent(self, event: QTimerEvent) -> None:
        
        pos = QCursor.pos()     
        
        frame = self.geometry()
        #print(frame)
        _x = pos.x() - (self.main_rect.x() + frame.x())
        _y = self.main_rect.height() - (pos.y() - (self.main_rect.y() + frame.y()))
        
        main_x = _x * self.pixel_scale_x + self.img_st
        main_y = _y * self.pixel_scale_y + self.img_st
        
        if (0 < _x < self.main_rect.width()) and (0 < _y < self.main_rect.height()):
            if self.img_load:
                cur_cursor = "(%.1f,%.1f)=%.3f" % (main_x, main_y, self.img[int(main_y)-self.img_st,int(main_x)-self.img_st])
            else:
                cur_cursor = "(%.1f,%.1f)" % (main_x, main_y)
            self.label_cur_cursor.setText(cur_cursor) 
            self.roi_center_x = main_x
            self.roi_center_y = main_y    
        else:
            self.label_cur_cursor.setText("( - , - )")
                
        return super().timerEvent(event)

    #---------------------------------
    # buttons
    
    def MQserver_connect_retry(self):
        #for with main, local
        self.connect_to_server_sc_ex()
        self.connect_to_server_main_q()
        
        #for dcss
        self.sc.connect_to_server_ics_ex()        
        self.connect_to_server_ics_q()
        
        
    def DCSS_monit(self, start):
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
        
        
    def Use_ROI_mode(self):
        use = self.chk_ROI_mode.isChecked()
        self.e_boxsize.setEnabled(use)
        self.bt_ROI_SET.setEnabled(use)
        
        
    def ROI_set(self):
        boxsize = int(self.e_boxsize.text())
        self.sc.set_win_param(self.simulation_mode, self.roi_center_x-boxsize/2, self.roi_center_x+boxsize/2, self.roi_center_y-boxsize/2, self.roi_center_y+boxsize/2)
        
        
    def single_exposure(self):
        
        # for test
        self.load_data()
        return
    
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
        self.reload_img()
        self.bt_scale_apply.setEnabled(False)
    
    def manual_scale(self):
        self.reload_img()
        self.bt_scale_apply.setEnabled(True)

        
    def scale_apply(self):
        self.mmin = float(self.e_mscale_min.text())
        self.mmax = float(self.e_mscale_max.text())
        
        self.reload_img()
    
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