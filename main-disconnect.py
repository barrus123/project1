import subprocess
import re
import wget
from func_timeout import func_timeout, FunctionTimedOut
import os
import sys
import datetime
import time
def runcommand(command, flag = ''):
    if len(flag) != 0:
        rew = subprocess.run(command, flag, creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    else:
        rew = subprocess.run(command, creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    result = rew.stdout.decode('utf-8')
    return result
def regex_bol(pattern, row):
    matched = re.match(pattern, row)
    is_match = bool(matched)
    return is_match

def currenttime():
    dt = datetime.datetime.now()
    return str(dt).split(".")[0]
def write2log(message):
    f = open(exec_path +"\\log.txt", "a")
    f.write("\n"+currenttime()+":"+message)
    f.close()
def truncate_log():
    open(exec_path +"\\log.txt", 'w').close()
def message_ping_error():
        write2log("ERROR: there was Ping from Google AFTER DISCONNECTION! CHECK YOUR INTERFACES SETTINGS.")
        exit()


def kill_vpn():
    try:
        rew = subprocess.run(['C:\Program Files\Oracle\VirtualBox\VboxManage.exe', 'controlvm', 'vpn', 'poweroff', 'soft'], creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    except:
        kill_vpn()

def make_sure_vpnc_off():
    while True:
       # rew = subprocess.run(['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'vpn'],  creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        #result = rew.stdout.decode('utf-8')
        command = ['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'vpn']
        result = runcommand(command)
        rows = result.splitlines()
        for row in rows:
          #  matched = re.match("^State:(.+)?powered off", row)
           # is_match = bool(matched)
            pattern = "^State:(.+)?powered off"
            is_match = regex_bol(pattern, row)
            if is_match:
                return

def ensure_connect_scripts_killed():
    #rew = subprocess.run(['tasklist'],  creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    #result = rew.stdout.decode('utf-8')
    command = ['tasklist']
    result = runcommand(command)
    rows = result.splitlines()
    for row in rows:
        #matched = re.match("^main\.exe", row)
        #is_match = bool(matched)
        pattern = "^main\.exe"
        is_match = regex_bol(pattern, row)
        if is_match:
            write2log("ERROR: couldn't kill main.exe ")
            exit()
        ##matched = re.match("^VPN-CONNECT\.exe", row)
        ##is_match = bool(matched)
        pattern = "^VPN-CONNECT\.exe"
        is_match = regex_bol(pattern, row)
        if is_match:
                write2log("ERROR: couldn't kill VPN-CONNECT.exe")
                exit()


def check_connect_script_on():
    #rew = subprocess.run(['tasklist'],  creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    #result = rew.stdout.decode('utf-8')
    command = ['tasklist']
    result = runcommand(command)
    rows = result.splitlines()
    for row in rows:
       ## matched = re.match("^main\.exe", row)
        ##is_match = bool(matched)
        pattern = "^main\.exe"
        is_match = regex_bol(pattern, row)
        if is_match:
            process_id = row.split()[1]
            try:
                rew = subprocess.run(['taskkill', '/F', '/PID', process_id],  creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

            except:
                write2log("ERROR: couldn't kill main.exe, try to shut it down manually.")
                exit()
        pattern = "^VPN-CONNECT\.exe"
        is_match = regex_bol(pattern, row)
        if is_match:
            process_id = row.split()[1]
            try:
                rew = subprocess.run(['taskkill', '/F', '/PID', process_id],  creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            except:
                write2log("ERROR: couldn't kill VPN-CONNECT.exe,try to shut it down manually.")
                exit()
    ensure_connect_scripts_killed()

def check_vpn_on():
    ##rew = subprocess.run(['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'vpn'],  creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    ##result = rew.stdout.decode('utf-8')
    command = ['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'vpn']
    result = runcommand(command)
    rows = result.splitlines()
    for row in rows:
        ##matched = re.match("^State:(.+)?running", row)
        ##is_match = bool(matched)
        pattern = "^State:(.+)?running"
        is_match = regex_bol(pattern, row)
        if is_match:
            try:
                func_timeout(30,  kill_vpn)
                func_timeout(30, make_sure_vpnc_off)
            except:
                write2log("ERROR: could not kill VPN container")
                exit()

def verify_no_ping():
    ####### checks if there isn't ping from 8.8.8.8
    #rew = subprocess.run(['ping','8.8.8.8'],  creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    #result = rew.stdout.decode('utf-8')
    command = ['ping','8.8.8.8']
    result = runcommand(command)
    ##print(result)
    num_of_request_timed_out = result.count("Request timed out")
    num_of_unreachable = result.count("Destination host unreachable")
    ##print(num_of_request_timed_out + num_of_unreachable)
    if num_of_request_timed_out + num_of_unreachable != 4:
        message_ping_error()


def main():
    check_connect_script_on()
    truncate_log()
    write2log("VPN Connecting Scripts are off")
    check_vpn_on()
    write2log("VPN Container is down")
    write2log("Verifying disconnection with Ping Test")
    verify_no_ping()
    write2log("Disconnection completed")
if __name__ == "__main__":
            DETACHED_PROCESS = 0x00000008
            exec_path = os.path.abspath(os.path.dirname(sys.argv[0])).split("\\main-disconnect")[0]
            main()