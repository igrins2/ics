# -*- coding: utf-8 -*-
"""
Created on Oct 08, 2021

Modified on Jan 4, 2022

@author: hilee

1. cli
2. communicate with other package: DTP (CalBoxTest - DTP - HKP)
3. unit test
4. GUI

"""


import click

# DTP/CalBoxTest
from DTP.CalBoxTest.CalBoxTest_core import *

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
        
    args = [mode, exptime, repeat]
    calbox = CalBoxTest()
    calbox.RunMode(args)

def test_runmode():
    assert "runmode dark 1.63 1"
    

@click.command(help=CLASS_NAME + " Move Delta of motor, motor: UT/LT, delta: int")
@click.argument("motor", type=click.STRING)
@click.argument("delta", type=click.INT)
def movedelta(motor, delta):
    if (motor == "UT" or motor == "LT") is not True:
        print("Please select UT or LT.")
        return
    if delta < 1:
        print("Please input a number over the 0 for delta.")
        return
        
    calbox = CalBoxTest()
    calbox.MoveDelta(motor, delta)

def test_movedelta():
    assert "movedelta UT 10"  


@click.command(help=CLASS_NAME + " Set value for each position of motor, motor: UT/LT, position: int (UT: 0/1, LT:0-4), value: int")
@click.argument("motor", type=click.STRING)
@click.argument("position", type=click.INT)
@click.argument("value", type=click.INT)
def setpos(motor, position, value):
    if (motor == "UT" or motor == "LT") is not True:
        print("Please select UT or LT.")
        return
    if motor == "UT":
        if 0 > position or position > 1: 
            print("Please input a number 0 or 1 for UT.")
            return
    if motor == "LT":
        if 0 > position or position > 4:
            print("Please input a number 0-4 for LT.")
            return
        
    CalBox = CalBoxTest()
    CalBox.SetPosition(motor, position, value)

def test_setpos():
    assert "setpos LT 2 20000"
    

def CliCommand():
    cli.add_command(runmode)
    cli.add_command(movedelta)
    cli.add_command(setpos)
    cli()


if __name__ == "__main__":
    CliCommand()

