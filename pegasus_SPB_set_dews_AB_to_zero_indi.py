# pegasus_SPB_set_dews_AB_to_zero_indi.py
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
#  This script setting dews power to manual and zero values for A and B port in Pegasus Astro Saddle Power Box.
#  Beware the action is immediate and without confirmation message!
#  The script is dedicated for setups with INDI server controlling Pegasus Astro Saddle Power Box.
#
# Example of Python program that use the CCDciel JSON-RPC interface.
# For more information and reference of the available methods see: 
# https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference
#
# Script needs installed pyindi_client
# sudo apt-get install swig libz3-dev libcfitsio-dev libnova-dev
# pip3 install --user --break-system-packages pyindi-client
#
# List of changes:
# [22-11-2025] Initial working version
# ---------------------------------------------------------------------------- #
#

from ccdciel import ccdciel
import PyIndi
import sys
import time

# INDI CLIENT CLASS
class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
    def newDevice(self, d):
        pass
    def newProperty(self, p):
        pass
    def removeProperty(self, p):
        pass
    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
        pass
    def newSwitch(self, svp):
        pass
    def newNumber(self, nvp):
        pass
    def newText(self, tvp):
        pass
    def newLight(self, lvp):
        pass
    def newMessage(self, d, m):
        pass
    def serverConnected(self):
        pass
    def serverDisconnected(self, code):
        pass

def processing_indi_commands_pa_spb():
    # Monitore Pegasus Astro Saddle Power Box 'Pegasus SPB' manager
    pa_spb="Pegasus SPB"
    device_pa_spb=None
    pa_spb_connected=None

    # Get INDI on port
    default_indi_port=7625
    indi_port=default_indi_port
    if len(sys.argv) > 1:
       indi_port=int(sys.argv[1])

    # Trying connect to INDI
    indiclient=IndiClient()
    indiclient.setServer("localhost",indi_port)

    # Check is INDI connected
    sleep_time=2.0
    if (not(indiclient.connectServer())):
       ccdciel('LogMsg',"INDI client is not connected on port %d" %(indi_port))
       sys.exit(1)
    else:
       ccdciel('LogMsg',"INDI client is connected on port %d" %(indi_port))
    time.sleep(sleep_time)

    # Connect to 'Pegasus SPB' mount
    max_time=30
    cur_time=0
    sleep_time=0.5
    device_pa_spb=indiclient.getDevice(pa_spb)
    while not(device_pa_spb):
          if cur_time == max_time:
               ccdciel('LogMsg',"Pegasus Astro Saddle Power Box mount not connected during %d, something goes wrong!!!" %(max_time))
               sys.exit(1)
          time.sleep(sleep_time)
          device_pa_spb=indiclient.getDevice(pa_spb)
          cur_time=cur_time+sleep_time

    print("Driver: %s" % str(device_pa_spb.getDriverName()))
    pa_spb_dew_operation_auto=device_pa_spb.getSwitch("DEWAUTO")
    pa_spb_dew_operation_auto_str=str(pa_spb_dew_operation_auto)
    print(pa_spb_dew_operation_auto_str)
    a=dir(pa_spb_dew_operation_auto)
    print(a)
    print(str(pa_spb_dew_operation_auto.getStateAsString()))
    b=pa_spb_dew_operation_auto.getLabel()
    print(str(b))
    c=dir(pa_spb_dew_operation_auto[0])
    print(str(c))



    d=pa_spb_dew_operation_auto[0].getState()
    print("(0) Enabled: %s : %s" % (str(d), str(pa_spb_dew_operation_auto[0].getStateAsString())))
    d=pa_spb_dew_operation_auto[1].getState()
    print("(0) Disabled: %s : %s" % (str(d), str(pa_spb_dew_operation_auto[1].getStateAsString())))
    pa_spb_dew_operation_auto[0].setState(1)
    pa_spb_dew_operation_auto[1].setState(0)
    d=pa_spb_dew_operation_auto[0].getState()
    print("(0) Enabled: %s : %s" % (str(d), str(pa_spb_dew_operation_auto[0].getStateAsString())))
    d=pa_spb_dew_operation_auto[1].getState()
    print("(0) Disabled: %s : %s" % (str(d), str(pa_spb_dew_operation_auto[1].getStateAsString())))
    #ccdciel('LogMsg',"Pegasus Astro Saddle Power Box DewAutoSP: %s" % (pa_spb_dew_operation_auto_str))


#
# MAIN PROGRAM
#

# Check is weather station connected - temporary disabled
#connected = (ccdciel('weather_station_connected')['details'])
#if not connected :
#   ccdciel('LogMsg','Weather station not connected!')
#   sys.exit(1)
   
# Go home position using INDI
processing_indi_commands_pa_spb()
