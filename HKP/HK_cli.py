# -*- coding: utf-8 -*-
"""
Created on Sep 17, 2021

Modified on Dec 29, 2021

@author: hilee

1. cli - ok
2. unit test - ok
3. communicate with components: multi thread, Async, non-blocking
4. communicate with other packages: DTP, GMP, ICS
5. GUI - ok
6. firebase

"""

#import os, sys          
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import click

from HKP.HK_def import *
from HKP.temp_ctrl import *
from HKP.monitor import *
from HKP.pdu import *
from HKP.motor import *

import subprocess

# group: cli
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


def show_func(show):
    if show:
        print("------------------------------------------\n"
            "Usage: Command [Options] [Args]...\n\n"
            "Options:\n"
            "  -h, --help  Show this message and exit.\n\n"
            "Command:\n"
            "  show\n"  
            "  getsetpoint index port\n" 
            "  getheatvalue index port\n"
            "  gettempvalue index port\n"
            "  getvacuumvalue\n"
            "  poweronoff index onoff\n"
            "  initmotor motor\n"
            "  motormove motor posnum\n"
            "  motorgo motor delta\n"   
            "  motorback motor delta\n"    
            "  setlt posnum\n"   
            "  setut posnum\n" 
            "  exit\n"
            "------------------------------------------")
    print("(If you want to show commands, type 'show'!!!)\n")
    print(">>", end=" ")
    args = list(input().split())
    return args


def show_subfunc(cmd, *args):
    msg = "Usage: %s [Options] %s\n\n  %s\n\n" % (cmd, args[0], args[1])
    print(msg+"Options:\n" 
               "  -h, --help  Show this message and exit")

def show_errmsg(args):
    print("Please input '%s' or '-h'/'--help'." % args)


def show_noargs(cmd):
    msg = "'%s' has no arguments. Please use just command." % cmd
    print(msg)


@click.command("start")
def start():
                
    print( '================================================\n'+
           '                Ctrl + C to exit or type: exit  \n'+
           '================================================\n')

    args = ""
    args = show_func(True)
    
    hk = [None for _ in range(COM_CNT)]
    
    while(True):
        while len(args) < 1:
            args = show_func(False)
        
        #print(args)
        if args[0] == "show":
            args = show_func(True)
                
        if args[0] == "getsetpoint" or args[0] == "getheatvalue":
            _args = "index, port"
            
            try:
                if len(args) < 2:
                    show_errmsg(_args)
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "index:int(1~3), port:int(1~2, 0:all)")   
                elif len(args) < 3:
                    show_errmsg(_args)         
                elif (1 <= int(args[1]) <= 3) is not True:    
                    print("Please input 1~3 for index.")
                elif (0 <= int(args[2]) <= 2) is not True:
                    print("Please input 0~2 for port.")
                else:
                    port = "%d" % (int(args[1]) + 10000)
                    temp = int(args[1])-1
                    if hk[temp] == None:
                        hk[temp] = temp_ctrl(port)
                        hk[temp].connect_to_component()
                        
                    if args[0] == "getsetpoint":
                        if args[2] == "0":
                            hk[temp].get_setpoint(1)
                            hk[temp].get_setpoint(2)
                            #(0.5)
                        else:
                            hk[temp].get_setpoint(int(args[2]))
                    elif args[0] == "getheatvalue":  
                        if args[2] == "0":
                            hk[temp].get_heating_power(1)
                            hk[temp].get_heating_power(2)
                            #ti.sleep(0.5)
                        else:
                            hk[temp].get_heating_power(int(args[2]))  
            except:
                print("Please input 1~3 for index and 0~2 for port.")
                                     
        elif args[0] == "gettempvalue":
            _args = "index, port"
            
            try:
                if len(args) < 2:
                    show_errmsg(_args)
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "index:int(1~4), port:int(index 1~3:A/B, index 4:1~8, all:0)")
                elif len(args) < 3:
                    show_errmsg(_args)  
                elif (1 <= int(args[1]) <= 4) is not True:    
                    print("Please input 1~4 for index.")
                else:
                    if 1 <= int(args[1]) <= 3:
                        if (args[2] == "A" or args[2] == "B") is not True:
                            print("Please input 'A' or 'B' for port on index 1~3.")
                        else:
                            port = "%d" % (int(args[1]) + 10000)
                            temp = int(args[1])-1
                            if hk[temp] == None:
                                hk[temp] = temp_ctrl(port)
                                
                            if args[2] == "0":
                                hk[temp].get_value("A")
                                hk[temp].get_value("B")
                                #ti.sleep(0.5)
                            else:
                                hk[temp].get_value(args[2])
                                
                    elif args[1] == "4":
                        if (0 <= int(args[2]) <= 8) is not True:
                            print("Please input 0~8 for port on index 4.")
                        else:
                            if hk[TM] == None:
                                hk[TM] = monitor("10004")
                            hk[TM].get_value_fromTM(int(args[2]))
            except:
                print("Please input 'A' or 'B' port for index 1~3 and 0~8 port for index 4.")                                                
                        
        elif args[0] == "getvacuumvalue":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                if hk[VM] == None:
                    hk[VM] = monitor("10005")
                    hk[VM].connect_to_component()
                hk[VM].get_value_fromVM()
                
        elif args[0] == "poweronoff":
            _args = "index, onoff"
            
            try:
                if len(args) < 2:
                    show_errmsg(_args)
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "index:int(1:MACIE 5V, 2:VM 24V, 3:Motor 24V, 4:TH lamp 24V, 5:HC lamp 24V, 0:all), onoff:on/off")
                elif len(args) < 3:
                    show_errmsg(_args)
                elif (0 <= int(args[1]) <= 8) is not True:
                    print("Please input a number 1~8 or 0(all).")
                elif (args[2] == "on" or args[2] == "off") is not True:
                    print("Please input 'on' or 'off'.")
                else:
                    if hk[PDU] == None:
                        hk[PDU] = pdu()
                        
                        hk[PDU].connect_to_component()
                        hk[PDU].initPDU()
                        #ti.sleep(2)
                        
                    if args[1] == "0":
                        for i in range(PDU_IDX):
                            hk[PDU].change_power(i+1, args[2])
                    else:
                        print(args[1], args[2])
                        hk[PDU].change_power(int(args[1]), args[2])
                    #ti.sleep(2)
            except:
                print("Please input a number 1~8 or 0(all) and 'on' or 'off'")
        
        
        elif args[0] == "initmotor":
            _args = "motor"
            
            try:
                if len(args) < 1:
                    show_errmsg(_args)
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "motor:ut/lt")
                elif len(args) < 2:
                    show_errmsg(_args)
                elif (args[1] == MOTOR_UT or args[1] == MOTOR_LT) is not True:
                    show_errmsg(_args)
                else:
                    motornum = -1
                    if args[1] == MOTOR_UT:
                        motornum = UT  
                        port = "10007"
                    elif args[1] == MOTOR_LT:
                        motornum = LT
                        port = "10006" 
                        
                    if hk[motornum] == None:
                        hk[motornum] = motor(args[1], port)
                    
                    hk[motornum].connect_to_component()
                    hk[motornum].init_motor()
            except:
                print("Please input 'ut' or 'lt'.")                   
                    
        elif args[0] == "motormove":
            _args = "motor, posnum"
            
            try:
                if len(args) < 2:
                    show_errmsg(_args)
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "motor:ut/lt, posnum:int(ut:0/1, lt:0-3)")
                elif len(args) < 3:
                    show_errmsg(_args)
                elif (args[1] == MOTOR_UT or args[1] == MOTOR_LT) is not True:
                    show_errmsg(_args)
                elif args[1] == MOTOR_UT and (0 <= int(args[2]) <= 1) is not True:
                    print("Please input a number 0 or 1 for ut.")
                elif args[1] == MOTOR_LT and (0 <= int(args[2]) <= 3) is not True:
                    print("Please input a number 0~3 for lt.")
                else:         
                    if args[1] == MOTOR_UT:
                        motornum = UT  
                    elif args[1] == MOTOR_LT:
                        motornum = LT
                    if hk[motornum] == None:
                        print("Please execute 'initmotor' first!")
                    else:    
                        hk[motornum].move_motor(int(args[2]))
            except:
                print("Please input a number 0 or 1 for ut and 0~3 for lt.")
        
        elif args[0] == "motorgo" or args[0] == "motorback":
            _args = "motor, delta"   
            
            try:
                if len(args) < 2:
                    show_errmsg(_args) 
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "motor:UT/LT, delta:int")   
                elif len(args) < 3:
                    show_errmsg(_args)     
                elif (args[1] == MOTOR_UT or args[1] == MOTOR_LT) is not True:
                    show_errmsg(_args)
                elif int(args[2]) < 1:
                    print("Please input a number over the 0 for delta.")
                else:
                    if args[1] == MOTOR_UT:
                        motornum = UT  
                    elif args[1] == MOTOR_LT:
                        motornum = LT
                        
                    if hk[motornum] == None:
                        print("Please execute 'initmotor' first!")
                    else:
                        go = True    
                        if args[0] == "motorgo":
                            go = True
                        elif args[0] == "motorback":
                            go = False
                        hk[motornum].move_motor_delta(go, int(args[2]))
            except:
                print("Please input a number over the 0 for delta.")
        
        elif args[0] == "setut":
            _args = "posnum"    
            
            try:  
                if len(args) < 2:
                    show_errmsg(_args)
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "posnum:0/1")          
                elif (0 <= int(args[1]) <= 1) is not True:  
                    print("Please input a number 0 or 1 for ut.")
                else:
                    if hk[UT] == None:
                        print("Please execute 'initmotor' first!")
                    else:    
                        hk[UT].setUT(int(args[1]))
            except:
                print("Please input a number 0 or 1 for ut.")
        
        elif args[0] == "setlt":
            _args = "posnum" 
        
            try:    
                if len(args) < 2:
                    show_errmsg(_args)
                elif args[1] == "-h" or args[1] == "--help":
                    show_subfunc(args[0], _args, "posnum:0-3")             
                elif (0 <= int(args[1]) <= 3) is not True:  
                    print("Please input a number 0-3 for lt.")
                else:
                    if hk[UT] == None:
                        print("Please execute 'initmotor' first!")
                    else:
                        hk[UT].setLT(int(args[1]))  
            except:
                print("Please input a number 0-3 for lt.")
                    
                
        elif args[0] == "exit":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                for i in range(COM_CNT):
                    if hk[i]:
                        hk[i].close_component()
                                    
                break
            
        else:
            print("Please confirm command.")
        
        #ti.sleep(0.5)
        args = ""
  

def CliCommand():
    cli.add_command(start)
    cli()


if __name__ == "__main__":
    CliCommand()
    
    
