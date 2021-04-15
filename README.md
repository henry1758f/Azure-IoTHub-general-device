# General Device Monitor
This is a python code that makes you get system information and get current CPU/Memory/Storage usage and sent these data via Azure IoT Hub using Azure Device Provisioning Service. 
You can monitor your device's status remotely by Azure IoT Services.
#### To pass the Azure PnP Certification
Please fill the form to let us know, we will contact you as soon as possible.
[LINK to the Form][form_link]
## About Azure PnP in this project
IoT Plug and Play enables solution builders to integrate smart devices with their solutions without any manual configuration. At the core of IoT Plug and Play, is a device model that a device uses to advertise its capabilities to an IoT Plug and Play-enabled application. This project uses [linuxdeviceinfo-1] or [windowsdeviceinfo-1] as device model. 
Support following elements:

| | Element Type | Data Type | Linux Support | Windows Support |
| ------ | ------ | ------ | ------ | ------ |
| hostname | Property | String | YES | YES |
| cpuInfo | Property | String | YES | YES |
|cpuCores | Property | long | YES | YES | 
| cpuMaxfreq | Property | long | YES | YES | 
| biosManufacturer | Property | String | YES | YES | 
| biosVersion | Property | String | YES | YES |
| baseboardManufacturer | Property | String | YES | YES |
| baseboardSerialNumber | Property | String | YES | YES |
| baseboardProduct | Property | String | YES | YES | 
| osVersion | Property | String | YES | YES |
| osBuildNumber | Property | String | YES | YES | 
| memTotal | Property | long | YES | YES |
| logicalDISKtotal | Property | long | YES | YES |
| criticalTemp | Property | double | YES | | 
| ipLocal | Property | String | YES | YES | 
| ipPublic | Property | String | YES | YES |
| highTemp | Property | double | YES | |
| currentTempGPU | Telemetry | double | YES (ARM SoC) | |
| cpuLoading | Telemetry | double | YES | YES | 
| cpuClock | Telemetry | double | YES | YES | 
| memFree | Telemetry | long | YES | YES | 
| memUsage | Telemetry | double | YES | YES |
| logicalDISKfree | Telemetry | long | YES | YES |
| logicalDISKusage | Telemetry | double | YES | YES |
| currentTemp | Telemetry | double | YES | |
| reboot | Command | | YES | YES |
|setperiod | Command | | YES | YES |

## Getting Start
#### 1. Create and set the Azure Device Provision Service (DPS).
#### 2. Clone this repo.
#### 3. Modify the Parameter
Open "[run.sh]" modify by following hint
```sh
export IOTHUB_DEVICE_SECURITY_TYPE="DPS" 
export IOTHUB_DEVICE_DPS_ENDPOINT=" Put your DPS endpoint here" 
export IOTHUB_DEVICE_DPS_ID_SCOPE=" Put your DPS ID Scope here" 
export IOTHUB_DEVICE_DPS_DEVICE_ID=" Put your Device ID here" 
export IOTHUB_DEVICE_DPS_DEVICE_KEY=" Put your Device Key here" 
export IOTHUB_DEVICE_CONNECTION_STRING="" 
#export KEYPAD_INTERRUPT="DISABLE" #If KEYPAD_INTERRUPT set DISABLE, the program will never stop
export KEYPAD_INTERRUPT="ENABLE" #If KEYPAD_INTERRUPT set ENABLE, you can stop the program by pressing 'q' key
```
#### 4. Excute the code
##### For Linux Target
Please make sure you have installed python 3.7+ version.
You can check your python version by
```sh
python3 -V
```
To make run.sh excutable please run
```sh
chmod +x run.sh
```
Then finally, run the script file
```sh
./run.sh
```
##### For Windows Target
Please make sure you have installed python 3.7+ version.And set the environment variable.
Install [git] inorder to run run.sh
Excute the run.sh by [git] shell.

Finally you will see ”Device was assigned” on terminal or git shell, then the program will process monitoring system info and sent message to Azure. You can also use [IoT Hub Explorer] to confirm the message.

If there's any problem please pull an [issue]. Thank you.

[Azure IoT]:<https://docs.microsoft.com/zh-tw/azure/iot-hub/about-iot-hub>
[Azure Device Provisioning Service]:<https://docs.microsoft.com/azure/iot-dps/about-iot-dps>
[linuxdeviceinfo-1]:<https://github.com/Azure/iot-plugandplay-models/blob/main/dtmi/synnex/linuxdeviceinfo-1.json>
[windowsdeviceinfo-1]:<https://github.com/Azure/iot-plugandplay-models/blob/main/dtmi/synnex/windowsdeviceinfo-1.json>
[form_link]:<https://forms.office.com/Pages/ResponsePage.aspx?id=qRDzO7AbAkmVLXiwXlxBKgNN3X18_ZBMisV-J4xFgWtUNzM4RUxWUlFWOEROQTVNTUFRN01FQ0Q5Vi4u>
[run.sh]:<https://github.com/henry1758f/Azure-IoTHub-general-device/blob/55b170a4aadac11906ff4a13d5a74d476bea86d8/run.sh#L8-L15>
[git]:<https://git-scm.com/downloads>
[IoT Hub Explorer]:<https://docs.microsoft.com/zh-tw/azure/iot-pnp/howto-use-iot-explorer>
[issue]:<https://github.com/henry1758f/Azure-IoTHub-general-device/issues/new>
