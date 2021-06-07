################################################
# SYNNEX International Technology Corp.
# General Device Monitor with Azure IoT Hub
# henryhuang@synnex-grp.com
################################################
#!/bin/bash
# set the STRING variable
export IOTHUB_DEVICE_SECURITY_TYPE=""
export IOTHUB_DEVICE_DPS_ENDPOINT=""
export IOTHUB_DEVICE_DPS_ID_SCOPE=""
export IOTHUB_DEVICE_DPS_DEVICE_ID=""
export IOTHUB_DEVICE_DPS_DEVICE_KEY=""
export IOTHUB_DEVICE_CONNECTION_STRING=""
#export KEYPAD_INTERRUPT="DISABLE"
export KEYPAD_INTERRUPT="ENABLE"

# print the contents of the variable on screen
echo $IOTHUB_DEVICE_SECURITY_TYPE
echo $IOTHUB_DEVICE_DPS_ENDPOINT
echo $IOTHUB_DEVICE_DPS_ID_SCOPE
echo $IOTHUB_DEVICE_DPS_DEVICE_ID
echo $IOTHUB_DEVICE_DPS_DEVICE_KEY
echo $IOTHUB_DEVICE_CONNECTION_STRING
echo $KEYPAD_INTERRUPT

pip3 install -r requirements.txt || pip install -r requirememts.txt
python3 main.py || python main.py 