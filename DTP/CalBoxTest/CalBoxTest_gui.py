# -*- coding: utf-8 -*-

"""
Created on Jan 4, 2022

Modified...

@author: hilee
"""


from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from ui_CalBox import *
from CalBoxTest_core import *
from CalBoxTest_def import *


class MainWindow(Ui_Dialog, QMainWindow):

    def __init__(self, autostart=False):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Calibration Box Test [IGOS2 0.1]")
        
        self.calbox = CalBoxTest(True)
        
        self.Status()
        self.Buttons()
        
        self.e_movinginterval.setText("10")
        
        self.curMotor = MOTOR_UT
        self.curNext = True
        self.timer_btpressed = QTimer(self)
        self.timer_btpressed.setInterval(200)
        self.timer_btpressed.timeout.connect(self.Pressed)
                
                
    def closeEvent(self, *args, **kwargs):
        return QMainWindow.closeEvent(self, *args, **kwargs)
    
    
    def Status(self):
        self.e_utpos.setText("300")
        self.e_ltpos.setText("500")
        
        self.sts_ut_pos1.setText(self.calbox.UT_POS[0])
        self.sts_ut_pos2.setText(self.calbox.UT_POS[1])
        
        self.sts_lt_pos1.setText(self.calbox.LT_POS[0])
        self.sts_lt_pos2.setText(self.calbox.LT_POS[1])
        self.sts_lt_pos3.setText(self.calbox.LT_POS[2])
        self.sts_lt_pos4.setText(self.calbox.LT_POS[3])
        self.sts_lt_pos5.setText(self.calbox.LT_POS[4])
        
        
    def Buttons(self):
        self.chk_whole.clicked.connect(self.Toggle_Whole)
        self.bt_run.clicked.connect(self.Run)
        
        #----------------------------------------------------
        self.bt_utpos_prev.pressed.connect(self.UTMoveToPrev)
        self.bt_utpos_next.pressed.connect(self.UTMoveToNext)
        self.bt_utpos_prev.released.connect(self.MoveStop)
        self.bt_utpos_next.released.connect(self.MoveStop)
        
        self.bt_utpos_set1.clicked.connect(self.UTPosSet1)        
        self.bt_utpos_set2.clicked.connect(self.UTPosSet2)
        self.bt_utpos_prev.clicked.connect(self.Pressed)
        self.bt_utpos_next.clicked.connect(self.Pressed)
                    
        #----------------------------------------------------
        self.bt_ltpos_prev.pressed.connect(self.LTMoveToPrev)
        self.bt_ltpos_next.pressed.connect(self.LTMoveToNext)
        self.bt_ltpos_prev.released.connect(self.MoveStop)
        self.bt_ltpos_next.released.connect(self.MoveStop)
        
        self.bt_ltpos_set1.clicked.connect(self.LTPosSet1)
        self.bt_ltpos_set2.clicked.connect(self.LTPosSet2)
        self.bt_ltpos_set3.clicked.connect(self.LTPosSet3)
        self.bt_ltpos_set4.clicked.connect(self.LTPosSet4)
        self.bt_ltpos_set5.clicked.connect(self.LTPosSet5)
        self.bt_ltpos_prev.clicked.connect(self.Pressed)
        self.bt_ltpos_next.clicked.connect(self.Pressed)   
        
    
    def Toggle_Whole(self):
        for i in range(FRM_CNT):
            if self.chk_whole.isChecked():
                self.tb_calmode.item(i, 0).setCheckState(Qt.Checked)
            else:
                self.tb_calmode.item(i, 0).setCheckState(Qt.Unchecked)
                
                
    def Run(self):
        #updated list
        runlist = []
        for row in range(FRM_CNT):
            args = []
            if self.tb_calmode.item(row, 0).checkState() == Qt.Checked:
                for col in range(3):
                    args.append(self.tb_calmode.item(row, col).text())
    
                runlist.append(args)
        
        if len(runlist) != 0:
            self.calbox.RunMode(runlist)
            
        
    def Pressed(self):
        interval = int(self.e_movinginterval.text())
        delta = interval
        if self.curMotor == MOTOR_UT:
            curpos = int(self.e_utpos.text())
            if self.curNext:
                self.e_utpos.setText(str(curpos+interval))
            else:
                self.e_utpos.setText(str(curpos-interval))
            delta = interval*(-1)
        elif self.curMotor == MOTOR_LT:
            curpos = int(self.e_ltpos.text())
            if self.curNext:
                self.e_ltpos.setText(str(curpos+interval))
            else:
                self.e_ltpos.setText(str(curpos-interval))
                delta = interval*(-1)
                
        self.calbox.MoveDelta(self.curMotor, delta)

            
    def UTMoveToPrev(self):
        self.curMotor = MOTOR_UT
        self.curNext = False
        self.timer_btpressed.start()
        
    def UTMoveToNext(self):
        self.curMotor = MOTOR_UT
        self.curNext = True
        self.timer_btpressed.start()
        
    def LTMoveToPrev(self):
        self.curMotor = MOTOR_LT
        self.curNext = False
        self.timer_btpressed.start()
        
    def LTMoveToNext(self):
        self.curMotor = MOTOR_LT
        self.curNext = True
        self.timer_btpressed.start()
        
    def MoveStop(self):
        self.timer_btpressed.stop()
        
    def UTPosSet1(self):
        self.calbox.SetPosition(MOTOR_UT, 0, self.e_utpos.text())
        self.sts_ut_pos1.setText(self.calbox.UT_POS[0])
    
    def UTPosSet2(self):
        self.calbox.SetPosition(MOTOR_UT, 1, self.e_utpos.text())
        self.sts_ut_pos2.setText(self.calbox.UT_POS[1])
    
    def LTPosSet1(self):
        self.calbox.SetPosition(MOTOR_LT, 0, self.e_ltpos.text())
        self.sts_lt_pos1.setText(self.calbox.LT_POS[0])
    
    def LTPosSet2(self):
        self.calbox.SetPosition(MOTOR_LT, 1, self.e_ltpos.text())
        self.sts_lt_pos2.setText(self.calbox.LT_POS[1])
    
    def LTPosSet3(self):
        self.calbox.SetPosition(MOTOR_LT, 2, self.e_ltpos.text())
        self.sts_lt_pos3.setText(self.calbox.LT_POS[2])
    
    def LTPosSet4(self):
        self.calbox.SetPosition(MOTOR_LT, 3, self.e_ltpos.text())
        self.sts_lt_pos4.setText(self.calbox.LT_POS[3])
    
    def LTPosSet5(self):
        self.calbox.SetPosition(MOTOR_LT, 4, self.e_ltpos.text())
        self.sts_lt_pos5.setText(self.calbox.LT_POS[4])
    
        
        
    
        
        

    
    

if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "--autostart":
        autostart = True
    else:
        autostart = False
        
    app = QApplication(sys.argv)
        
    calbox = MainWindow()
    calbox.show()
        
    app.exec_()
