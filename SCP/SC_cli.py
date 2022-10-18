# -*- coding: utf-8 -*-
"""
Created on Jan 27, 2022

Modified on Jun 28, 2022

@author: hilee

1. cli
2. unit test
3. communicate with components: multi thread, Async, non-blocking
4. communicate with other packages: DTP, GMP, ICS
5. GUI

"""

import click

from SCP.SC_core import *

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
            "  connecttoserver (be getting ready)\n"  
            "  getTCSinfo\n" 
            "  initialize\n"
            "  sendtoGMP status\n"
            "  setFSmode mode\n"
            "  setrampparam p1 p2 p3 p4 p5\n"
            "  setfsparam p1 p2 p3 p4 p5\n"
            "  acquireramp\n"   
            "  stopacquisition\n"
            "  closesocket\n"    
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
    sc = SC()



def CliCommand():
    cli.add_command(start)    
    cli()


if __name__ == "__main__":
    CliCommand()

