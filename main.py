import subprocess
import re
import wget
from func_timeout import func_timeout, FunctionTimedOut
import os
import sys
import datetime
import time
def currenttime():
    dt = datetime.datetime.now()
    return str(dt).split(".")[0]
def write2log(message):
    f = open(exec_path +"\\log.txt", "a")
    f.write("\n"+currenttime()+":"+message)
    f.close()
def truncate_log():
    open(exec_path +"\\log.txt", 'w').close()

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

def message_geo_location(country_name):
    write2log("You are Surfing from " + country_name )
def message_no_geo_location():
    write2log("ERROR: couldn't determine Geo Location, this may result from BAD CONNECTIVITY")
def message_ping_error():
    write2log("ERROR: there was Ping from Google CHECK YOUR INTERFACES SETTINGS.")
    sys.exit()
def message_vpn_on():
    write2log("ERROR: the VPN is powered on please disconnect first and try again")
    sys.exit()
def  message_vpn_noopen():
    write2log("ERROR: the VPN process couldn't open")
    sys.exit()
def check_disconnecting():
    #rew = subprocess.run(['tasklist'], creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    #result = rew.stdout.decode('utf-8')
    command = ['tasklist']
    result = runcommand(command)
    rows = result.splitlines()
    for row in rows:
        ##matched = re.match("^main-disconnect\.exe", row)
        ##is_match = bool(matched)
        pattern = "^main-disconnect\.exe"
        is_match = regex_bol(pattern, row)
        if is_match:
            write2log("ERROR: The system is currently disconnecting, please wait for it to finish and then try to reconnect again.")
            sys.exit()

def check_no_vpn():
    ##rew = subprocess.run(['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'vpn'],creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    ##result = rew.stdout.decode('utf-8')
    command = ['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'vpn']
    result = runcommand(command)
    rows = result.splitlines()
    for row in rows:
        ##matched = re.match("^State:(.+)?powered off", row)
        ##is_match = bool(matched)
        pattern = "^State:(.+)?powered off"
        is_match = regex_bol(pattern, row)
        if is_match:
            return
    message_vpn_on()
def is_in_config(interface_name):
    rew = subprocess.run(['ipconfig', '/all'], creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    result = str(rew.stdout)
    ##count = result.count(interface_name)
    ##print(result)
    ##matched = re.match("(.+)?Description.+: " + interface_name, result)
    ##is_match = bool(matched)
    pattern = "(.+)?Description.+: " + interface_name
    is_match = regex_bol(pattern, result)
    return is_match

def check_vpn_interface_config():
    #rew = subprocess.run(['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'vpn'],creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    #result = rew.stdout.decode('utf-8')
    command = ['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','showvminfo', 'Core']
    result = runcommand(command)
    rows = result.splitlines()
    counter = 0
    host_only = False
    bridge = False
    for row in rows:
        ##matched = re.match("^NIC [0-9]:.+disabled", row)
        ##is_match = bool(matched)
        pattern ="^NIC [0-9]:.+disabled"
        is_match = regex_bol(pattern, row)
        if is_match:
            counter = counter + 1
            continue
        ##matched1 = re.match("^NIC [0-9]:.+MAC", row)
        ##is_match1 = bool(matched1)
        pattern ="^NIC [0-9]:.+MAC"
        is_match1 = regex_bol(pattern, row)
        if is_match1:
            ##print(row)
            try:
                interface_name = row.split(",")[1].split("'")[1]
                print(interface_name)
                if interface_name == "VirtualBox Host-Only Ethernet Adapter":
                    host_only = True
                    continue
               # matched2 = re.match("(.+)?Attachment: Bridged Interface", row)
                #is_match2 = bool(matched2)
                pattern ="(.+)?Attachment: Bridged Interface"
                is_match2 = regex_bol(pattern, row)
                ##print(str(is_match2))
                if is_match2:
                    ##print(row)
                    bridge = is_in_config(interface_name)
            except:
                write2log("ERROR: Vpn Interfaces Configuration is invalid")
                sys.exit()

    ##print("counter: " + str(counter) +"hostonly is:" + str(host_only) + "bridge is: " + str(bridge))
    if not (counter == 6 and host_only and bridge):
        write2log("ERROR: Vpn Interfaces Configuration is invalid")
        sys.exit()

def check_ping():
    ####### checks if there isn't ping from 8.8.8.8
    ##rew = subprocess.run(['ping','8.8.8.8'],creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    ##result = rew.stdout.decode('utf-8')
    ##print(result)
    command = ['ping','8.8.8.8']
    result = runcommand(command)
    num_of_request_timed_out = result.count("Request timed out")
    num_of_unreachable = result.count("Destination host unreachable")
    ##print(num_of_request_timed_out + num_of_unreachable)
    if num_of_request_timed_out + num_of_unreachable != 4:
        message_ping_error()

def check_hostonly_config(result):
    ########## makes sure that there is an Host-Only Adapter and it's configured properly
    is_hostonly = result.count("Ethernet adapter VirtualBox Host-Only Network:")
    #print(is_hostonly)
    if is_hostonly != 1:
        write2log("ERROR: Host-Only Adapter Configuration is Invalid, Either there is more than one or there is NONE.")
        sys.exit()
    rows_result = result.splitlines()
    num_of_row_hostonly = rows_result.index("Ethernet adapter VirtualBox Host-Only Network:")
    rows_hostonly = []
    for i in range(num_of_row_hostonly + 1, len(rows_result)):
        #matched = re.match(".+:$", rows_result[i])
       # is_match = bool(matched)
        pattern =".+:$"
        is_match = regex_bol(pattern, rows_result[i])
        if not is_match:
            rows_hostonly.append(rows_result[i])
        else:
            break
    #print(rows_hostonly)
    ############################ checks the configuration itself
    is_ip = False
    is_gateway = False
    for row in rows_hostonly:
        #print(row)
        #print(row.count("IPv4 Address"))
        if row.count("IPv4 Address") == 1:
            ip_address = row.split(":")[1]
            #print(ip_address)
            if ip_address != " 192.168.56.1":
                write2log("ERROR: Host-Only Adapter Configuration is Invalid, check Host IP.")
                break
            #print("gray")
            is_ip = True
        if row.count("Default Gateway") == 1:
            default_gateway = row.split(":")[1]
            if default_gateway != " 192.168.56.101":
                write2log("ERROR: Host-Only Adapter Configuration is Invalid, check Default Gateway.")
                break
            is_gateway = True
            #print("yey")

    if is_gateway and is_ip:
        write2log("Host-Only Configuration validated")
    else:
        write2log("ERROR: Host-Only Adapter Configuration is Invalid")
        sys.exit()


def check_other_interfaces(result):
    rows_result = result.splitlines()
    counter_ip = 0
    counter_gateway = 0
    for row in rows_result:
       # matched = re.match("(.+)?IPv4 Address.+: (([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])", row)
        #is_match = bool(matched)
        pattern ="(.+)?IPv4 Address.+: (([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])"
        is_match = regex_bol(pattern, row)
        if is_match:
            counter_ip = counter_ip + 1
        #matched = re.match("(.+)?Default Gateway.+: (([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])", row)
        #is_match = bool(matched)
        pattern ="(.+)?Default Gateway.+: (([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])"
        is_match = regex_bol(pattern, row)
        ##print("default",row,is_match)
        if is_match:
            counter_gateway = counter_gateway + 1
        if counter_gateway > 1 or counter_ip >1:
            write2log("ERROR: Interfaces configuration is invalid: some adapters, NOT THE HOST-ONLY, have an ip address or default Gateway!")
            sys.exit()

def  check_interfaces_configuration():
    #rew = subprocess.run(['ipconfig'],creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    #result = rew.stdout.decode('utf-8')
    command = ['ipconfig']
    result = runcommand(command)
    check_hostonly_config(result)
    check_other_interfaces(result)

def message_interfaces_successs():
    write2log("Interfaces configuration is authorized.")

def message_route_error():
    write2log("ERROR: Routes aren't configured properly")
    sys.exit()

def message_routes_successs():
    write2log("The routes are authorized")

def check_default_route():
    hostonly_default = False
    other_default = False
    ##rew = subprocess.run(['route', 'print'],creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    ##result = rew.stdout.decode('utf-8')
    command = ['route', 'print']
    result = runcommand(command)
    rows = result.splitlines()
    for row in rows:
       # matched = re.match("(.+)?0\.0\.0\.0(.+)?0\.0\.0\.0(.+)?(([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])(.+)?(([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])", row)
        #is_match = bool(matched)
        pattern ="(.+)?0\.0\.0\.0(.+)?0\.0\.0\.0(.+)?(([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])(.+)?(([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])\.){3}([0-9][]0-9][0-9]|[0-9][0-9]|[0-9])"
        is_match = regex_bol(pattern, row)
        ##print("other",row,is_match)
        if is_match:
          ##  matched1 = re.match("(.+)?0\.0\.0\.0(.+)?0\.0\.0\.0(.+)?192\.168\.56\.101(.+)?192\.168\.56\.1", row)
            ##is_match1 = bool(matched1)
            pattern ="(.+)?0\.0\.0\.0(.+)?0\.0\.0\.0(.+)?192\.168\.56\.101(.+)?192\.168\.56\.1"
            is_match1 = regex_bol(pattern, row)
            if is_match1:
                hostonly_default = True
                continue
            other_default = True
    if hostonly_default and not other_default:
        return
    else:
        message_route_error()
def connect_2vpn():
    ##rew = subprocess.run(['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','startvm', 'vpn', '--type', 'headless'], creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    ##result = rew.stdout.decode('utf-8')
    command = ['C:\Program Files\Oracle\VirtualBox\VboxManage.exe','startvm', 'vpn', '--type', 'headless']
    result = runcommand(command)
    is_powered = result.count("has been successfully started")
    if is_powered != 1:
        message_vpn_noopen()
    write2log("the VPN is powered on and will be soon connecting....")
def wait_for_connection():
    num_replies = 0
    while num_replies < 3:
        num_replies = 0
        ##rew = subprocess.run(['ping', '8.8.8.8'], creationflags=DETACHED_PROCESS, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        ##result = rew.stdout.decode('utf-8')
        command = ['ping', '8.8.8.8']
        result = runcommand(command)
        ##print(result)
        rows = result.splitlines()
        for row in rows:
            ##match = re.match("Reply from 8\.8\.8\.8: bytes=32 time.+[0-9]+ms", row)
            ##is_match = bool(match)
            pattern ="Reply from 8\.8\.8\.8: bytes=32 time.+[0-9]+ms"
            is_match = regex_bol(pattern, row)
            if is_match:
                num_replies = num_replies + 1
def message_vpn_not_connect():
    write2log("vpn couldn't connect....")
    sys.exit()
def message_is_ping():
    write2log("There is ping from google after connection")

def find_country_name(country_code):
    country_code_file = exec_path + '\\inc\\country_codes.txt'
    with open(country_code_file, 'r') as file:
        data = file.read()
        rows = data.splitlines()
        for row in rows:
            ##match = re.match("^"+country_code+",", row)
            ##is_match = bool(match)
            pattern ="^"+country_code+","
            is_match = regex_bol(pattern, row)
            if is_match:
                country_name = row.split('"')[1]
                return country_name




def find_geo_location():
    country_name = ""
    url = 'http://www.wtfismyip.com/json'
    try:
     subprocess.run(['del', exec_path + '\\json'], creationflags=DETACHED_PROCESS,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    except:
        pass
    while len(country_name) == 0:
        try:
            filename = wget.download(url)
        except:
            time.sleep(5)
            continue
        with open('json', 'r') as file:
            data = file.read()
            #print(data)
            rows = data.splitlines()
            country_code = rows[6].split(":")[1].split('"')[1]
            ##print(country_code)
            country_name = find_country_name(country_code)
    return country_name

def main():
    check_disconnecting()
    truncate_log()
    write2log("Beginning intial checks on the System Configuration.")
    check_no_vpn()
    check_vpn_interface_config()
    check_ping()
    check_interfaces_configuration()
    message_interfaces_successs()
    check_default_route()
    message_routes_successs()
    connect_2vpn()
    try:
        func_timeout(180, wait_for_connection)
    except:
        message_vpn_not_connect()
        sys.exit()
    message_is_ping()
    try:
        country_name = func_timeout(30, find_geo_location)
        message_geo_location(country_name)
    except:
        message_no_geo_location()
if __name__ == "__main__":
            DETACHED_PROCESS = 0x00000008
            exec_path = os.path.abspath(os.path.dirname(sys.argv[0])).split("\\main")[0]
            main()