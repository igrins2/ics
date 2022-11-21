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

import os, sys
import click
                
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.temp_ctrl import *
from HKP.monitor import *
from HKP.pdu import *
from HKP.motor import *
from HKP.uploader import *

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
            "  showcommand show\n"  
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
            "------------------------------------------\n")
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
    
    cnt = 0
        
    iam = "cli"
    print( '================================================\n'+
           '                Ctrl + C to exit or type: exit  \n'+
           '================================================\n')

    show = True
    args = show_func(show)
    
    hk = [None for _ in range(COM_CNT)]
        
    while(True):
        if len(args) == 0:
            args = show_func(show)
            continue
        
        #print(str(args))

        if args[0] == "showcommand":
            _args = "show"
            if args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "show: True/False")
            elif args[1] == "False":
                show = False
            elif args[1] == "True":
                show = True
            else:
                show_errmsg(_args)

                
        elif args[0] == "getsetpoint" or args[0] == "getheatvalue":
            _args = "index, port"
            
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
                    else:
                        print(cnt)
                        hk[temp].get_setpoint(int(args[2]))
                elif args[0] == "getheatvalue":  
                    if args[2] == "0":
                        hk[temp].get_heating_power(1)
                        hk[temp].get_heating_power(2)
                    else:
                        hk[temp].get_heating_power(int(args[2]))  
                        
                        
        elif args[0] == "gettempvalue":
            _args = "index, port"
            if len(args) < 3:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "index:int(1~4), port:int(index 1~3:A/B, index 4:1~8, all:0)")
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
                            hk[temp] = temp_ctrl(port, False)
                            
                        if args[2] == "0":
                            hk[temp].get_value("A")
                            hk[temp].get_value("B")
                        else:
                            hk[temp].get_value(args[2])
                            
                elif args[1] == "4":
                    if (0 <= int(args[2]) <= 8) is not True:
                        print("Please input 0~8 for port on index 4.")
                    else:
                        if hk[TM] == None:
                            hk[TM] = monitor("temp", "10004")
                        hk[TM].get_value(int(args[2]))
                                                                
                        
        elif args[0] == "getvacuumvalue":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                if hk[VM] == None:
                    hk[VM] = monitor("vm", "10005")
                    hk[VM].connect_to_component()
                hk[VM].get_value()
                     
                
        elif args[0] == "poweronoff":
            _args = "index, onoff"
            if len(args) < 3:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "index:int(1:MACIE 5V, 2:VM 24V, 3:Motor 24V, 4:TH lamp 24V, 5:HC lamp 24V, 0:all), onoff:on/off")
            elif (0 <= int(args[1]) <= 8) is not True:
                print("Please input a number 1~8 or 0(all).")
            elif (args[2] == "on" or args[2] == "off") is not True:
                print("Please input a 'on' or 'off'.")
            else:
                if hk[PDU] == None:
                    hk[PDU] = pdu("50023")
                    
                    hk[PDU].connect_to_component()
                    hk[PDU].initPDU()
                    
                if args[1] == "0":
                    for i in range(PDU_IDX):
                        hk[PDU].change_power(i+1, args[2])
                else:
                    hk[PDU].change_power(int(args[1]), args[2])
        
        
        elif args[0] == "initmotor":
            _args = "motor"
            if len(args) < 2:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "motor:UT/LT")
            elif (args[1] == "UT" or args[1] == "LT") is not True:
                show_errmsg(_args)
            else:
                motornum = -1
                if args[1] == "UT":
                    motornum = UT  
                elif args[1] == "LT":
                    motornum = LT 
                    
                if hk[motornum] == None:
                    hk[motornum] = motor(args[1])
                hk[motornum].init_motor()
                                             
                    
        elif args[0] == "motormove":
            _args = "motor, posnum"
            if len(args) < 3:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "motor:UT/LT, posnum:int(UT:0/1, LT:0-3)")
            elif (args[1] == "UT" or args[1] == "LT") is not True:
                show_errmsg(_args)
            elif args[1] == "UT" and (0 <= int(args[2]) <= 1) is not True:
                print("Please input a number 0 or 1 for UT.")
            elif args[1] == "LT" and (0 <= int(args[2]) <= 3) is not True:
                print("Please input a number 0~3 for LT.")
            else:
                motornum = -1
                if args[1] == "UT":
                    motornum = UT  
                elif args[1] == "LT":
                    motornum = LT
                    
                if hk[motornum] == None:
                    hk[motornum] = motor(args[1])
                    
                hk[motornum].move_motor(int(args[2]))
        
        
        elif args[0] == "motorgo" or args[0] == "motorback":
            _args = "motor, delta"   
            if len(args) < 3:
                show_errmsg(_args) 
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "motor:UT/LT, delta:int")        
            elif (args[1] == "UT" or args[1] == "LT") is not True:
                show_errmsg(_args)
            elif int(args[2]) < 1:
                print("Please input a number over the 0 for delta.")
            else:
                motornum = -1
                if args[1] == "UT":
                    motornum = UT  
                elif args[1] == "LT":
                    motornum = LT
                
                if hk[motornum] == None:
                    hk[motornum] = motor(args[1])
                    
                go = True    
                if args[0] == "motorgo":
                    go = True
                elif args[0] == "motorback":
                    go = False
                                        
                hk[motornum].move_motor_delta(go, int(args[2]))
        
        
        elif args[0] == "setut":
            _args = "posnum"      
            if len(args) < 2:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "posnum:0/1")          
            elif (0 <= int(args[1]) <= 1) is not True:  
                print("Please input a number 0 or 1 for UT.")
            else:
                if hk[UT] == None:
                    hk[UT] = motor(args[1])
                    
                hk[UT].setUT(int(args[1]))
        
        
        elif args[0] == "setlt":
            _args = "posnum"     
            if len(args) < 2:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "posnum:0-3")             
            elif (0 <= int(args[1]) <= 3) is not True:  
                print("Please input a number 0-3 for LT.")
            else:
                if hk[UT] == None:
                    hk[UT] = motor(args[1])
                    
                hk[UT].setLT(int(args[1]))  
                    
                
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
        
        #ti.sleep(1)
        cnt += 1
        print()
        args = show_func(show)
  

def CliCommand():
    cli.add_command(start)
    cli()


if __name__ == "__main__":
    CliCommand()

