# -*- coding: utf-8 -*-
'''
Created on Oct 12, 2021

@author: hilee
'''

H = 'h'
K = 'k'

class DT():

    def __init__(self):
        self.fExpTime = 0.0
        self.fFowlerTime = 0.0
    
    #main
    def ConnectToPackages(self):
        #self.client_hk
        #self.client_sc
        #self.client_det[H]
        #self.client_det[K]
        pass
    
    
    #--------------------------------------------------
    def ConnectToHKP(self):
        pass
    
    def ConnectToSCP(self):
        pass
    
    def ConnectToDCS(self, detector):
        pass
    
    #--------------------------------------------------
    
    
    #main
    def ReadTCSInfo(self):
        pass
    
    #main
    def InitializeDCS(self, detector):
        pass
    
    #--------------------------------------------------
    def Initialize(self, detector):
        pass
    
    def DownloadMCD(self, detector):
        pass
    
    def SetDetector(self, detector):
        pass
    
    def SetFSMode(self, detector):
        pass
    #--------------------------------------------------
    
    #main
    def MoveSelectTarget(self):
        pass
    
    #main
    def SingleExp(self, exptime):
        pass
    
    #--------------------------------------------------
    def SetFSParam(self, detector, *param):
        pass
    
    def AcquireRamp(self, detector):
        pass
    
    #--------------------------------------------------
    
    #main
    def StopExp(self, detector):
        self.StopAcquisition(detector)
    
    #--------------------------------------------------
    def StopAcquisition(self, detector):
        pass
    
    #--------------------------------------------------
    
    #main
    def SaveFits(self, detector):
        pass
    
    #main
    def StartSequence(self):
        pass
    
    #main
    def StopSequence(self):
        pass
    
    #--------------------------------------------------
    #Cal box test -> HKP for 1 line
    def CalBox_Mode(self, mode, fExptime, nRepeat):
        #sendToHK("[DT_to_HK]Change Mode: Dark")
        '''
        for list in args:            
       #     value = 
       #     print("test: ", value)
            for value in list:
                mode = value[0]
                fExpTime = value[1]
                nRepeat = value[2]
        '''
        print('[DT] CalBox_Mode:', mode, fExptime, nRepeat)
        

        
    def CalBox_MoveDelta(self, motor, nDelta):
        print('[DT] CalBox_MoveDelta:', motor, nDelta)
        

        