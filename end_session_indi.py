# end_session_indi.py
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
# Script finish the session, it's dedicated for setups with INDI server
# controlling mount (iOptron CEM-60-EC), focuser and filter wheel.
# The script will do the following operations:
#   - set filter wheel on first position and reset all offsets
#   - set focuser on position ZERO
#   - set iEQ (iOptron CEM-60-EC) in ZERO position (use INDI commands: iEQ)
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
    if (not(indiclient.connectServer())):
       ccdciel('LogMsg',"INDI client is not connected on port %d" %(indi_port))
       return -1
    else:
       ccdciel('LogMsg',"INDI client is connected on port %d" %(indi_port))

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
    sleep_time=60
    time.sleep(sleep_time)

    return 0


def TelescopeGoToHomePosition():
    connected = (ccdciel('Telescope_Connected')['result'])
    if not connected :
       ccdciel('LogMsg','Telescope not connected!')
       return -1

    parked = (ccdciel('Telescope_Parked')['result'])
    if parked :
       ccdciel('LogMsg','Unpark the telescope')
       r = (ccdciel('Telescope_Park',False)['result']['status'])
       ccdciel('LogMsg','Telescope status parked %r' %(r))

    return processing_indi_commands_iEQ()

def SetFocuserToZeroPosition():
    connected = (ccdciel('Focuser_connected')['result'])
    if not connected:
       return -1

    # Get the focuser position
    fp = ccdciel('FocuserPosition')['result']

    # Print the focuser position
    ccdciel('LogMsg','Focuser before setting to ZERO position=%d' %(fp))

    # Set position to 0
    max_time=120
    cur_time=0
    new_pos=0
    if fp > new_pos:
       ccdciel('Focuser_setposition',new_pos)
       fp = ccdciel('FocuserPosition')['result']
       while fp != new_pos:
             if cur_time == max_time:
                ccdciel('LogMsg', 'Focuser not set in position %d during %ds something goes wrong!!!' %(new_pos,max_time))
                break
             time.sleep(1)
             fp = ccdciel('FocuserPosition')['result']
             cur_time=cur_time+1

    # Print the focuser position
    fp = ccdciel('FocuserPosition')['result']
    ccdciel('LogMsg','Focuser after setting to ZERO position=%d' %(fp))
    return 0


def SetFilterToFirst():
    connected = (ccdciel('Wheel_connected')['result'])
    if not connected :
       return -1

    # Get the filters array
    filters = ccdciel('Wheel_GetfiltersName')['result']

    # Get the current filter
    fp = ccdciel('Wheel_getfilter')['result']

    # Print the current filter
    cur_pos=int(fp.get('status'))-1
    ccdciel('LogMsg','Current filter is %s' %(filters[cur_pos]))

    # Reset filters offsets
    for idf,f in enumerate(filters):
       ccdciel('Set_FilterOffset',[f,0])

    # Set filter position to first
    max_time=30
    cur_time=0
    new_pos=0
    cur_pos=int(fp.get('status'))-1
    if cur_pos != new_pos:
       ccdciel('Wheel_setfilter',(new_pos+1))
       while cur_pos != new_pos:
             if cur_time == max_time:
                ccdciel('LogMsg', 'Filter wheel not set in first position %s during %ds something goes wrong!!!' %(filters[new_pos],max_time))
                break
             time.sleep(1)
             fp = ccdciel('Wheel_getfilter')['result']
             cur_pos=int(fp.get('status'))-1
             cur_time=cur_time+1

    # Print the final filter position
    fp = ccdciel('Wheel_getfilter')['result']
    cur_pos=int(fp.get('status'))-1
    ccdciel('LogMsg','Final filter is %s' %(filters[cur_pos]))

    return 0

#
# MAIN PROGRAM
#
if SetFocuserToZeroPosition() == -1:
   ccdciel('LogMsg','Focuser not connected!')
else:
   ccdciel('LogMsg','Focuser position has been set to ZERO')

if SetFilterToFirst() == -1:
   ccdciel('LogMsg','Filters wheel not connected!')
else:
   ccdciel('LogMsg','Position in filter wheel has been set to FIRST')


if TelescopeGoToHomePosition() == -1:
    ccdciel('LogMsg','Can not move mount iEQ into HOME position!')
else:
    ccdciel('LogMsg','The iEQ mount has been moved into HOME position')



