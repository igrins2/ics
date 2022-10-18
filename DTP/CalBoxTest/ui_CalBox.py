# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CalBoxOhHqwI.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(421, 682)
        self.tb_calmode = QTableWidget(Dialog)
        if (self.tb_calmode.columnCount() < 3):
            self.tb_calmode.setColumnCount(3)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        __qtablewidgetitem = QTableWidgetItem()
        __qtablewidgetitem.setFont(font);
        self.tb_calmode.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        __qtablewidgetitem1.setTextAlignment(Qt.AlignCenter);
        __qtablewidgetitem1.setFont(font);
        self.tb_calmode.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        __qtablewidgetitem2.setFont(font);
        self.tb_calmode.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        if (self.tb_calmode.rowCount() < 9):
            self.tb_calmode.setRowCount(9)
        __qtablewidgetitem3 = QTableWidgetItem()
        __qtablewidgetitem3.setCheckState(Qt.Unchecked);
        __qtablewidgetitem3.setTextAlignment(Qt.AlignLeading|Qt.AlignVCenter);
        __qtablewidgetitem3.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(0, 0, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        __qtablewidgetitem4.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem4.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(0, 1, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        __qtablewidgetitem5.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem5.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(0, 2, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        __qtablewidgetitem6.setCheckState(Qt.Unchecked);
        __qtablewidgetitem6.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(1, 0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        __qtablewidgetitem7.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem7.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(1, 1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        __qtablewidgetitem8.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem8.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(1, 2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setCheckState(Qt.Unchecked);
        __qtablewidgetitem9.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(2, 0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        __qtablewidgetitem10.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem10.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(2, 1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        __qtablewidgetitem11.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem11.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(2, 2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        __qtablewidgetitem12.setCheckState(Qt.Unchecked);
        __qtablewidgetitem12.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(3, 0, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        __qtablewidgetitem13.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem13.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(3, 1, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        __qtablewidgetitem14.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem14.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(3, 2, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        __qtablewidgetitem15.setCheckState(Qt.Unchecked);
        __qtablewidgetitem15.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(4, 0, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        __qtablewidgetitem16.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem16.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(4, 1, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        __qtablewidgetitem17.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem17.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(4, 2, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        __qtablewidgetitem18.setCheckState(Qt.Unchecked);
        __qtablewidgetitem18.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(5, 0, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        __qtablewidgetitem19.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem19.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(5, 1, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        __qtablewidgetitem20.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem20.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(5, 2, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        __qtablewidgetitem21.setCheckState(Qt.Unchecked);
        __qtablewidgetitem21.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(6, 0, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        __qtablewidgetitem22.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem22.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(6, 1, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        __qtablewidgetitem23.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem23.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(6, 2, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        __qtablewidgetitem24.setCheckState(Qt.Unchecked);
        __qtablewidgetitem24.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(7, 0, __qtablewidgetitem24)
        __qtablewidgetitem25 = QTableWidgetItem()
        __qtablewidgetitem25.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem25.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(7, 1, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        __qtablewidgetitem26.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem26.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(7, 2, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        __qtablewidgetitem27.setCheckState(Qt.Unchecked);
        __qtablewidgetitem27.setFlags(Qt.ItemIsSelectable|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(8, 0, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        __qtablewidgetitem28.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem28.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(8, 1, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        __qtablewidgetitem29.setTextAlignment(Qt.AlignTrailing|Qt.AlignVCenter);
        __qtablewidgetitem29.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEditable|Qt.ItemIsEnabled);
        self.tb_calmode.setItem(8, 2, __qtablewidgetitem29)
        self.tb_calmode.setObjectName(u"tb_calmode")
        self.tb_calmode.setGeometry(QRect(11, 60, 401, 301))
        self.tb_calmode.setShowGrid(True)
        self.tb_calmode.setSortingEnabled(False)
        self.tb_calmode.setRowCount(9)
        self.tb_calmode.setColumnCount(3)
        self.tb_calmode.horizontalHeader().setCascadingSectionResizes(False)
        self.tb_calmode.horizontalHeader().setDefaultSectionSize(130)
        self.tb_calmode.horizontalHeader().setProperty("showSortIndicator", False)
        self.tb_calmode.verticalHeader().setVisible(False)
        self.tb_calmode.verticalHeader().setProperty("showSortIndicator", False)
        self.tb_calmode.verticalHeader().setStretchLastSection(False)
        self.chk_whole = QCheckBox(Dialog)
        self.chk_whole.setObjectName(u"chk_whole")
        self.chk_whole.setGeometry(QRect(21, 20, 141, 31))
        self.chk_whole.setFont(font)
        self.bt_run = QPushButton(Dialog)
        self.bt_run.setObjectName(u"bt_run")
        self.bt_run.setGeometry(QRect(270, 20, 141, 31))
        self.bt_run.setFont(font)
        self.groupBox_3 = QGroupBox(Dialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setGeometry(QRect(10, 380, 401, 291))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        font1.setWeight(75)
        self.groupBox_3.setFont(font1)
        self.bt_ltpos_set5 = QPushButton(self.groupBox_3)
        self.bt_ltpos_set5.setObjectName(u"bt_ltpos_set5")
        self.bt_ltpos_set5.setGeometry(QRect(310, 250, 71, 20))
        font2 = QFont()
        font2.setFamily(u"Arial")
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setWeight(75)
        self.bt_ltpos_set5.setFont(font2)
        self.bt_ltpos_set1 = QPushButton(self.groupBox_3)
        self.bt_ltpos_set1.setObjectName(u"bt_ltpos_set1")
        self.bt_ltpos_set1.setGeometry(QRect(310, 130, 71, 20))
        self.bt_ltpos_set1.setFont(font2)
        self.bt_utpos_set1 = QPushButton(self.groupBox_3)
        self.bt_utpos_set1.setObjectName(u"bt_utpos_set1")
        self.bt_utpos_set1.setGeometry(QRect(310, 40, 71, 20))
        self.bt_utpos_set1.setFont(font2)
        self.bt_utpos_set2 = QPushButton(self.groupBox_3)
        self.bt_utpos_set2.setObjectName(u"bt_utpos_set2")
        self.bt_utpos_set2.setGeometry(QRect(310, 70, 71, 20))
        self.bt_utpos_set2.setFont(font2)
        self.sts_lt_pos1 = QLabel(self.groupBox_3)
        self.sts_lt_pos1.setObjectName(u"sts_lt_pos1")
        self.sts_lt_pos1.setGeometry(QRect(200, 130, 91, 21))
        font3 = QFont()
        font3.setFamily(u"Comic Sans MS")
        font3.setPointSize(12)
        font3.setBold(False)
        font3.setItalic(False)
        font3.setWeight(50)
        self.sts_lt_pos1.setFont(font3)
        self.sts_lt_pos1.setAlignment(Qt.AlignCenter)
        self.bt_ltpos_prev = QPushButton(self.groupBox_3)
        self.bt_ltpos_prev.setObjectName(u"bt_ltpos_prev")
        self.bt_ltpos_prev.setGeometry(QRect(26, 160, 21, 20))
        self.bt_ltpos_prev.setFont(font2)
        self.bt_ltpos_set4 = QPushButton(self.groupBox_3)
        self.bt_ltpos_set4.setObjectName(u"bt_ltpos_set4")
        self.bt_ltpos_set4.setGeometry(QRect(310, 220, 71, 20))
        self.bt_ltpos_set4.setFont(font2)
        self.bt_ltpos_set3 = QPushButton(self.groupBox_3)
        self.bt_ltpos_set3.setObjectName(u"bt_ltpos_set3")
        self.bt_ltpos_set3.setGeometry(QRect(310, 190, 71, 20))
        self.bt_ltpos_set3.setFont(font2)
        self.bt_ltpos_set2 = QPushButton(self.groupBox_3)
        self.bt_ltpos_set2.setObjectName(u"bt_ltpos_set2")
        self.bt_ltpos_set2.setGeometry(QRect(310, 160, 71, 20))
        self.bt_ltpos_set2.setFont(font2)
        self.bt_utpos_next = QPushButton(self.groupBox_3)
        self.bt_utpos_next.setObjectName(u"bt_utpos_next")
        self.bt_utpos_next.setGeometry(QRect(140, 70, 21, 20))
        self.bt_utpos_next.setFont(font2)
        self.bt_utpos_prev = QPushButton(self.groupBox_3)
        self.bt_utpos_prev.setObjectName(u"bt_utpos_prev")
        self.bt_utpos_prev.setGeometry(QRect(26, 70, 21, 20))
        self.bt_utpos_prev.setFont(font2)
        self.e_utpos = QLineEdit(self.groupBox_3)
        self.e_utpos.setObjectName(u"e_utpos")
        self.e_utpos.setGeometry(QRect(48, 70, 91, 20))
        self.e_utpos.setFont(font2)
        self.e_utpos.setLayoutDirection(Qt.LeftToRight)
        self.e_utpos.setAlignment(Qt.AlignCenter)
        self.line = QFrame(self.groupBox_3)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(20, 100, 371, 20))
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.e_ltpos = QLineEdit(self.groupBox_3)
        self.e_ltpos.setObjectName(u"e_ltpos")
        self.e_ltpos.setGeometry(QRect(48, 160, 91, 20))
        self.e_ltpos.setFont(font2)
        self.e_ltpos.setLayoutDirection(Qt.LeftToRight)
        self.e_ltpos.setAlignment(Qt.AlignCenter)
        self.bt_ltpos_next = QPushButton(self.groupBox_3)
        self.bt_ltpos_next.setObjectName(u"bt_ltpos_next")
        self.bt_ltpos_next.setGeometry(QRect(140, 160, 21, 20))
        self.bt_ltpos_next.setFont(font2)
        self.sts_ut_pos1 = QLabel(self.groupBox_3)
        self.sts_ut_pos1.setObjectName(u"sts_ut_pos1")
        self.sts_ut_pos1.setGeometry(QRect(200, 40, 91, 21))
        self.sts_ut_pos1.setFont(font3)
        self.sts_ut_pos1.setAlignment(Qt.AlignCenter)
        self.sts_ut_pos2 = QLabel(self.groupBox_3)
        self.sts_ut_pos2.setObjectName(u"sts_ut_pos2")
        self.sts_ut_pos2.setGeometry(QRect(200, 70, 91, 21))
        self.sts_ut_pos2.setFont(font3)
        self.sts_ut_pos2.setAlignment(Qt.AlignCenter)
        self.sts_lt_pos2 = QLabel(self.groupBox_3)
        self.sts_lt_pos2.setObjectName(u"sts_lt_pos2")
        self.sts_lt_pos2.setGeometry(QRect(200, 160, 91, 21))
        self.sts_lt_pos2.setFont(font3)
        self.sts_lt_pos2.setAlignment(Qt.AlignCenter)
        self.sts_lt_pos3 = QLabel(self.groupBox_3)
        self.sts_lt_pos3.setObjectName(u"sts_lt_pos3")
        self.sts_lt_pos3.setGeometry(QRect(200, 190, 91, 16))
        self.sts_lt_pos3.setFont(font3)
        self.sts_lt_pos3.setAlignment(Qt.AlignCenter)
        self.sts_lt_pos4 = QLabel(self.groupBox_3)
        self.sts_lt_pos4.setObjectName(u"sts_lt_pos4")
        self.sts_lt_pos4.setGeometry(QRect(200, 220, 91, 21))
        self.sts_lt_pos4.setFont(font3)
        self.sts_lt_pos4.setAlignment(Qt.AlignCenter)
        self.sts_lt_pos5 = QLabel(self.groupBox_3)
        self.sts_lt_pos5.setObjectName(u"sts_lt_pos5")
        self.sts_lt_pos5.setGeometry(QRect(200, 250, 91, 21))
        self.sts_lt_pos5.setFont(font3)
        self.sts_lt_pos5.setAlignment(Qt.AlignCenter)
        self.label = QLabel(self.groupBox_3)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 30, 161, 31))
        font4 = QFont()
        font4.setPointSize(11)
        font4.setBold(True)
        font4.setWeight(75)
        self.label.setFont(font4)
        self.label.setAlignment(Qt.AlignCenter)
        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 120, 161, 31))
        self.label_2.setFont(font4)
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_15 = QLabel(self.groupBox_3)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(200, 0, 141, 21))
        self.label_15.setFont(font3)
        self.label_15.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.e_movinginterval = QLineEdit(self.groupBox_3)
        self.e_movinginterval.setObjectName(u"e_movinginterval")
        self.e_movinginterval.setGeometry(QRect(350, 0, 51, 20))
        self.e_movinginterval.setFont(font2)
        self.e_movinginterval.setLayoutDirection(Qt.LeftToRight)
        self.e_movinginterval.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Calibration Box Test", None))
        ___qtablewidgetitem = self.tb_calmode.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("Dialog", u"Frame Type", None));
        ___qtablewidgetitem1 = self.tb_calmode.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("Dialog", u"Exposure Time", None));
        ___qtablewidgetitem2 = self.tb_calmode.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("Dialog", u"Repeat", None));

        __sortingEnabled = self.tb_calmode.isSortingEnabled()
        self.tb_calmode.setSortingEnabled(False)
        ___qtablewidgetitem3 = self.tb_calmode.item(0, 0)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("Dialog", u"Dark", None));
        ___qtablewidgetitem4 = self.tb_calmode.item(0, 1)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem5 = self.tb_calmode.item(0, 2)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem6 = self.tb_calmode.item(1, 0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("Dialog", u"Flat ON", None));
        ___qtablewidgetitem7 = self.tb_calmode.item(1, 1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem8 = self.tb_calmode.item(1, 2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem9 = self.tb_calmode.item(2, 0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("Dialog", u"Flat OFF", None));
        ___qtablewidgetitem10 = self.tb_calmode.item(2, 1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem11 = self.tb_calmode.item(2, 2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem12 = self.tb_calmode.item(3, 0)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("Dialog", u"Th-Ar", None));
        ___qtablewidgetitem13 = self.tb_calmode.item(3, 1)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem14 = self.tb_calmode.item(3, 2)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem15 = self.tb_calmode.item(4, 0)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("Dialog", u"Pinhole-Flat", None));
        ___qtablewidgetitem16 = self.tb_calmode.item(4, 1)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem17 = self.tb_calmode.item(4, 2)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem18 = self.tb_calmode.item(5, 0)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("Dialog", u"Pinhole-ThAr", None));
        ___qtablewidgetitem19 = self.tb_calmode.item(5, 1)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem20 = self.tb_calmode.item(5, 2)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem21 = self.tb_calmode.item(6, 0)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("Dialog", u"USAF ON", None));
        ___qtablewidgetitem22 = self.tb_calmode.item(6, 1)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem23 = self.tb_calmode.item(6, 2)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem24 = self.tb_calmode.item(7, 0)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("Dialog", u"USAF OFF", None));
        ___qtablewidgetitem25 = self.tb_calmode.item(7, 1)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem26 = self.tb_calmode.item(7, 2)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("Dialog", u"1", None));
        ___qtablewidgetitem27 = self.tb_calmode.item(8, 0)
        ___qtablewidgetitem27.setText(QCoreApplication.translate("Dialog", u"PARKING", None));
        ___qtablewidgetitem28 = self.tb_calmode.item(8, 1)
        ___qtablewidgetitem28.setText(QCoreApplication.translate("Dialog", u"1.63", None));
        ___qtablewidgetitem29 = self.tb_calmode.item(8, 2)
        ___qtablewidgetitem29.setText(QCoreApplication.translate("Dialog", u"1", None));
        self.tb_calmode.setSortingEnabled(__sortingEnabled)

        self.chk_whole.setText(QCoreApplication.translate("Dialog", u"whole select", None))
        self.bt_run.setText(QCoreApplication.translate("Dialog", u"RUN", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Set motor position", None))
        self.bt_ltpos_set5.setText(QCoreApplication.translate("Dialog", u"Set", None))
        self.bt_ltpos_set1.setText(QCoreApplication.translate("Dialog", u"Set", None))
        self.bt_utpos_set1.setText(QCoreApplication.translate("Dialog", u"Set", None))
        self.bt_utpos_set2.setText(QCoreApplication.translate("Dialog", u"Set", None))
        self.sts_lt_pos1.setText(QCoreApplication.translate("Dialog", u"     position 1", None))
        self.bt_ltpos_prev.setText(QCoreApplication.translate("Dialog", u"\u25c0", None))
        self.bt_ltpos_set4.setText(QCoreApplication.translate("Dialog", u"Set", None))
        self.bt_ltpos_set3.setText(QCoreApplication.translate("Dialog", u"Set", None))
        self.bt_ltpos_set2.setText(QCoreApplication.translate("Dialog", u"Set", None))
        self.bt_utpos_next.setText(QCoreApplication.translate("Dialog", u"\u25b6", None))
        self.bt_utpos_prev.setText(QCoreApplication.translate("Dialog", u"\u25c0", None))
        self.bt_ltpos_next.setText(QCoreApplication.translate("Dialog", u"\u25b6", None))
        self.sts_ut_pos1.setText(QCoreApplication.translate("Dialog", u"      position 1", None))
        self.sts_ut_pos2.setText(QCoreApplication.translate("Dialog", u"position 2", None))
        self.sts_lt_pos2.setText(QCoreApplication.translate("Dialog", u"position 2", None))
        self.sts_lt_pos3.setText(QCoreApplication.translate("Dialog", u"position 3", None))
        self.sts_lt_pos4.setText(QCoreApplication.translate("Dialog", u"position 4", None))
        self.sts_lt_pos5.setText(QCoreApplication.translate("Dialog", u"position 5", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Upper Translator", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Lower Translator", None))
        self.label_15.setText(QCoreApplication.translate("Dialog", u"moving interval:", None))
    # retranslateUi

