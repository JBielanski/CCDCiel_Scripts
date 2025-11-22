# iEQ_scope_go_home_indi.py
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
#  This script setting in HOME POSITION the telescope mount.
#  Beware the action is immediate and without confirmation message!
#  The script is dedicated for setups with INDI server controlling iOptron CEM-60-EC mount.
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
# [22-11-2025] Working version
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

def processing_indi_commands_iEQ():
    # Monitore iEQ 'iOptron CEM60-EC' mount
    mount="iEQ"
    device_mount=None
    mount_connected=None

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

    # Connect to iEQ mount
    max_time=30
    cur_time=0
    sleep_time=0.5
    device_mount=indiclient.getDevice(mount)
    while not(device_mount):
          if cur_time == max_time:
               ccdciel('LogMsg',"iEQ mount not connected during %d, something goes wrong!!!" %(max_time))
               sys.exit(1)
          time.sleep(sleep_time)
          device_mount=indiclient.getDevice(mount)
          cur_time=cur_time+sleep_time

    # iEQ go to HOME
    mount_home_operation=device_mount.getSwitch("HOME")
    ccdciel('LogMsg',"INDI iEQ go to home position...")

    # Set switch to GO HOME
    # mount_home_operation[0].s -  SET CURRENT POSITION AS HOME
    # mount_home_operation[1].s -  GO HOME
    # mount_home_operation[2].s -  FIND HOME
    mount_home_operation[1].s=1
    indiclient.sendNewSwitch(mount_home_operation)


#
# MAIN PROGRAM
#

connected = (ccdciel('Telescope_Connected')['result'])
if not connected :
   ccdciel('LogMsg','Telescope not connected!')
   sys.exit(1)
   
parked = (ccdciel('Telescope_Parked')['result'])
if parked :
   ccdciel('LogMsg','Unpark the telescope')
   r = (ccdciel('Telescope_Park',False)['result']['status'])
   ccdciel('LogMsg','Telescope status parked %r' %(r))

# Go home position using INDI
processing_indi_commands_iEQ()
