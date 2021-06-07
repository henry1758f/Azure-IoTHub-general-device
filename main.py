################################################
# SYNNEX International Technology Corp.
# General Device Monitor with Azure IoT Hub
# henryhuang@synnex-grp.com
################################################
import psutil
import asyncio
import platform
import json
import os
import sys
import csv

#for IP Address obtain
import socket
import requests
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import constant, Message, MethodResponse

## for DPS Testing
model_id = "dtmi:ASUS:TinkerEdgeR;1"
# For Multiple components
import pnp_helper
windows_device_info_component_name = "WindowsDeviceInfo1"
linux_device_info_component_name = "LinuxDeviceInfo1"
lpr_device_info_component_name = "LprDetectCam1"
#================#
global period
period = 5

global lpr_period
lpr_period = 2
info_dump = True
debug_dump = False

def info_dumper(msg):   # information for user
    if info_dump:
        print('[INFO] ' + msg)

def debug_dumper(msg):  # information for debug
    if debug_dump:
        print('[DEBUG] ' + msg)

def end_listener():
    if os.getenv("KEYPAD_INTERRUPT") == "ENABLE":
        while True:
            selection = input("Press Q to quit\n")
            if selection == "Q" or selection == "q":
                print("Quitting...")
                break
    else :
        print('[DEBUG] Telemetry will send forever.')
        import time
        while True:
            time.sleep(1)
            sys.stdout.flush()


async def property_update(device_client,os_type,machine):
    print("[DEBUG] Update System Message")
    # get IP Address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipLocal = s.getsockname()[0]
    s.close()
    ipPublic = requests.get('http://ifconfig.me/ip', timeout=1).text.strip()
    #


    global root_path
    if os_type == "Windows":
        root_path = 'C:/'
        hostname_str = platform.node()
        cpuInfo = ' '.join(os.popen('wmic cpu get name').read().splitlines()[2].split() )
        cpuCores = psutil.cpu_count()
        biosManufacturer = ' '.join(os.popen('wmic bios get Manufacturer').read().splitlines()[2].split() )
        biosVersion = ''.join(os.popen('wmic bios get Version').read().splitlines()[2].split() )
        baseboardManufacturer = ''.join(os.popen('wmic baseboard get Manufacturer').read().splitlines()[2].split() )
        baseboardSerialNumber = ''.join(os.popen('wmic baseboard get SerialNumber').read().splitlines()[2].split() )
        baseboardProduct = ''.join(os.popen('wmic baseboard get Product').read().splitlines()[2].split() )
        osVersion = ''.join(os.popen('wmic os get Version').read().splitlines()[2].split() )
        osBuildNumber = ''.join(os.popen('wmic os get BuildNumber').read().splitlines()[2].split() )

    elif os_type == "Linux":
        root_path = '/'
        hostname_str = platform.node()
        osVersion = ' '.join(os.popen('hostnamectl |grep "Operating System"').read().split(':')[1].split() )
        osBuildNumber = ' '.join(os.popen('hostnamectl |grep "Kernel"').read().split(':')[1].split() )
        if "x86" in machine:
            cpuInfo = ' '.join(os.popen('lscpu |grep "Model name"').read().split(':')[1].split() )
            biosManufacturer = ' '.join(os.popen('cat /sys/class/dmi/id/bios_vendor').read().split() )
            biosVersion = ' '.join(os.popen('cat /sys/class/dmi/id/bios_version').read().split() )
            baseboardManufacturer = ' '.join(os.popen('cat /sys/class/dmi/id/board_vendor').read().split() )
            baseboardSerialNumber = ' '.join(os.popen('sudo cat /sys/class/dmi/id/board_serial').read().split() )
            baseboardProduct = ' '.join(os.popen('cat /sys/class/dmi/id/board_name').read().split() )
            # Linux Only
            highTemp = psutil.sensors_temperatures()['coretemp'][0][2]
            criticalTemp = psutil.sensors_temperatures()['coretemp'][0][3]
        else :
            biosManufacturer = 'N/A'
            biosVersion = 'N/A'
            baseboardManufacturer = 'N/A'
            baseboardSerialNumber = 'N/A'
            baseboardProduct = 'N/A'
            try:
                cpuInfo = ' '.join(os.popen('lscpu |grep "Model name"').read().split(':')[1].split() )
            except:
                cpuInfo = machine
            try:
                highTemp = psutil.sensors_temperatures()['soc-thermal'][0][2]
                criticalTemp = psutil.sensors_temperatures()['soc-thermal'][0][3]
            except:
                highTemp = 0
                criticalTemp = 0    

    cpuCores = psutil.cpu_count()
    cpuMaxfreq = psutil.cpu_freq().max
    logicalDISKtotal = psutil.disk_usage(root_path).total
    memTotal = psutil.virtual_memory().total

    # Print Property result
    print('============================')
    print('Property List Upodate >>>>>>')
    print("OS type : {os}".format(os=os_type))
    print("OS Version : {osV}".format(osV=osVersion))
    print("OS Build/Kernel : {osK}".format(osK=osBuildNumber))
    print("Hostname : {host}".format(host=hostname_str))
    print("CPU Info : {cpu}".format(cpu=cpuInfo))
    print("CPU Core Count : {cpus}".format(cpus=cpuCores))
    print("CPU Max Frequency : {cpuMF}".format(cpuMF=cpuMaxfreq))
    if os_type == "Linux":
        print("> CPU High Temp : {cpu_ht} Ce".format(cpu_ht=highTemp))
        print("> CPU Critical : {cpu_ct} Ce".format(cpu_ct=criticalTemp))
    print("BIOS Manufature : {biosM}".format(biosM=biosManufacturer))
    print("BIOS Version : {biosV}".format(biosV=biosVersion))
    print("Board Manufature : {boardM}".format(boardM=baseboardManufacturer))
    print("Board Product : {boardP}".format(boardP=baseboardProduct))
    print("Board SerialNumber : {boardSN}".format(boardSN=baseboardSerialNumber))
    print("System DISK size : {diskSZ}".format(diskSZ=logicalDISKtotal))
    print("Memory size : {memSZ}".format(memSZ=memTotal))
    print("Local IP Address : {ip}".format(ip=ipLocal))
    print("Public IP Address : {ip}".format(ip=ipPublic))

    # For Multiple components
    if os_type == "Windows":
        properties_device_info = pnp_helper.create_reported_properties(
            windows_device_info_component_name,
            hostname=hostname_str,
            cpuInfo=cpuInfo,
            cpuCores=cpuCores,
            cpuMaxfreq=cpuMaxfreq,
            biosManufacturer=biosManufacturer,
            biosVersion=biosVersion,
            baseboardManufacturer=baseboardManufacturer,
            baseboardSerialNumber=baseboardSerialNumber,
            baseboardProduct=baseboardProduct,
            osVersion=osVersion,
            osBuildNumber=osBuildNumber,
            memTotal=memTotal,
            logicalDISKtotal=logicalDISKtotal,
            ipLocal=ipLocal,
            ipPublic=ipPublic,
        )
    elif os_type == "Linux":
        properties_device_info = pnp_helper.create_reported_properties(
            linux_device_info_component_name,
            hostname=hostname_str,
            cpuInfo=cpuInfo,
            cpuCores=cpuCores,
            cpuMaxfreq=cpuMaxfreq,
            biosManufacturer=biosManufacturer,
            biosVersion=biosVersion,
            baseboardManufacturer=baseboardManufacturer,
            baseboardSerialNumber=baseboardSerialNumber,
            baseboardProduct=baseboardProduct,
            osVersion=osVersion,
            osBuildNumber=osBuildNumber,
            memTotal=memTotal,
            logicalDISKtotal=logicalDISKtotal,
            ipLocal=ipLocal,
            ipPublic=ipPublic,
            highTemp=highTemp,
            criticalTemp=criticalTemp,
        )
    global property_updates
    property_updates = asyncio.gather(
        device_client.patch_twin_reported_properties(properties_device_info),
    )

async def telemetery_update(device_client,os_type,machine):
    print('[DEBUG] Start sending telemetry every {sec} Second(s).'.format(sec=period))
    while True:
        cpuLoading = psutil.cpu_percent()
        cpuClock =  psutil.cpu_freq().current
        mem_free = psutil.virtual_memory().free
        mem_usg = psutil.virtual_memory().percent
        logicalDISKfree = psutil.disk_usage(root_path).free
        logicalDISKpercent = psutil.disk_usage(root_path).percent
        if os_type == "Linux":
            if 'x86' in machine:
                currentTemp = psutil.sensors_temperatures()['coretemp'][0][1]
            else:
                currentTemp = psutil.sensors_temperatures()['soc-thermal'][0][1]
                currentTempGPU = psutil.sensors_temperatures()['gpu-thermal'][0][1]
        
        json_msg = {}
        json_msg["cpuLoading"]=cpuLoading
        json_msg["cpuClock"]=cpuClock
        json_msg["memFree"]=mem_free
        json_msg["memUsage"]=mem_usg
        json_msg["logicalDISKfree"]=logicalDISKfree
        json_msg["logicalDISKusage"]=logicalDISKpercent
        if os_type == "Linux":
            json_msg["currentTemp"]=currentTemp

        print('[DEBUG] Sending Telemetry :{m}'.format(m=json_msg))
        # For Multiple components
        if os_type == "Windows":
            await send_telemetry_with_component_name(device_client, json_msg, windows_device_info_component_name)
        elif os_type == "Linux":
            await send_telemetry_with_component_name(device_client, json_msg, linux_device_info_component_name)
            if not 'x86' in machine:
                json_msg_gpu = {}
                json_msg_gpu["currentTempGPU"]=currentTempGPU
                print('[DEBUG] Sending Telemetry :{m}'.format(m=json_msg_gpu))
                await send_telemetry_with_component_name(device_client,json_msg_gpu)
        await asyncio.sleep(period)

async def lpr_update(device_client):
    info_dumper('Start Checking License Plate every {sec} Second(s).'.format(sec=lpr_period))
    import rfc3339
    from datetime import datetime
    detectDaytime=rfc3339.rfc3339( datetime.strptime("2021-05-21 15:50:50","%Y-%m-%d %H:%M:%S") )
    lpString="ABC-1234"
    score=0.05
    lpLocation=[0.05,0.05,0.05,0.05]
    lpSize=0.025
    old_lpr_data = None
    old_event_data = None
    debug_dumper("Start finding container ID...")
    container_id = "NO ID"
    container_id = os.popen('docker ps |grep alpr-native').read().split()[0]
    info_dumper("Get container ID! {id}".format(id=container_id))
    while True:
        lpr_detail='detail-' + datetime.strftime( datetime.now(), '%Y-%m-%d' ) + '.csv'
        lpr_event='event-' + datetime.strftime( datetime.now(), '%Y-%m-%d' ) + '.csv'
        #debug_dumper('Reading {filename} from Container {id} ...'.format(filename=lpr_detail,id=container_id) )
        command_readlpr = 'docker exec ' + container_id + ' cat /google/azuretest/csv/' + lpr_detail + ' > ' + lpr_detail
        #debug_dumper('Excute: ' + command_readlpr )
        os.popen(command_readlpr)
        #debug_dumper('Reading {filename} from Container {id} ...'.format(filename=lpr_event,id=container_id) )
        command_readevent = 'docker exec ' + container_id + ' cat /google/azuretest/csv/' + lpr_event + ' > ' + lpr_event
        #debug_dumper('Excute: ' + command_readevent )
        os.popen(command_readevent)
        latest_lpr_data = None
        latest_event_data = None
        await asyncio.sleep(0.5)    #Waiting for cat writing
        try:
            with open(lpr_detail, newline='') as csvfile:
                rows = csv.reader(csvfile)
                for row in rows:
                    latest_lpr_data = row
                debug_dumper('Done! Last Data of {file} is : {data}'.format(file=lpr_detail,data=latest_lpr_data) )
        except:
            debug_dumper('Reading {file} ERROR!!'.format(file=lpr_detail))
        try:   
            with open(lpr_event, newline='') as csvfile:
                rows = csv.reader(csvfile)
                for row in rows:
                    latest_event_data = row
                debug_dumper('Last Data of {file} is : {data}'.format(file=lpr_event,data=latest_event_data) )
        except:
            debug_dumper('Reading {file} ERROR!!'.format(file=lpr_event))
        
        if old_lpr_data != latest_lpr_data and latest_lpr_data != None:
            json_msg = {}
            debug_dumper('Updating License Plate Data : {m}'.format(m=latest_lpr_data))
            try:
                detectDaytime= rfc3339.rfc3339( datetime.strptime(latest_lpr_data[0],"%Y-%m-%d %H:%M:%S") )
                lpString = latest_lpr_data[1]
                score = latest_lpr_data[2]
                lpLocation = [ latest_lpr_data[3],latest_lpr_data[4],latest_lpr_data[5],latest_lpr_data[6] ]
                lpSize = latest_lpr_data[7]
                json_msg["detectDaytime"]=detectDaytime
                json_msg["lpString"]=lpString
                json_msg["score"]=score
                json_msg["lpLocation"]=lpLocation
                json_msg["lpSize"]=lpSize
            except:
                debug_dumper('This License Plate Data is not complete!!')
            else:
                info_dumper('Sending License Plate Telemetry : {m}'.format(m=json_msg))
                await send_telemetry_with_component_name(device_client, json_msg, lpr_device_info_component_name)
                old_lpr_data = latest_lpr_data
        else:
            info_dumper('No License Plate Data Update !!')

        if old_event_data != latest_event_data and latest_event_data != None:
            json_msg = {}
            debug_dumper('Updating Event Data : {m}'.format(m=latest_event_data))
            try:
                eventName = latest_event_data[0]
                eventTime = rfc3339.rfc3339( datetime.strptime(latest_event_data[1],"%Y-%m-%d %H:%M:%S") )
                json_msg["eventName"]=eventName
                json_msg["eventTime"]=eventTime
            except:
                debug_dumper('This Event Data is not complete!!')
            else:
                info_dumper('Sending Event Telemetry : {m}'.format(m=json_msg))
                await send_telemetry_with_component_name(device_client, json_msg, lpr_device_info_component_name)
                old_event_data = latest_event_data
        else:
            info_dumper('No Event Data Update !!')

        
        await asyncio.sleep(lpr_period)

async def reboot_handler(values):
    if values and type(values) == int:
        print("Rebooting after delay of {delay} secs".format(delay=values))
        asyncio.sleep(values)
    print("Done rebooting")

def create_reboot_response(values):
    response = {"result": True, "data": "reboot succeeded"}
    return response

async def setperiod_handler(values):
    global period
    if values and type(values) == int:
        print("Reset telemetry sending period from {delay_old} to {delay} secs".format(delay_old=period,delay=values))
        period = values
    print("Finished period setting!")

def create_setperiod_response(values):
    response = {"result": True, "data": "Reset telemetry sending period succeeded"}
    return response

async def setlprperiod_handler(values):
    global lpr_period
    if values and type(values) == int:
        print("Reset telemetry sending lprperiod from {delay_old} to {delay} secs".format(delay_old=lpr_period,delay=values))
        lpr_period = values
    print("Finished lprperiod setting!")

def create_setlprperiod_response(values):
    response = {"result": True, "data": "Reset telemetry sending lprperiod succeeded"}
    return response

async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key, model_id):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )
    provisioning_device_client.provisioning_payload = {"modelId": model_id}
    return await provisioning_device_client.register()

# For Multiple components
async def send_telemetry_with_component_name(device_client, telemetry_msg, component_name=None):
    msg = pnp_helper.create_telemetry(telemetry_msg, component_name)
    await device_client.send_message(msg)
    print("Sent message")

async def execute_command_listener(
    device_client,
    component_name=None,
    method_name=None,
    user_command_handler=None,
    create_user_response_handler=None,
):
    """
    Coroutine for executing listeners. These will listen for command requests.
    They will take in a user provided handler and call the user provided handler
    according to the command request received.
    :param device_client: The device client
    :param component_name: The name of the device like "sensor"
    :param method_name: (optional) The specific method name to listen for. Eg could be "blink", "turnon" etc.
    If not provided the listener will listen for all methods.
    :param user_command_handler: (optional) The user provided handler that needs to be executed after receiving "command requests".
    If not provided nothing will be executed on receiving command.
    :param create_user_response_handler: (optional) The user provided handler that will create a response.
    If not provided a generic response will be created.
    :return:
    """
    while True:
        if component_name and method_name:
            command_name = component_name + "*" + method_name
        elif method_name:
            command_name = method_name
        else:
            command_name = None

        command_request = await device_client.receive_method_request(command_name)
        print("Command request received with payload")
        values = command_request.payload
        print(values)

        if user_command_handler:
            await user_command_handler(values)
        else:
            print("No handler provided to execute")

        (response_status, response_payload) = pnp_helper.create_response_payload_with_status(
            command_request, method_name, create_user_response=create_user_response_handler
        )

        command_response = MethodResponse.create_from_method_request(
            command_request, response_status, response_payload
        )

        try:
            await device_client.send_method_response(command_response)
        except Exception:
            print("responding to the {command} command failed".format(command=method_name))

async def main():
    print("SYNNEX Technology International Corp. Azure-IoT General Device")
    switch = os.getenv("IOTHUB_DEVICE_SECURITY_TYPE")
    switch = "DPS"
    if switch == "DPS":
        provisioning_host = (
            os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
            if os.getenv("IOTHUB_DEVICE_DPS_ENDPOINT")
            else "global.azure-devices-provisioning.net"
        )
        id_scope = os.getenv("IOTHUB_DEVICE_DPS_ID_SCOPE")
        registration_id = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_ID")
        symmetric_key = os.getenv("IOTHUB_DEVICE_DPS_DEVICE_KEY")

        print('[DEBUG] id_scope={id},\n > registration_id={rid}\n > symmetric_key={skey}'.format(id=id_scope,rid=registration_id,skey=symmetric_key))

        registration_result = await provision_device(
            provisioning_host, id_scope, registration_id, symmetric_key, model_id
        )

        if registration_result.status == "assigned":
            print("Device was assigned")
            print(registration_result.registration_state.assigned_hub)
            print(registration_result.registration_state.device_id)

            device_client = IoTHubDeviceClient.create_from_symmetric_key(
                symmetric_key=symmetric_key,
                hostname=registration_result.registration_state.assigned_hub,
                device_id=registration_result.registration_state.device_id,
                product_info=model_id,
            )
        else:
            raise RuntimeError(
                "Could not provision device. Aborting Plug and Play device connection."
            )

    elif switch == "connectionString":
        conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")
        print("Connecting using Connection String " + conn_str)
        device_client = IoTHubDeviceClient.create_from_connection_string(
            conn_str, product_info=model_id
        )
    else:
        raise RuntimeError(
            "At least one choice needs to be made for complete functioning of this sample."
        )

    # Connect the client.
    await device_client.connect()

    OS_SYSTEM = platform.system()
    MACHINE = platform.machine()
    
    # Command Listener
    # For Multiple components
    if OS_SYSTEM == "Windows":
        listeners = asyncio.gather(
            execute_command_listener(
                device_client,
                windows_device_info_component_name,
                method_name="reboot",
                user_command_handler=reboot_handler,
                create_user_response_handler=create_reboot_response,
            ),
            execute_command_listener(
                device_client,
                windows_device_info_component_name,
                method_name="setperiod",
                user_command_handler=setperiod_handler,
                create_user_response_handler=create_setperiod_response,
            ),
            execute_command_listener(
                device_client,
                lpr_device_info_component_name,
                method_name="setlprperiod",
                user_command_handler=setlprperiod_handler,
                create_user_response_handler=create_setlprperiod_response,
            ),
        )
    elif OS_SYSTEM == "Linux":
        listeners = asyncio.gather(
            execute_command_listener(
                device_client,
                linux_device_info_component_name,
                method_name="reboot",
                user_command_handler=reboot_handler,
                create_user_response_handler=create_reboot_response,
            ),
            execute_command_listener(
                device_client,
                linux_device_info_component_name,
                method_name="setperiod",
                user_command_handler=setperiod_handler,
                create_user_response_handler=create_setperiod_response,
            ),
            execute_command_listener(
                device_client,
                lpr_device_info_component_name,
                method_name="setlprperiod",
                user_command_handler=setlprperiod_handler,
                create_user_response_handler=create_setlprperiod_response,
            ),
        )

    await property_update(device_client,OS_SYSTEM,MACHINE)
    telemetery_update_task = asyncio.create_task(telemetery_update(device_client,OS_SYSTEM,MACHINE))
    lpr_update_task = asyncio.create_task(lpr_update(device_client))

    loop = asyncio.get_running_loop()
    end = loop.run_in_executor(None, end_listener)
    await end

    if not listeners.done():
        listeners.set_result("DONE")
    
    # For Multiple components
    if not property_updates.done():
        property_updates.set_result("DONE")

    listeners.cancel()
    # For Multiple components
    property_updates.cancel()

    telemetery_update_task.cancel()
    lpr_update_task.cancel()

    # finally, disconnect
    await device_client.disconnect()


#================================#
if __name__ == "__main__":
    asyncio.run(main())
