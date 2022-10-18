import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_HKP_mp import *
from HK_def import *

class ManualHeat(Ui_ManualHeat, QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        
        self.hk = parent
        self.heat_idx = 0
        
        self.pushButton.clicked.connect(self.value_changed)    
    
        
    def closeEvent(self, *args, **Kwargs):
        pass


    def showModal(self):
        return super().exec()
    
    
    def setTitile(self, ctrl, heater_name, cur_heating):
        
        self.heat_idx = ctrl
        msg = "Manual Heat Power: %s" % heater_name
        self.setWindowTitle(msg)
     
        self.lineEdit.setText(cur_heating)
        
        
    def value_changed(self):
        heating_pwr = float(self.lineEdit.text())
        if self.heat_idx == 4:
            self.hk.SetHeatingValue_manual(TMC3, 2, heating_pwr)
        else:
            self.hk.SetHeatingValue_manual(int(self.heat_idx/2), (self.heat_idx%2)+1, heating_pwr)

   
