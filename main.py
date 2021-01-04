import psutil
import asyncio
import platform
import json
import os
import sys

#for IP Address obtain
import socket
import requests
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import constant, Message, MethodResponse

## for DPS Testing
model_id = ""
#================#
OS_SYSTEM = "N/A"
period = 2

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


async def property_update(device_client):
    print("[DEBUG] Update System Message")
    OS_SYSTEM = platform.system()
    memTotal = psutil.virtual_memory().total
    # get IP Address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipLocal = s.getsockname()[0]
    s.close()
    ipPublic = requests.get('http://ifconfig.me/ip', timeout=1).text.strip()
    #

    if OS_SYSTEM == "Windows":
        root_path = 'C:/'
        hostname_str = platform.node()
        cpuInfo = ' '.join(os.popen('wmic cpu get name').read().splitlines()[2].split() )
        biosManufacturer = ' '.join(os.popen('wmic bios get Manufacturer').read().splitlines()[2].split() )
        biosVersion = ''.join(os.popen('wmic bios get Version').read().splitlines()[2].split() )
        baseboardManufacturer = ''.join(os.popen('wmic baseboard get Manufacturer').read().splitlines()[2].split() )
        baseboardSerialNumber = ''.join(os.popen('wmic baseboard get SerialNumber').read().splitlines()[2].split() )
        baseboardProduct = ''.join(os.popen('wmic baseboard get Product').read().splitlines()[2].split() )
        osVersion = ''.join(os.popen('wmic os get Version').read().splitlines()[2].split() )
        osBuildNumber = ''.join(os.popen('wmic os get BuildNumber').read().splitlines()[2].split() )

    elif OS_SYSTEM == "Linux":
        root_path = '/'
        hostname_str = platform.node()
        cpuInfo = ' '.join(os.popen('lscpu |grep "Model name"').read().split(':')[1].split() )
        biosManufacturer = ' '.join(os.popen('cat /sys/class/dmi/id/bios_vendor').read().split() )
        biosVersion = ' '.join(os.popen('cat /sys/class/dmi/id/bios_version').read().split() )
        baseboardManufacturer = ' '.join(os.popen('cat /sys/class/dmi/id/board_vendor').read().split() )
        baseboardSerialNumber = ' '.join(os.popen('sudo cat /sys/class/dmi/id/board_serial').read().split() )
        baseboardProduct = ' '.join(os.popen('cat /sys/class/dmi/id/board_name').read().split() )
        osVersion = ' '.join(os.popen('hostnamectl |grep "Operating System"').read().split(':')[1].split() )
        osBuildNumber = ' '.join(os.popen('hostnamectl |grep "Kernel"').read().split(':')[1].split() )
        # Linux Only
        highTemp = psutil.sensors_Temperatures()['coretemp'][0][2]
        criticalTemp = psutil.sensors_Temperatures()['coretemp'][0][3]


    logicalDISKtotal = psutil.disk_usage(root_path).total

    # Print Property result
    print('============================')
    print('Property List Upodate >>>>>>')
    print("OS type : {os}".format(os=OS_SYSTEM))
    print("OS Version : {osV}".format(osV=osVersion))
    print("OS Build/Kernel : {osK}".format(osK=osBuildNumber))
    print("Hostname : {host}".format(host=hostname_str))
    print("CPU Info : {cpu}".format(cpu=cpuInfo))
    if OS_SYSTEM == "Linux":
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

    # Sending System Property 
    await device_client.patch_twin_reported_properties({"hostname": hostname_str})
    await device_client.patch_twin_reported_properties({"cpuInfo": cpuInfo})
    await device_client.patch_twin_reported_properties({"biosManufacturer": biosManufacturer})
    await device_client.patch_twin_reported_properties({"biosVersion": biosVersion})
    await device_client.patch_twin_reported_properties({"baseboardManufacturer": baseboardManufacturer})
    await device_client.patch_twin_reported_properties({"baseboardSerialNumber": baseboardSerialNumber})
    await device_client.patch_twin_reported_properties({"baseboardProduct": baseboardProduct})
    await device_client.patch_twin_reported_properties({"osVersion": osVersion})
    await device_client.patch_twin_reported_properties({"osBuildNumber": osBuildNumber})
    await device_client.patch_twin_reported_properties({"memTotal": memTotal})
    await device_client.patch_twin_reported_properties({"logicalDISKtotal": logicalDISKtotal})
    await device_client.patch_twin_reported_properties({"ipLocal": ipLocal})
    await device_client.patch_twin_reported_properties({"ipPublic": ipPublic})
    if OS_SYSTEM == "Linux":
        await device_client.patch_twin_reported_properties({"highTemp": highTemp})
        await device_client.patch_twin_reported_properties({"criticalTemp": criticalTemp})
    #

async def telemetery_update(device_client):
    print('[DEBUG] Start sending telemetry every {sec} Second(s).'.format(sec=period))
    while True:
        cpuLoading = psutil.cpu_percent()
        cpuClock =  psutil.cpu_freq().current
        mem_free = psutil.virtual_memory().free
        mem_usg = psutil.virtual_memory().percent
        logicalDISKfree = psutil.disk_usage('C:/').free
        logicalDISKpercent = psutil.disk_usage('C:/').percent
        
        json_msg = {}
        json_msg["cpuLoading"]=cpuLoading
        json_msg["cpuClock"]=cpuClock
        json_msg["memFree"]=mem_free
        json_msg["memUsg"]=mem_usg
        json_msg["logicalDISKfree"]=logicalDISKfree
        json_msg["logicalDISKpercent"]=logicalDISKpercent
        print('[DEBUG] Sending Telemetry :{m}'.format(m=json_msg))
        await telemetry_sender(device_client, json_msg)
        await asyncio.sleep(period)
    
    
async def telemetry_sender(device_client, telemetry_msg):
    msg = Message(json.dumps(telemetry_msg))
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    print("Sent message")
    await device_client.send_message(msg)

async def reboot_handler(values):
    if values and type(values) == int:
        print("Rebooting after delay of {delay} secs".format(delay=values))
        asyncio.sleep(values)

    print("Done rebooting")

def create_reboot_response(values):
    response = {"result": True, "data": "reboot succeeded"}
    return response

async def setperiod_handler(values):
    if values and type(values) == int:
        print("Reset telemetry sending period from {delay_old} to {delay} secs".format(delay_old=period,delay=values))
        period = values
    print("Finished period setting!")

def create_setperiod_response(values):
    response = {"result": True, "data": "Reset telemetry sending period succeeded"}
    return response

async def execute_command_listener(device_client, method_name, user_command_handler, create_user_response_handler):
    while True:
        if method_name:
            command_name = method_name
        else:
            command_name = None

        command_request = await device_client.receive_method_request(command_name)
        print("Command request received with payload ({method_name})".format(method_name=method_name))
        print(command_request.payload)

        values = {}
        if not command_request.payload:
            print("Payload was empty.")
        else:
            values = command_request.payload

        await user_command_handler(values)

        response_status = 200
        response_payload = create_user_response_handler(values)

        command_response = MethodResponse.create_from_method_request(
            command_request, response_status, response_payload
        )

        try:
            await device_client.send_method_response(command_response)
        except Exception:
            print("responding to the {command} command failed".format(command=method_name))


async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key, model_id):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )
    provisioning_device_client.provisioning_payload = {"modelId": model_id}
    return await provisioning_device_client.register()

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
    # Command Listener
    listeners = asyncio.gather(
        execute_command_listener(
            device_client,
            method_name="reboot",
            user_command_handler=reboot_handler,
            create_user_response_handler=create_reboot_response,
        ),
        execute_command_listener(
            device_client,
            method_name="setperiod",
            user_command_handler=setperiod_handler,
            create_user_response_handler=create_setperiod_response,
        ),
    )
    await property_update(device_client)
    telemetery_update_task = asyncio.create_task(telemetery_update(device_client))

    loop = asyncio.get_running_loop()
    end = loop.run_in_executor(None, end_listener)
    await end

    if not listeners.done():
        listeners.set_result("DONE")

    listeners.cancel()

    telemetery_update_task.cancel()

    # finally, disconnect
    await device_client.disconnect()




    #await property_update(device_client)

    #await telemetery_update(device_client)



#================================#
if __name__ == "__main__":
    asyncio.run(main())