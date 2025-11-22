# log_focuser_position.py
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
# Script for log focuser position
#
# Example of Python program that use the CCDciel JSON-RPC interface.
# For more information and reference of the available methods see: 
# https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference
#
# List of changes:
# [22-11-2025] Log focuser current position
# ---------------------------------------------------------------------------- #
#

from ccdciel import ccdciel
import sys

connected = (ccdciel('Focuser_connected')['result'])
if not connected :
   ccdciel('LogMsg','Focuser not connected!')
   sys.exit(1)

# Get the focuser position
fp = ccdciel('FocuserPosition')['result']

# Print the focuser position
ccdciel('LogMsg','Focuser position=%d' %(fp))

