# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ObsAppOviYCt.ui'
##
## Created by: Qt User Interface Compiler version 6.3.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGraphicsView,
    QGroupBox, QLabel, QLineEdit, QProgressBar,
    QPushButton, QRadioButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(844, 596)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.groupBox_18 = QGroupBox(Dialog)
        self.groupBox_18.setObjectName(u"groupBox_18")
        self.groupBox_18.setGeometry(QRect(10, 10, 241, 331))
        font = QFont()
        font.setPointSize(8)
        self.groupBox_18.setFont(font)
        self.label_61 = QLabel(self.groupBox_18)
        self.label_61.setObjectName(u"label_61")
        self.label_61.setGeometry(QRect(10, 50, 111, 20))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(False)
        self.label_61.setFont(font1)
        self.label_61.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_is_health = QLabel(self.groupBox_18)
        self.label_is_health.setObjectName(u"label_is_health")
        self.label_is_health.setGeometry(QRect(130, 50, 101, 20))
        self.label_is_health.setFont(font1)
        self.label_is_health.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_63 = QLabel(self.groupBox_18)
        self.label_63.setObjectName(u"label_63")
        self.label_63.setGeometry(QRect(10, 70, 111, 20))
        self.label_63.setFont(font1)
        self.label_63.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_GDSN_connection = QLabel(self.groupBox_18)
        self.label_GDSN_connection.setObjectName(u"label_GDSN_connection")
        self.label_GDSN_connection.setGeometry(QRect(130, 70, 101, 20))
        self.label_GDSN_connection.setFont(font1)
        self.label_GDSN_connection.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_65 = QLabel(self.groupBox_18)
        self.label_65.setObjectName(u"label_65")
        self.label_65.setGeometry(QRect(10, 90, 111, 20))
        self.label_65.setFont(font1)
        self.label_65.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_GMP_connection = QLabel(self.groupBox_18)
        self.label_GMP_connection.setObjectName(u"label_GMP_connection")
        self.label_GMP_connection.setGeometry(QRect(130, 90, 101, 20))
        self.label_GMP_connection.setFont(font1)
        self.label_GMP_connection.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_67 = QLabel(self.groupBox_18)
        self.label_67.setObjectName(u"label_67")
        self.label_67.setGeometry(QRect(10, 110, 111, 20))
        self.label_67.setFont(font1)
        self.label_67.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_state = QLabel(self.groupBox_18)
        self.label_state.setObjectName(u"label_state")
        self.label_state.setGeometry(QRect(130, 110, 101, 20))
        self.label_state.setFont(font1)
        self.label_state.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_69 = QLabel(self.groupBox_18)
        self.label_69.setObjectName(u"label_69")
        self.label_69.setGeometry(QRect(10, 130, 111, 20))
        self.label_69.setFont(font1)
        self.label_69.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_action_state = QLabel(self.groupBox_18)
        self.label_action_state.setObjectName(u"label_action_state")
        self.label_action_state.setGeometry(QRect(130, 130, 101, 20))
        self.label_action_state.setFont(font1)
        self.label_action_state.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_71 = QLabel(self.groupBox_18)
        self.label_71.setObjectName(u"label_71")
        self.label_71.setGeometry(QRect(10, 160, 111, 20))
        self.label_71.setFont(font1)
        self.label_71.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_vacuum = QLabel(self.groupBox_18)
        self.label_vacuum.setObjectName(u"label_vacuum")
        self.label_vacuum.setGeometry(QRect(130, 160, 101, 20))
        self.label_vacuum.setFont(font1)
        self.label_vacuum.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_73 = QLabel(self.groupBox_18)
        self.label_73.setObjectName(u"label_73")
        self.label_73.setGeometry(QRect(10, 190, 111, 20))
        self.label_73.setFont(font1)
        self.label_73.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_temp_detH = QLabel(self.groupBox_18)
        self.label_temp_detH.setObjectName(u"label_temp_detH")
        self.label_temp_detH.setGeometry(QRect(130, 190, 101, 20))
        self.label_temp_detH.setFont(font1)
        self.label_temp_detH.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_temp_detS = QLabel(self.groupBox_18)
        self.label_temp_detS.setObjectName(u"label_temp_detS")
        self.label_temp_detS.setGeometry(QRect(130, 230, 101, 20))
        self.label_temp_detS.setFont(font1)
        self.label_temp_detS.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_temp_detK = QLabel(self.groupBox_18)
        self.label_temp_detK.setObjectName(u"label_temp_detK")
        self.label_temp_detK.setGeometry(QRect(130, 210, 101, 20))
        self.label_temp_detK.setFont(font1)
        self.label_temp_detK.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_heater_detH = QLabel(self.groupBox_18)
        self.label_heater_detH.setObjectName(u"label_heater_detH")
        self.label_heater_detH.setGeometry(QRect(130, 250, 101, 20))
        self.label_heater_detH.setFont(font1)
        self.label_heater_detH.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_heater_detS = QLabel(self.groupBox_18)
        self.label_heater_detS.setObjectName(u"label_heater_detS")
        self.label_heater_detS.setGeometry(QRect(130, 290, 101, 20))
        self.label_heater_detS.setFont(font1)
        self.label_heater_detS.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_79 = QLabel(self.groupBox_18)
        self.label_79.setObjectName(u"label_79")
        self.label_79.setGeometry(QRect(10, 270, 111, 20))
        self.label_79.setFont(font1)
        self.label_79.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_heater_detK = QLabel(self.groupBox_18)
        self.label_heater_detK.setObjectName(u"label_heater_detK")
        self.label_heater_detK.setGeometry(QRect(130, 270, 101, 20))
        self.label_heater_detK.setFont(font1)
        self.label_heater_detK.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_81 = QLabel(self.groupBox_18)
        self.label_81.setObjectName(u"label_81")
        self.label_81.setGeometry(QRect(10, 210, 111, 20))
        self.label_81.setFont(font1)
        self.label_81.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_82 = QLabel(self.groupBox_18)
        self.label_82.setObjectName(u"label_82")
        self.label_82.setGeometry(QRect(10, 230, 111, 20))
        self.label_82.setFont(font1)
        self.label_82.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_83 = QLabel(self.groupBox_18)
        self.label_83.setObjectName(u"label_83")
        self.label_83.setGeometry(QRect(10, 250, 111, 20))
        self.label_83.setFont(font1)
        self.label_83.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_84 = QLabel(self.groupBox_18)
        self.label_84.setObjectName(u"label_84")
        self.label_84.setGeometry(QRect(10, 290, 111, 20))
        self.label_84.setFont(font1)
        self.label_84.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_85 = QLabel(self.groupBox_18)
        self.label_85.setObjectName(u"label_85")
        self.label_85.setGeometry(QRect(10, 10, 221, 20))
        font2 = QFont()
        font2.setPointSize(13)
        font2.setBold(True)
        self.label_85.setFont(font2)
        self.label_85.setAlignment(Qt.AlignCenter)
        self.graphicsView_expand = QGraphicsView(Dialog)
        self.graphicsView_expand.setObjectName(u"graphicsView_expand")
        self.graphicsView_expand.setGeometry(QRect(260, 14, 161, 151))
        self.graphicsView_expand.setFont(font)
        self.graphicsView_fitting = QGraphicsView(Dialog)
        self.graphicsView_fitting.setObjectName(u"graphicsView_fitting")
        self.graphicsView_fitting.setGeometry(QRect(420, 14, 161, 151))
        self.graphicsView_fitting.setFont(font)
        self.graphicsView_svc = QGraphicsView(Dialog)
        self.graphicsView_svc.setObjectName(u"graphicsView_svc")
        self.graphicsView_svc.setGeometry(QRect(260, 167, 321, 321))
        self.graphicsView_svc.setFont(font)
        self.graphicsView_profile = QGraphicsView(Dialog)
        self.graphicsView_profile.setObjectName(u"graphicsView_profile")
        self.graphicsView_profile.setGeometry(QRect(260, 490, 321, 81))
        self.graphicsView_profile.setFont(font)
        self.groupBox_19 = QGroupBox(Dialog)
        self.groupBox_19.setObjectName(u"groupBox_19")
        self.groupBox_19.setGeometry(QRect(10, 350, 241, 221))
        self.groupBox_19.setFont(font)
        self.label_86 = QLabel(self.groupBox_19)
        self.label_86.setObjectName(u"label_86")
        self.label_86.setGeometry(QRect(10, 50, 101, 20))
        self.label_86.setFont(font1)
        self.label_86.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_data_label = QLabel(self.groupBox_19)
        self.label_data_label.setObjectName(u"label_data_label")
        self.label_data_label.setGeometry(QRect(120, 50, 111, 20))
        self.label_data_label.setFont(font1)
        self.label_data_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_88 = QLabel(self.groupBox_19)
        self.label_88.setObjectName(u"label_88")
        self.label_88.setGeometry(QRect(10, 70, 101, 20))
        self.label_88.setFont(font1)
        self.label_88.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_obs_state = QLabel(self.groupBox_19)
        self.label_obs_state.setObjectName(u"label_obs_state")
        self.label_obs_state.setGeometry(QRect(120, 70, 111, 20))
        self.label_obs_state.setFont(font1)
        self.label_obs_state.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_90 = QLabel(self.groupBox_19)
        self.label_90.setObjectName(u"label_90")
        self.label_90.setGeometry(QRect(10, 90, 141, 20))
        self.label_90.setFont(font1)
        self.label_90.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_sampling_number = QLabel(self.groupBox_19)
        self.label_sampling_number.setObjectName(u"label_sampling_number")
        self.label_sampling_number.setGeometry(QRect(160, 90, 71, 20))
        self.label_sampling_number.setFont(font1)
        self.label_sampling_number.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_92 = QLabel(self.groupBox_19)
        self.label_92.setObjectName(u"label_92")
        self.label_92.setGeometry(QRect(10, 110, 141, 20))
        self.label_92.setFont(font1)
        self.label_92.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_exp_time = QLabel(self.groupBox_19)
        self.label_exp_time.setObjectName(u"label_exp_time")
        self.label_exp_time.setGeometry(QRect(160, 110, 71, 20))
        self.label_exp_time.setFont(font1)
        self.label_exp_time.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_94 = QLabel(self.groupBox_19)
        self.label_94.setObjectName(u"label_94")
        self.label_94.setGeometry(QRect(10, 130, 141, 20))
        self.label_94.setFont(font1)
        self.label_94.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_time_left = QLabel(self.groupBox_19)
        self.label_time_left.setObjectName(u"label_time_left")
        self.label_time_left.setGeometry(QRect(160, 130, 71, 20))
        self.label_time_left.setFont(font1)
        self.label_time_left.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_110 = QLabel(self.groupBox_19)
        self.label_110.setObjectName(u"label_110")
        self.label_110.setGeometry(QRect(10, 10, 221, 20))
        self.label_110.setFont(font2)
        self.label_110.setAlignment(Qt.AlignCenter)
        self.progressBar_obs = QProgressBar(self.groupBox_19)
        self.progressBar_obs.setObjectName(u"progressBar_obs")
        self.progressBar_obs.setGeometry(QRect(10, 180, 221, 20))
        font3 = QFont()
        font3.setPointSize(10)
        self.progressBar_obs.setFont(font3)
        self.progressBar_obs.setValue(24)
        self.label_IPA = QLabel(self.groupBox_19)
        self.label_IPA.setObjectName(u"label_IPA")
        self.label_IPA.setGeometry(QRect(160, 150, 71, 20))
        self.label_IPA.setFont(font1)
        self.label_IPA.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_97 = QLabel(self.groupBox_19)
        self.label_97.setObjectName(u"label_97")
        self.label_97.setGeometry(QRect(10, 150, 141, 20))
        self.label_97.setFont(font1)
        self.label_97.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.groupBox_20 = QGroupBox(Dialog)
        self.groupBox_20.setObjectName(u"groupBox_20")
        self.groupBox_20.setGeometry(QRect(590, 10, 241, 481))
        self.groupBox_20.setFont(font)
        self.label_112 = QLabel(self.groupBox_20)
        self.label_112.setObjectName(u"label_112")
        self.label_112.setGeometry(QRect(10, 40, 101, 20))
        self.label_112.setFont(font1)
        self.label_112.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_svc_filename = QLabel(self.groupBox_20)
        self.label_svc_filename.setObjectName(u"label_svc_filename")
        self.label_svc_filename.setGeometry(QRect(120, 40, 111, 20))
        self.label_svc_filename.setFont(font1)
        self.label_svc_filename.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_114 = QLabel(self.groupBox_20)
        self.label_114.setObjectName(u"label_114")
        self.label_114.setGeometry(QRect(10, 60, 101, 20))
        self.label_114.setFont(font1)
        self.label_114.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_svc_state = QLabel(self.groupBox_20)
        self.label_svc_state.setObjectName(u"label_svc_state")
        self.label_svc_state.setGeometry(QRect(120, 60, 111, 20))
        self.label_svc_state.setFont(font1)
        self.label_svc_state.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_116 = QLabel(self.groupBox_20)
        self.label_116.setObjectName(u"label_116")
        self.label_116.setGeometry(QRect(10, 80, 141, 20))
        self.label_116.setFont(font1)
        self.label_116.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_svc_sampling_number = QLabel(self.groupBox_20)
        self.label_svc_sampling_number.setObjectName(u"label_svc_sampling_number")
        self.label_svc_sampling_number.setGeometry(QRect(160, 80, 71, 20))
        self.label_svc_sampling_number.setFont(font1)
        self.label_svc_sampling_number.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.label_118 = QLabel(self.groupBox_20)
        self.label_118.setObjectName(u"label_118")
        self.label_118.setGeometry(QRect(10, 100, 141, 20))
        self.label_118.setFont(font1)
        self.label_118.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_122 = QLabel(self.groupBox_20)
        self.label_122.setObjectName(u"label_122")
        self.label_122.setGeometry(QRect(10, 10, 221, 20))
        self.label_122.setFont(font2)
        self.label_122.setAlignment(Qt.AlignCenter)
        self.progressBar_svc = QProgressBar(self.groupBox_20)
        self.progressBar_svc.setObjectName(u"progressBar_svc")
        self.progressBar_svc.setGeometry(QRect(10, 170, 221, 20))
        self.progressBar_svc.setFont(font3)
        self.progressBar_svc.setValue(24)
        self.lineEdit_svc_exp_time = QLineEdit(self.groupBox_20)
        self.lineEdit_svc_exp_time.setObjectName(u"lineEdit_svc_exp_time")
        self.lineEdit_svc_exp_time.setGeometry(QRect(160, 100, 61, 21))
        self.lineEdit_svc_exp_time.setFont(font)
        self.pushButton_single = QPushButton(self.groupBox_20)
        self.pushButton_single.setObjectName(u"pushButton_single")
        self.pushButton_single.setGeometry(QRect(10, 130, 101, 31))
        self.pushButton_single.setFont(font3)
        self.pushButton_stop_guide = QPushButton(self.groupBox_20)
        self.pushButton_stop_guide.setObjectName(u"pushButton_stop_guide")
        self.pushButton_stop_guide.setGeometry(QRect(160, 390, 71, 41))
        self.pushButton_stop_guide.setFont(font3)
        self.pushButton_slow_guide = QPushButton(self.groupBox_20)
        self.pushButton_slow_guide.setObjectName(u"pushButton_slow_guide")
        self.pushButton_slow_guide.setGeometry(QRect(10, 390, 141, 41))
        self.pushButton_slow_guide.setFont(font3)
        self.pushButton_center = QPushButton(self.groupBox_20)
        self.pushButton_center.setObjectName(u"pushButton_center")
        self.pushButton_center.setGeometry(QRect(10, 250, 51, 31))
        self.pushButton_center.setFont(font3)
        self.pushButton_minus_p = QPushButton(self.groupBox_20)
        self.pushButton_minus_p.setObjectName(u"pushButton_minus_p")
        self.pushButton_minus_p.setGeometry(QRect(40, 350, 31, 31))
        self.pushButton_minus_p.setFont(font1)
        self.pushButton_plus_q = QPushButton(self.groupBox_20)
        self.pushButton_plus_q.setObjectName(u"pushButton_plus_q")
        self.pushButton_plus_q.setGeometry(QRect(70, 320, 31, 31))
        self.pushButton_plus_q.setFont(font1)
        self.pushButton_minus_q = QPushButton(self.groupBox_20)
        self.pushButton_minus_q.setObjectName(u"pushButton_minus_q")
        self.pushButton_minus_q.setGeometry(QRect(10, 320, 31, 31))
        self.pushButton_minus_q.setFont(font1)
        self.pushButton_plus_p = QPushButton(self.groupBox_20)
        self.pushButton_plus_p.setObjectName(u"pushButton_plus_p")
        self.pushButton_plus_p.setGeometry(QRect(40, 290, 31, 31))
        self.pushButton_plus_p.setFont(font1)
        self.radioButton_5 = QRadioButton(self.groupBox_20)
        self.radioButton_5.setObjectName(u"radioButton_5")
        self.radioButton_5.setGeometry(QRect(76, 445, 81, 21))
        self.radioButton_5.setFont(font3)
        self.radioButton_raw_sub = QRadioButton(self.groupBox_20)
        self.radioButton_raw_sub.setObjectName(u"radioButton_raw_sub")
        self.radioButton_raw_sub.setGeometry(QRect(20, 445, 51, 21))
        self.radioButton_raw_sub.setFont(font3)
        self.pushButton_continuous = QPushButton(self.groupBox_20)
        self.pushButton_continuous.setObjectName(u"pushButton_continuous")
        self.pushButton_continuous.setGeometry(QRect(120, 130, 111, 31))
        self.pushButton_continuous.setFont(font3)
        self.checkBox_auto_save = QCheckBox(self.groupBox_20)
        self.checkBox_auto_save.setObjectName(u"checkBox_auto_save")
        self.checkBox_auto_save.setGeometry(QRect(80, 195, 91, 25))
        self.checkBox_auto_save.setFont(font3)
        self.checkBox_off_slit = QCheckBox(self.groupBox_20)
        self.checkBox_off_slit.setObjectName(u"checkBox_off_slit")
        self.checkBox_off_slit.setGeometry(QRect(170, 253, 61, 25))
        self.checkBox_off_slit.setFont(font3)
        self.lineEdit_repeat_file_name = QLineEdit(self.groupBox_20)
        self.lineEdit_repeat_file_name.setObjectName(u"lineEdit_repeat_file_name")
        self.lineEdit_repeat_file_name.setGeometry(QRect(80, 220, 91, 21))
        self.lineEdit_repeat_file_name.setFont(font)
        self.label_119 = QLabel(self.groupBox_20)
        self.label_119.setObjectName(u"label_119")
        self.label_119.setGeometry(QRect(10, 220, 61, 20))
        self.label_119.setFont(font1)
        self.label_119.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.pushButton_repeat_filesave = QPushButton(self.groupBox_20)
        self.pushButton_repeat_filesave.setObjectName(u"pushButton_repeat_filesave")
        self.pushButton_repeat_filesave.setGeometry(QRect(170, 220, 41, 21))
        self.pushButton_repeat_filesave.setFont(font3)
        self.lineEdit_repeat_number = QLineEdit(self.groupBox_20)
        self.lineEdit_repeat_number.setObjectName(u"lineEdit_repeat_number")
        self.lineEdit_repeat_number.setGeometry(QRect(210, 220, 21, 21))
        self.lineEdit_repeat_number.setFont(font3)
        self.lineEdit_repeat_number.setAlignment(Qt.AlignCenter)
        self.pushButton_set_guide_star = QPushButton(self.groupBox_20)
        self.pushButton_set_guide_star.setObjectName(u"pushButton_set_guide_star")
        self.pushButton_set_guide_star.setGeometry(QRect(70, 250, 91, 31))
        self.pushButton_set_guide_star.setFont(font3)
        self.label_120 = QLabel(self.groupBox_20)
        self.label_120.setObjectName(u"label_120")
        self.label_120.setGeometry(QRect(105, 325, 71, 20))
        self.label_120.setFont(font1)
        self.label_120.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.lineEdit_offset = QLineEdit(self.groupBox_20)
        self.lineEdit_offset.setObjectName(u"lineEdit_offset")
        self.lineEdit_offset.setGeometry(QRect(180, 325, 51, 21))
        self.lineEdit_offset.setFont(font3)
        self.pushButton_mark_sky = QPushButton(self.groupBox_20)
        self.pushButton_mark_sky.setObjectName(u"pushButton_mark_sky")
        self.pushButton_mark_sky.setGeometry(QRect(160, 440, 71, 31))
        self.pushButton_mark_sky.setFont(font3)
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(590, 500, 241, 71))
        self.lineEdit_zscale_min = QLineEdit(self.groupBox)
        self.lineEdit_zscale_min.setObjectName(u"lineEdit_zscale_min")
        self.lineEdit_zscale_min.setGeometry(QRect(100, 40, 61, 21))
        self.lineEdit_zscale_min.setFont(font)
        self.label_autoscale = QLabel(self.groupBox)
        self.label_autoscale.setObjectName(u"label_autoscale")
        self.label_autoscale.setGeometry(QRect(110, 10, 111, 25))
        self.label_autoscale.setFont(font1)
        self.label_autoscale.setAlignment(Qt.AlignCenter)
        self.radioButton_2 = QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName(u"radioButton_2")
        self.radioButton_2.setGeometry(QRect(20, 37, 61, 25))
        self.radioButton_2.setFont(font3)
        self.radioButton_autoscale_zscale = QRadioButton(self.groupBox)
        self.radioButton_autoscale_zscale.setObjectName(u"radioButton_autoscale_zscale")
        self.radioButton_autoscale_zscale.setGeometry(QRect(20, 10, 81, 25))
        self.radioButton_autoscale_zscale.setFont(font3)
        self.lineEdit_zscale_max = QLineEdit(self.groupBox)
        self.lineEdit_zscale_max.setObjectName(u"lineEdit_zscale_max")
        self.lineEdit_zscale_max.setGeometry(QRect(170, 40, 61, 21))
        self.lineEdit_zscale_max.setFont(font)
        self.label_messagebar = QLabel(Dialog)
        self.label_messagebar.setObjectName(u"label_messagebar")
        self.label_messagebar.setGeometry(QRect(10, 574, 821, 20))
        font4 = QFont()
        font4.setBold(True)
        self.label_messagebar.setFont(font4)
        self.label_messagebar.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.groupBox_18.setTitle("")
        self.label_61.setText(QCoreApplication.translate("Dialog", u"IGRINS-2 Health:", None))
        self.label_is_health.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.label_63.setText(QCoreApplication.translate("Dialog", u"GDSN Status:", None))
        self.label_GDSN_connection.setText(QCoreApplication.translate("Dialog", u"Disconnected", None))
        self.label_65.setText(QCoreApplication.translate("Dialog", u"GMP Status:", None))
        self.label_GMP_connection.setText(QCoreApplication.translate("Dialog", u"Disconnected", None))
        self.label_67.setText(QCoreApplication.translate("Dialog", u"State:", None))
        self.label_state.setText(QCoreApplication.translate("Dialog", u"Running", None))
        self.label_69.setText(QCoreApplication.translate("Dialog", u"Action State:", None))
        self.label_action_state.setText(QCoreApplication.translate("Dialog", u"Idle", None))
        self.label_71.setText(QCoreApplication.translate("Dialog", u"Press (Torr):", None))
        self.label_vacuum.setText(QCoreApplication.translate("Dialog", u"9.99e+1", None))
        self.label_73.setText(QCoreApplication.translate("Dialog", u"Det H (K):", None))
        self.label_temp_detH.setText(QCoreApplication.translate("Dialog", u"65.0", None))
        self.label_temp_detS.setText(QCoreApplication.translate("Dialog", u"65.0", None))
        self.label_temp_detK.setText(QCoreApplication.translate("Dialog", u"65.0", None))
        self.label_heater_detH.setText(QCoreApplication.translate("Dialog", u"50", None))
        self.label_heater_detS.setText(QCoreApplication.translate("Dialog", u"50", None))
        self.label_79.setText(QCoreApplication.translate("Dialog", u"Heater K (%):", None))
        self.label_heater_detK.setText(QCoreApplication.translate("Dialog", u"50", None))
        self.label_81.setText(QCoreApplication.translate("Dialog", u"Det K (K):", None))
        self.label_82.setText(QCoreApplication.translate("Dialog", u"Det S (K):", None))
        self.label_83.setText(QCoreApplication.translate("Dialog", u"Heater H (%):", None))
        self.label_84.setText(QCoreApplication.translate("Dialog", u"Heater S (%):", None))
        self.label_85.setText(QCoreApplication.translate("Dialog", u"Instrument Status", None))
        self.groupBox_19.setTitle("")
        self.label_86.setText(QCoreApplication.translate("Dialog", u"Data Label:", None))
        self.label_data_label.setText(QCoreApplication.translate("Dialog", u"S20221020S0001", None))
        self.label_88.setText(QCoreApplication.translate("Dialog", u"Observing State:", None))
        self.label_obs_state.setText(QCoreApplication.translate("Dialog", u"---", None))
        self.label_90.setText(QCoreApplication.translate("Dialog", u"Fowler Sampling:", None))
        self.label_sampling_number.setText(QCoreApplication.translate("Dialog", u"16", None))
        self.label_92.setText(QCoreApplication.translate("Dialog", u"Exposure Time (sec):", None))
        self.label_exp_time.setText(QCoreApplication.translate("Dialog", u"123456.32", None))
        self.label_94.setText(QCoreApplication.translate("Dialog", u"Time Left:", None))
        self.label_time_left.setText(QCoreApplication.translate("Dialog", u"0", None))
        self.label_110.setText(QCoreApplication.translate("Dialog", u"Science Observation", None))
        self.label_IPA.setText(QCoreApplication.translate("Dialog", u"90", None))
        self.label_97.setText(QCoreApplication.translate("Dialog", u"IPA (deg):", None))
        self.groupBox_20.setTitle("")
        self.label_112.setText(QCoreApplication.translate("Dialog", u"File Name:", None))
        self.label_svc_filename.setText(QCoreApplication.translate("Dialog", u"S20221020S0001", None))
        self.label_114.setText(QCoreApplication.translate("Dialog", u"Observing State:", None))
        self.label_svc_state.setText(QCoreApplication.translate("Dialog", u"---", None))
        self.label_116.setText(QCoreApplication.translate("Dialog", u"Fowler Sampling:", None))
        self.label_svc_sampling_number.setText(QCoreApplication.translate("Dialog", u"16", None))
        self.label_118.setText(QCoreApplication.translate("Dialog", u"Exposure Time (sec):", None))
        self.label_122.setText(QCoreApplication.translate("Dialog", u"Slit View Camera", None))
        self.pushButton_single.setText(QCoreApplication.translate("Dialog", u"Single/Abort", None))
        self.pushButton_stop_guide.setText(QCoreApplication.translate("Dialog", u"Stop\n"
"Guide", None))
        self.pushButton_slow_guide.setText(QCoreApplication.translate("Dialog", u"Slow Guide", None))
        self.pushButton_center.setText(QCoreApplication.translate("Dialog", u"Center", None))
        self.pushButton_minus_p.setText(QCoreApplication.translate("Dialog", u"-p", None))
        self.pushButton_plus_q.setText(QCoreApplication.translate("Dialog", u"+q", None))
        self.pushButton_minus_q.setText(QCoreApplication.translate("Dialog", u"-q", None))
        self.pushButton_plus_p.setText(QCoreApplication.translate("Dialog", u"+p", None))
        self.radioButton_5.setText(QCoreApplication.translate("Dialog", u"Sub (Sky)", None))
        self.radioButton_raw_sub.setText(QCoreApplication.translate("Dialog", u"Raw", None))
        self.pushButton_continuous.setText(QCoreApplication.translate("Dialog", u"Continous/Stop", None))
        self.checkBox_auto_save.setText(QCoreApplication.translate("Dialog", u"Auto save", None))
        self.checkBox_off_slit.setText(QCoreApplication.translate("Dialog", u"Off-slit", None))
        self.label_119.setText(QCoreApplication.translate("Dialog", u"Filename:", None))
        self.pushButton_repeat_filesave.setText(QCoreApplication.translate("Dialog", u"save", None))
        self.lineEdit_repeat_number.setText(QCoreApplication.translate("Dialog", u"5", None))
        self.pushButton_set_guide_star.setText(QCoreApplication.translate("Dialog", u"Set Guide star", None))
        self.label_120.setText(QCoreApplication.translate("Dialog", u"Offset(\") =", None))
        self.pushButton_mark_sky.setText(QCoreApplication.translate("Dialog", u"Mark Sky", None))
        self.groupBox.setTitle("")
        self.label_autoscale.setText(QCoreApplication.translate("Dialog", u"10 ~ 500", None))
        self.radioButton_2.setText(QCoreApplication.translate("Dialog", u"zscale", None))
        self.radioButton_autoscale_zscale.setText(QCoreApplication.translate("Dialog", u"autoscale", None))
        self.label_messagebar.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
    # retranslateUi

