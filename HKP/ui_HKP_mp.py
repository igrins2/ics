# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'HKP_mpJrWzoF.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_ManualHeat(object):
    def setupUi(self, ManualHeat):
        if not ManualHeat.objectName():
            ManualHeat.setObjectName(u"ManualHeat")
        ManualHeat.setEnabled(True)
        ManualHeat.resize(338, 63)
        ManualHeat.setModal(False)
        self.label = QLabel(ManualHeat)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 21, 201, 20))
        self.label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.pushButton = QPushButton(ManualHeat)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(273, 20, 51, 27))
        self.lineEdit = QLineEdit(ManualHeat)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(211, 20, 61, 27))

        self.retranslateUi(ManualHeat)

        QMetaObject.connectSlotsByName(ManualHeat)
    # setupUi

    def retranslateUi(self, ManualHeat):
        ManualHeat.setWindowTitle(QCoreApplication.translate("ManualHeat", u"Manual Heat Power", None))
        self.label.setText(QCoreApplication.translate("ManualHeat", u"Manual Heat Power(0-100): ", None))
        self.pushButton.setText(QCoreApplication.translate("ManualHeat", u"Input", None))
    # retranslateUi

