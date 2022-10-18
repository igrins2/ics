# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'EngineeringToolsRfbVsD.ui'
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
        Dialog.resize(240, 273)
        self.pushButton_15 = QPushButton(Dialog)
        self.pushButton_15.setObjectName(u"pushButton_15")
        self.pushButton_15.setGeometry(QRect(20, 60, 131, 41))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.pushButton_15.setFont(font)
        self.pushButton_16 = QPushButton(Dialog)
        self.pushButton_16.setObjectName(u"pushButton_16")
        self.pushButton_16.setGeometry(QRect(20, 160, 131, 41))
        self.pushButton_16.setFont(font)
        self.pushButton_17 = QPushButton(Dialog)
        self.pushButton_17.setObjectName(u"pushButton_17")
        self.pushButton_17.setGeometry(QRect(20, 210, 131, 41))
        self.pushButton_17.setFont(font)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(160, 70, 71, 19))
        self.label.setAlignment(Qt.AlignCenter)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(160, 170, 71, 19))
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(160, 220, 71, 19))
        self.label_3.setAlignment(Qt.AlignCenter)
        self.checkBox = QCheckBox(Dialog)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setGeometry(QRect(30, 20, 151, 25))
        self.pushButton_18 = QPushButton(Dialog)
        self.pushButton_18.setObjectName(u"pushButton_18")
        self.pushButton_18.setGeometry(QRect(20, 110, 131, 41))
        self.pushButton_18.setFont(font)
        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(160, 120, 71, 19))
        self.label_4.setAlignment(Qt.AlignCenter)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.pushButton_15.setText(QCoreApplication.translate("Dialog", u"run HKP", None))
        self.pushButton_16.setText(QCoreApplication.translate("Dialog", u"run SCP", None))
        self.pushButton_17.setText(QCoreApplication.translate("Dialog", u"run DTP", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Simulation Mode", None))
        self.pushButton_18.setText(QCoreApplication.translate("Dialog", u"run MACIE", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"GOOD", None))
    # retranslateUi

