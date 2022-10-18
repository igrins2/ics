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


def show_func(show):
    if show:
        print("------------------------------------------\n"
            "Usage: Command [Options] [Args]...\n\n"
            "Options:\n"
            "  -h, --help  Show this message and exit.\n\n"
            "Command:\n"
            "  showcommand show\n"  
            "  getsetpoint\n" 
            "  getheatvalue\n"
            "  getvalue\n"
            "  initPDU\n"    
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


def show_checkmsg(pkg):
    pkg.logwrite(BOTH, "Please check the interface status!!!")
    

def show_noargs(cmd):
    msg = "'%s' has no arguments. Please use just command." % cmd
    print(msg)


@click.command(help=CLASS_NAME + " Start")
def start():
    hk = HK()  
    for i in range(COM_CNT):
        hk.connect_to_component(i)

    hk.logwrite(CMDLINE, 
           '================================================\n'+
           '                                Ctrl + C to exit\n'+
           '================================================\n')

    show = True
    args = show_func(show)
    PDU_sts = False
    motor_sts = [False, False]  #LT, UT
    
    while(True):
        if len(args) == 0:
            args = show_func(show)
            continue
        
        hk.logwrite(CMDLINE, str(args))

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

                
        elif args[0] == "getsetpoint":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                res = []
                res.append(hk.get_setpoint_fromTMC(TMC1, 1))   # bench set point
                res.append(hk.get_setpoint_fromTMC(TMC1, 2))  # Grating set point
                res.append(hk.get_setpoint_fromTMC(TMC2, 1))  # SVC set point
                res.append(hk.get_setpoint_fromTMC(TMC2, 2))  # Detector K set point
                res.append(hk.get_setpoint_fromTMC(TMC3, 2))  # Detector H set point
                
                for i in range(len(res)):
                    if res[i] == None:
                        show_checkmsg(hk)
                        break
                
                
        elif args[0] == "getheatvalue":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                res = []
                res.append(hk.get_heating_power(TMC1, 1))  # bench heating
                res.append(hk.get_heating_power(TMC1, 2))  # Grating heating
                res.append(hk.get_heating_power(TMC2, 1))  # SVC heating
                res.append(hk.get_heating_power(TMC2, 2))  # Detector K heating
                res.append(hk.get_heating_power(TMC3, 2))  # Detector H heating

                for i in range(len(res)):
                    if res[i] == None:
                        show_checkmsg(hk)
                        break
                    
                    
        elif args[0] == "getvalue":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                res = []
                res.append(hk.get_value_fromTMC(TMC1, "A"))  # bench monitoring
                res.append(hk.get_value_fromTMC(TMC1, "B"))  # Grating monitoring
                res.append(hk.get_value_fromTMC(TMC2, "A"))  # SVC monitoring
                res.append(hk.get_value_fromTMC(TMC2, "B"))  # Detector K monitoring
                res.append(hk.get_value_fromTMC(TMC3, "A"))  # Camera H monitoring
                res.append(hk.get_value_fromTMC(TMC3, "B"))  # Detector H monitoring

                res.append(hk.get_value_fromTM(0))
                
                res.append(hk.get_value_fromVM())
            
                for i in range(len(res)):
                    if res[i] == None:
                        show_checkmsg(hk)
                        break
                    
                    
        elif args[0] == "initPDU":
            if PDU_sts == True:
                print("PDU already has been initialized.")
                args = []
                continue
            
            if len(args) > 1:
                show_noargs(args[0])
            elif hk.initPDU() == False:
                show_checkmsg(hk)
                PDU_sts = False
            else:
                PDU_sts = True
                
                
        elif args[0] == "poweronoff":
            _args = "index onoff"
            if len(args) < 3:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "index: int (1:MACIE 5V, 2:VM 24V, 3:Motor 24V, 4:TH lamp 24V, 5:HC lamp 24V, 0:all), onoff:on/off")
            elif (0 <= int(args[1]) <= 8) is not True:
                print("Please input a number 1~8 or 0(all).")
            elif (args[2] == "on" or args[2] == "off") is not True:
                print("Please input a 'on' or 'off'.")
            else:
                if int(args[1]) == 0:
                    for i in range(PDU_IDX):
                        if hk.change_power(i+1, args[2]) == False:
                            show_checkmsg(hk)
                            break
                else:
                    if hk.change_power(int(args[1]), args[2]) == False:
                        show_checkmsg(hk)                        
        
        
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
                if args[1] == "LT":
                    motornum = MOTOR_LT
                elif args[1] == "UT":
                    motornum = MOTOR_UT
                    
                if motor_sts[motornum] == True:
                    msg = "Motor (%s) already has been initialized." % args[1]
                    print(msg)
                elif hk.init_motor(motornum) == False:
                    show_checkmsg(hk)
                    motor_sts[motornum] = False
                else:
                    motor_sts[motornum] = True
                    
                    
        elif args[0] == "motormove":
            _args = "motor posnum"
            if len(args) < 3:
                show_errmsg(_args)
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "motor:UT/LT, posnum:int(UT:0/1, LT:0-3)")
            elif (args[1] == "UT" or args[1] == "LT") is not True:
                show_errmsg(_args)
            elif args[1] == "UT" and (0 <= int(args[2]) <= 1) is not True:
                print("Please input a number 0 or 1 for UT.")
            elif args[1] == "LT" and (0 <= int(args[2]) <= 3) is not True:
                print("Please input a number 0~3 for UT.")
            else:
                motornum = -1
                if args[1] == "LT":
                    motornum = MOTOR_LT
                elif args[1] == "UT":
                    motornum = MOTOR_UT
                    
                if motor_sts[motornum] == False:   
                    msg = "Please initialize Motor (%s)." % args[1]
                    print(msg)
                elif hk.move_motor(motornum, int(args[2])) == False:
                    show_checkmsg(hk)
                    motor_sts[motornum] = False
        
        
        elif args[0] == "motorgo" or args[0] == "motorback":
            _args = "motor delta"    
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
                if args[1] == "LT":
                    motornum = MOTOR_LT
                elif args[1] == "UT":
                    motornum = MOTOR_UT
                    
                if motor_sts[motornum] == False:   
                    msg = "Please initialize Motor (%s)." % args[1]
                    print(msg)
                else:
                    if args[0] == "motorgo":
                        go = True
                    elif args[1] == "motorback":
                        go = False
                                        
                    if hk.move_motor_delta(motornum, go, int(args[2])) == False:
                        show_checkmsg(hk)
                        motor_sts[motornum] = False
        
        
        elif args[0] == "setut":
            _args = "posnum"      
            if len(args) < 2:
                show_errmsg(_args)       
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "posnum:0/1")   
            elif (0 <= int(args[1]) <= 1) is not True:  
                print("Please input a number 0 or 1 for UT.")
            elif hk.setUT(int(args[1])) == False:
                show_checkmsg(hk)
                motor_sts[MOTOR_UT] = False
        
        
        elif args[0] == "setlt":
            _args = "posnum"     
            if len(args) < 2:
                show_errmsg(_args)          
            elif args[1] == "-h" or args[1] == "--help":
                show_subfunc(args[0], _args, "posnum:0-3")   
            elif (0 <= int(args[1]) <= 3) is not True:  
                print("Please input a number 0-3 for LT.")
            elif hk.setLT(int(args[1])) == False:
                show_checkmsg(hk)
                motor_sts[MOTOR_LT] = False      
                    
                
        elif args[0] == "exit":
            if len(args) > 1:
                show_noargs(args[0])
            else:
                for i in range(COM_CNT):
                    if hk.comStatus[i]:
                        hk.close_component(i)
                break
            
        else:
            hk.logwrite(CMDLINE, "Please confirm command.")
        
        print()
        args = show_func(show)
  

def CliCommand():
    cli.add_command(start)
    cli()


if __name__ == "__main__":
    CliCommand()

