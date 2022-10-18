# -*- coding: utf-8 -*-
"""
Created on Sep 17, 2021

Modified on Dec 08, 2021

@author: hilee

1. cli - ok
2. unit test - ok
3. communicate with components: multi thread, Async, non-blocking
4. communicate with other packages: DTP, GMP, ICS
5. GUI - ok
6. firebase

"""

import click
                
#from definition import *
from HKP.HK_core import *

# group: cli
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass

@click.command(help=CLASS_NAME + " Get Set Point from TMC1(1,2), TMC2(1,2), TMC3(2), count:int")
@click.argument("count", type=click.INT)
def getsetpoint(count):
    hk = HK()
    #connect
    print("---------------------------------------------------------")
    for i in range(3):
        hk.ConnectToComponent(i)
    print("---------------------------------------------------------")
    #read
    for _ in range(count):
        hk.GetSetPointfromTMC(TMC1, 1)   # bench set point
        hk.GetSetPointfromTMC(TMC1, 2)  # Grating set point
        hk.GetSetPointfromTMC(TMC2, 1)  # SVC set point
        hk.GetSetPointfromTMC(TMC2, 2)  # Detector K set point
        hk.GetSetPointfromTMC(TMC3, 2)  # Detector H set point
        print("---------------------------------------------------------")
        
    for i in range(3):
        hk.CloseComponent(i)
        

def test_getsetpoint():
    assert "getsetpoint 5"
    

@click.command(help=CLASS_NAME + " Get Heating value from TMC1(1,2), TMC2(1,2), TMC3(2), count:int")
@click.argument("count", type=click.INT)
def getheatvalue(count):
    hk = HK()
    #connect
    print("---------------------------------------------------------")
    for i in range(3):
        hk.ConnectToComponent(i)
    print("---------------------------------------------------------")
    #read
    for i in range(count):
        hk.GetHeatingValue(TMC1, 1)  # bench heating
        hk.GetHeatingValue(TMC1, 2)  # Grating heating
        hk.GetHeatingValue(TMC2, 1)  # SVC heating
        hk.GetHeatingValue(TMC2, 2)  # Detector K heating
        hk.GetHeatingValue(TMC3, 2)  # Detector H heating
        print("---------------------------------------------------------")
        
    for i in range(3):
        hk.CloseComponent(i)
        
def test_getheatvalue():
    assert "getheatvalue 5"

@click.command(help=CLASS_NAME + " Get value from TMC1(1,2), TMC2(1,2), TMC3(1, 2), TM(1-8), VM, count:int")
@click.argument("count", type=click.INT)
def getvalue(count):
    hk = HK()
    #connect
    print("---------------------------------------------------------")
    for i in range(5):
        hk.ConnectToComponent(i)
    print("---------------------------------------------------------")
    #read
    for i in range(count):
        hk.GetValuefromTMC(TMC1, "A")  # bench monitoring
        hk.GetValuefromTMC(TMC1, "B")  # Grating monitoring
        hk.GetValuefromTMC(TMC2, "A")  # SVC monitoring
        hk.GetValuefromTMC(TMC2, "B")  # Detector K monitoring
        hk.GetValuefromTMC(TMC3, "A")  # Camera H monitoring
        hk.GetValuefromTMC(TMC3, "B")  # Detector H monitoring
        
        for i in range(TM_CNT):
            hk.GetValuefromTM(i+1)
        
        hk.GetValuefromVM()         
        print("---------------------------------------------------------")
    
    for i in range(5):
        hk.CloseComponent(i)
        
def test_getvalue():
    assert "getvalue 5"

@click.command(help=CLASS_NAME + " Power Status")
def powersts():
    hk = HK()
    hk.ConnectToComponent(PDU)
    print("---------------------------------------------------------")
    hk.InitPDU()
    print("---------------------------------------------------------")
    hk.CloseComponent(PDU)
 
def test_powersts():
    assert "powersts"
    
 
@click.command(help=CLASS_NAME +
               " Change power, index: int (1:MACIE 5V, 2:VM 24V, 3:Motor 24V, 4:TH lamp 24V, 5:HC lamp 24V, 0:all), onoff:on/off")
@click.argument("index", type=click.INT)
@click.argument("onoff", type=click.STRING)
def poweronoff(index, onoff):
        
    if (onoff == "on" or onoff == "off") is not True:
        print("Please input on or off")
        return
    
    hk = HK()
    hk.ConnectToComponent(PDU)
    hk.InitPDU()
    
    print("---------------------------------------------------------")
    if index == 0:
        for i in range(PDU_IDX):
            hk.PowChange(i+1, onoff)
    else:
        hk.PowChange(index, onoff)
        
    hk.CloseComponent(PDU)

def test_poweronoff():
    assert "poweronoff 3 off"
    

@click.command(help=CLASS_NAME + " Initialize motor, motor:UT/LT")
@click.argument("motor", type=click.STRING)
def initmotor(motor):
    if (motor == "UT" or motor == "LT") is not True:
        print("Please select UT or LT.")
        return
    
    motornum = -1
    if motor == "UT":
        motornum = MOTOR_UT
    elif motor == "LT":
        motornum = MOTOR_LT

    hk = HK()
    hk.ConnectToComponent(5+motornum)
    hk.InitMotor(motornum)
    hk.CloseComponent(5+motornum)
   
def test_initmotor():
    assert "initmotor UT"
    

@click.command(help=CLASS_NAME + " Move motor, motor:UT/LT, posnum:int(UT:0/1, LT:0-4)")
@click.argument("motor", type=click.STRING)
@click.argument("posnum", type=click.INT)
def motormove(motor, posnum):
    
    #print("go")
    if (motor == "UT" or motor == "LT") is not True:
        print("Please select UT or LT.")
        return
    if motor == "UT":
        if 0 > posnum or posnum > 1: 
            print("Please input a number 0 or 1 for UT.")
            return
    if motor == "LT":
        if 0 > posnum or posnum > 4:
            print("Please input a number 0-4 for LT.")
            return
    
    motornum = -1
    if motor == "UT":
        motornum = MOTOR_UT
    elif motor == "LT":
        motornum = MOTOR_LT

    hk = HK()
    hk.ConnectToComponent(5+motornum)
    hk.MotorMove(motornum, posnum)
    hk.CloseComponent(5+motornum)

def test_motormove():
    assert "motormove UT 1"

@click.command(help=CLASS_NAME + " Go Delta of motor, motor:UT/LT, delta:int")
@click.argument("motor", type=click.STRING)
@click.argument("delta", type=click.INT)
def motorgodelta(motor, delta):
    if (motor == "UT" or motor == "LT") is not True:
        print("Please select UT or LT.")
        return
   
    if delta < 1:
        print("Please input a number over the 0 for delta.")
        return

    motornum = -1
    if motor == "UT":
        motornum = MOTOR_UT
    elif motor == "LT":
        motornum = MOTOR_LT

    hk = HK()
    hk.ConnectToComponent(5+motornum)
    hk.MotorMoveDelta(motornum, True, delta)
    hk.CloseComponent(5+motornum)
    

@click.command(help=CLASS_NAME + " Back Delta of motor, motor:UT/LT, delta:int")
@click.argument("motor", type=click.STRING)
@click.argument("delta", type=click.INT)
def motorbackdelta(motor, delta):
    if (motor == "UT" or motor == "LT") is not True:
        print("Please select UT or LT.")
        return
   
    if delta < 1:
        print("Please input a number over the 0 for delta.")
        return

    motornum = -1
    if motor == "UT":
        motornum = MOTOR_UT
    elif motor == "LT":
        motornum = MOTOR_LT

    hk = HK()
    hk.ConnectToComponent(5+motornum)
    hk.MotorMoveDelta(motornum, False, delta)
    hk.CloseComponent(5+motornum)
    

def test_motormovedelta():
    assert "motormovedelta UT 1 50"

    
@click.command(help=CLASS_NAME + " Set motor position (UT), posnum:0/1")
@click.argument("posnum", type=click.INT)
def setut(posnum):
    if 0 > posnum or posnum > 1: 
        print("Please input a number 0 or 1 for UT.")
        return
        
    hk = HK()
    hk.ConnectToComponent(UT)
    hk.SetUT(posnum)
    hk.CloseComponent(UT)

def test_setut():
    assert "setut 0"
    

@click.command(help=CLASS_NAME + " Set motor position (LT), posnum:0-4")
@click.argument("posnum", type=click.INT)
def setlt(posnum):
    if 0 > posnum or posnum > 4:
        print("Please input a number 0-4 for LT.")
        return
        
    hk = HK()
    hk.ConnectToComponent(LT)
    hk.SetLT(posnum)
    hk.CloseComponent(LT)

def test_setlt():
    assert "setlt 1"

  

def CliCommand():
    cli.add_command(getsetpoint)
    cli.add_command(getheatvalue)
    cli.add_command(getvalue)
    cli.add_command(powersts)
    cli.add_command(poweronoff)
    
    cli.add_command(initmotor)
    cli.add_command(motormove)
    cli.add_command(motorgodelta)
    cli.add_command(motorbackdelta)
    cli.add_command(setut)
    cli.add_command(setlt)
    cli()


if __name__ == "__main__":
    CliCommand()

