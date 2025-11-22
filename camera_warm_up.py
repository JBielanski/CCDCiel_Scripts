# camera_warm_up.py
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
# Script to manage focuser position per filter
# - warm up the camera to constant 20C
#
# Example of Python program that use the CCDciel JSON-RPC interface.
# For more information and reference of the available methods see: 
# https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference
#
# List of changes:
# [21-11-2025] Initial version, simple camera warm up script to 20C
# ---------------------------------------------------------------------------- #
#

from ccdciel import ccdciel
import sys
import time

connected = (ccdciel('Camera_connected')['result'])
if not connected :
   ccdciel('LogMsg','Camera is not connected!')
   sys.exit(1)

# Warm up the camera, setting the temperature to 20 C
# TODO: could be improved by taken ambient temperature into account
ccdciel('Ccd_settemperature',20)
ccdciel('LogMsg','Warming up the camera to 20 C...')

# Loop until the camera temperature reaches 20 C or 5 minutes have passed
start_time = time.time()
while True:
    ct = ccdciel('CcdTemp')['result']
    if ct >= 20:
        break
    if time.time() - start_time > 300:
        ccdciel('LogMsg','Timeout reached while warming up the camera.')
        break
    ccdciel('LogMsg','Curent main camera temperature = %lf C' %(ct))
    time.sleep(5)

# Final temperature log
ct = ccdciel('CcdTemp')['result']
ccdciel('LogMsg','Camera warm up completed. Current temperature = %lf C' %(ct))
