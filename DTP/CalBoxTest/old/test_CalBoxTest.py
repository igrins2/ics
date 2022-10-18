# -*- coding: utf-8 -*-
"""
Created on Oct 08, 2021

Modified on Oct 25, 2021

@author: hilee

1. cli
2. communicate with other package: DTP (HKP for test)
3. unit test
4. GUI

"""

import click

# DTP/CalBoxTest


CLASS_NAME = "[Calibration Box Test]"
DEFAULT_EXPTIME = 1.63
DEFAULT_REPEAT = 1

DARK = 0
FLAT = 1
FLATOFF = 2
THAR = 3
FOCUS = 4
HOME = 5

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

# group: cli
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@click.command(help=CLASS_NAME + " Run mode, mode: dark/flat/flatoff/thar/focus/home, exptime: float, repeat: int")
@click.argument("mode", type=click.STRING)
@click.argument("exptime", type=click.FLOAT)
@click.argument("repeat", type=click.INT)
def runmode(mode, exptime, repeat):
    if (mode == "dark" or mode == "flat" or mode == "flatoff" or mode == "thar" or mode == "focus" or mode == "home") is not True :
        print("Please select the mode of dark, flat, flatoff, thar, focus, or home.")
        return
    if exptime < 0:
        print("Please input a number over the 0 for exptime.")
        return
    if repeat < 1:
        print("Please input a number over the 0 for repeat.")
        return        
        
    CalBox = CalBoxTest()
    CalBox.RunMode(mode, exptime, repeat)

def test_runmode():
    assert "runmode dark 1.63 1"

@click.command(help=CLASS_NAME + " Move Delta of motor, motor: UT/BT, delta: int")
@click.argument("motor", type=click.STRING)
@click.argument("delta", type=click.INT)
def movedelta(motor, delta):
    if (motor == "UT" or motor == "BT") is not True:
        print("Please select UT or BT.")
        return
    if delta < 1:
        print("Please input a number over the 0 for delta.")
        return
        
    CalBox = CalBoxTest()
    CalBox.MoveDelta(motor, delta)
    
def test_movedelta():
    assert "movedelta UT 10"  


@click.command(help=CLASS_NAME + " Set value for each position of motor, motor: UT/BT, position: int (UT: 0/1, BT:0-4), value: int")
@click.argument("motor", type=click.STRING)
@click.argument("position", type=click.INT)
@click.argument("value", type=click.INT)
def setpos(motor, position, value):
    if (motor == "UT" or motor == "BT") is not True:
        print("Please select UT or BT.")
        return
    if motor == "UT":
        if 0 > position or position > 1: 
            print("Please input a number 0 or 1 for UT.")
            return
    if motor == "BT":
        if 0 > position or position > 4:
            print("Please input a number 0-4 for BT.")
            return
        
    CalBox = CalBoxTest()
    CalBox.SetPosition(motor, position, value)

def test_setpos():
    assert "setpos BT 2 20000"
    

class CalBoxTest() :
    def __init__(self):
        self.fExpTime, self.nRepeat = [DEFAULT_EXPTIME], [DEFAULT_REPEAT]

    def RunMode(self, mode, fExpTime, nRepeat):
        # self.hDt.CalBox_ChangeMode(mode, fExpTime, nRepeat)
        print(CLASS_NAME + " RunMode:", mode, fExpTime, nRepeat)

    def MoveDelta(self, motor, nDelta):
        # self.hDt.CalBox_MoveDelta(motor, fDelta)
        print(CLASS_NAME + " MoveDelta", motor, nDelta)

    def SetPosition(self, motor, position, nValue):
        # self.hDt.CalBox_SetPosition(motor, position, fValue)
        print(CLASS_NAME + " SetPosition", motor, position, nValue)


def CliCommand():
    cli.add_command(runmode)
    cli.add_command(movedelta)
    cli.add_command(setpos)
    cli()


if __name__ == "__main__":

    # test = CalBoxText()
    # test.__init__()
    CliCommand()

