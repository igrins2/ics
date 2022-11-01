# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'EngineeringToolsCdebGm.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(249, 284)
        self.bt_runHKP = QPushButton(Dialog)
        self.bt_runHKP.setObjectName(u"bt_runHKP")
        self.bt_runHKP.setGeometry(QRect(30, 60, 101, 41))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.bt_runHKP.setFont(font)
        self.bt_runSCP = QPushButton(Dialog)
        self.bt_runSCP.setObjectName(u"bt_runSCP")
        self.bt_runSCP.setGeometry(QRect(30, 160, 101, 41))
        self.bt_runSCP.setFont(font)
        self.bt_runDTP = QPushButton(Dialog)
        self.bt_runDTP.setObjectName(u"bt_runDTP")
        self.bt_runDTP.setGeometry(QRect(30, 210, 101, 41))
        self.bt_runDTP.setFont(font)
        self.label_stsHKP = QLabel(Dialog)
        self.label_stsHKP.setObjectName(u"label_stsHKP")
        self.label_stsHKP.setGeometry(QRect(140, 70, 71, 19))
        self.label_stsHKP.setAlignment(Qt.AlignCenter)
        self.label_stsSCP = QLabel(Dialog)
        self.label_stsSCP.setObjectName(u"label_stsSCP")
        self.label_stsSCP.setGeometry(QRect(140, 170, 71, 19))
        self.label_stsSCP.setAlignment(Qt.AlignCenter)
        self.label_stsDTP = QLabel(Dialog)
        self.label_stsDTP.setObjectName(u"label_stsDTP")
        self.label_stsDTP.setGeometry(QRect(140, 220, 71, 19))
        self.label_stsDTP.setAlignment(Qt.AlignCenter)
        self.checkBox = QCheckBox(Dialog)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(30, 20, 151, 25))
        self.label_stsMACIE = QLabel(Dialog)
        self.label_stsMACIE.setObjectName(u"label_stsMACIE")
        self.label_stsMACIE.setGeometry(QRect(140, 120, 71, 19))
        self.label_stsMACIE.setAlignment(Qt.AlignCenter)
        self.bt_runMACIE = QPushButton(Dialog)
        self.bt_runMACIE.setObjectName(u"bt_runMACIE")
        self.bt_runMACIE.setGeometry(QRect(30, 110, 101, 41))
        self.bt_runMACIE.setFont(font)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"EngTools", None))
        self.bt_runHKP.setText(QCoreApplication.translate("Dialog", u"run HKP", None))
        self.bt_runSCP.setText(QCoreApplication.translate("Dialog", u"run SCP", None))
        self.bt_runDTP.setText(QCoreApplication.translate("Dialog", u"run DTP", None))
        self.label_stsHKP.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.label_stsSCP.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.label_stsDTP.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Simulation Mode", None))
        self.label_stsMACIE.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.bt_runMACIE.setText(QCoreApplication.translate("Dialog", u"run MACIE", None))
    # retranslateUi

