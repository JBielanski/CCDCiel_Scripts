# log_filters_wheel_position.py
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
# Script for log filters wheel current position
#
# Example of Python program that use the CCDciel JSON-RPC interface.
# For more information and reference of the available methods see: 
# https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference
#
# List of changes:
# [22-11-2025] Log filters wheel current position
# ---------------------------------------------------------------------------- #
#

from ccdciel import ccdciel
import sys

connected = (ccdciel('Wheel_connected')['result'])
if not connected :
   ccdciel('LogMsg','Filters wheel not connected!')
   sys.exit(1)

# Get the filters array
filters = ccdciel('Wheel_GetfiltersName')['result']

# Get the current filter
fp = ccdciel('Wheel_getfilter')['result']

# Print the current filter
ccdciel('LogMsg','Current filter is %s' %(filters[int(fp.get('status'))-1]))

