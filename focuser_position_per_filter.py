# focuser_position_per_filter.py
# SPDX-FileCopyrightText: 2025 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
#
# ---------------------------------------------------------------------------- #
# Script to manage focuser position per filter
# - calculate focuser position for selected filter using autofocus tool
# - store information about filter and calculated focus point in database
# - read and set focuser position from/to database
# - work in three modes:
# -- 'CALCULATE' [default] calculate focuser position for all filters in filter wheel and store in database
# -- 'READ' read configuration for focuser and filters from database
# -- 'RESET' reset focuser position to 0, set first filter in filters wheel, remove all offsets for filters
# Script use the CCDciel JSON-RPC interface.
# For more information and reference of the available methods see: 
# https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference
#
# List of changes:
# [26-10-2025] Initial version
# - calculate focuser position for selected filter using autofocus tool
# - store information about filter and calculated focus point in database
# [28-10-2025]
# - script remember filter which was set before script has been started
# - script try to use current focuser position to initial for autofocus if:
# -- can not read position from database
# -- focuser position send as parameter to script is 0
# - script exit if focuser position is 0 and ask to set it manually
# - script at the end return to filter which was set before script has 
#   been started and set focuser position to calculated value for this filter
# [29-10-2025]
# - added reference filter and offset for each filter in database
# - move to reference filter after calculate focuser position for all filters in filters wheel
# [01-11-2025]
# - added working modes: CALCULATE (default) and READ
# - added command line arguments parser
# [02-11-2025]
# - added RESET working mode to reset focuser positions and offsets for all filters
# - added check for sqlite3 module
# [07-11-2025]
# - support CCDCiel version
# - disable setting OFFSET for CCDCiel older than 0.9.92.3829
# - added option which allow to provide reference filter: --filtername, -n <filter name>
# - added selection between AutomaticAutofocus and Autofocus by: --focustype, -t <autofocus type: AUTO, INPLACE>
# [09-11-2025]
# - added filter usage flag in database, allow to reduce filters for which will autofocus to selected subset: SELECTED FILTERS + REFERENCE FILTER
# - for other filters only offset will be recalculated
# - release under GPL-3.0 license
# [12-11-2025]
# - added command line argument to select filters subset like "-s [1,3,4,5]" for slots 1,3,4 and 5: --subset, -s <list of filter indexes>
# [14-11-2025]
# - added selection of reference filter by ID --filterid, -i <filter index>
# - selection reference filter by name and index can not be use together, use: --filtername, -n <filter name> OR --filterid, -i <filter index>
# ---------------------------------------------------------------------------- #
#

from ccdciel import ccdciel
import sqlite3
import os
import sys
import time

# ERROR CODES
# 0   - no error / success
# 11  - focuser not connected (critical error)
# 12  - cannot set new focuser position
# 13  - cannot return to initial focuser position
# 15  - using current focuser position as initial position
# 21  - filter wheel not connected (critical error)
# 22  - specified filter not found
# 23  - cannot set filter in filter wheel
# 24  - cannot restore filter in filter wheel (critical error)
# 31  - cannot open database
# 32  - cannot read focuser position for selected filter
# 33  - no focuser position for selected filter in database
# 34  - cannot read reference flag for selected filter
# 35  - cannot read offset for selected filter
# 36  - cannot read reference flag and offset for selected filter
#

# GLOBAL VARIABLES
this_script_path = os.path.abspath(__file__) # Path to this script
this_script_dir = os.path.dirname(this_script_path) # Directory of this script
ccdciel_version = ccdciel('CCDciel_Version')['result'] # Main version, short revision, full revision stored in array
initial_focuser_position = 0 # Initial focuser position
filters_and_focuser_positions_database_file = 'focuser_position_per_filter.db' # Name of file with filters and focuser positions
filters_and_focuser_positions_database_directory = this_script_dir # Directory with database file
filter_name_to_set = ['', 0, None, None] # Filter name and position provided by user otherwise used reference filter or current filter in filter wheel
filters_subset = [] # List of selected filters for which autofocus will be performed provided by argument
script_working_mode = 0 # Script working mode, 0 - calculate focuser position for all filters in filter wheel, 1 - read focuser position for selected filter from database
focus_type = 0 # Autofocus type AUTO - with eventually move to a bright star, INPLACE - autofocus in place

# arguments_parser - parse arguments from command line
# @arguments
# --dbname, -d <database file name>
# --focuserposition, -f <focuser position>
# --filtername, -n <filter name>
# --filterid, -i <filter index>
# --subset, -s <list of filter indexes>
# --focustype, -t <autofocus type: AUTO, INPLACE>
# --mode, -m <working mode: CALCULATE, READ, RESET>
# --help, -help - display help
def arguments_parser():
   """Parse command line arguments and update global settings.

   Supported options:
   --dbname, -d <database file name>
   --focuserposition, -f <focuser position>
   --filtername, -n <filter name>
   --filterid, -i <filter index>
   --subset, -s <list of filter indexes>
   --focustype, -t <autofocus type: AUTO, INPLACE>
   --mode, -m <working mode>: CALCULATE, READ, RESET
   --help, -help - display help and exit

   If provided, this updates the module-level globals:
   - filters_and_focuser_positions_database_file
   - initial_focuser_position
   """
   global initial_focuser_position
   global filters_and_focuser_positions_database_file
   global filter_name_to_set
   global script_working_mode
   global filters_subset

   usage = (
      "Usage: {} [--mode|-m CALCULATE (default)/READ/RESET] [--dbname|-d <database>] [--focuserposition|-f <pos>] [--subset|-s <list of filter indexes>] [--focustype|-t <autofocus type: AUTO (default)/INPLACE>] [--filtername|-n <name>] [--filterid|-i <index>] [--help|-help]".format(sys.argv[0])
   )

   # Test reference filter id/name flag 
   filter_name_id_provided = False

   args = sys.argv[1:]
   if not args:
      return

   i = 0
   while i < len(args):
      a = args[i]
      if a in ("--help", "-help"):
         print(usage)
         print("\nOptions:\n  --mode,-m <working mode: CALCULATE (default)/READ/RESET>\n --dbname, -d <database file name>\n  --focuserposition, -f <focuser position>\n  --focustype, -t <autofocus type: AUTO (default)/INPLACE>\n  --filtername, -n <name>\n  --filterid, -i <filter index>\n  --subset, -s <list of filter indexes>\n  --help, -help\n")
         sys.exit(0)
      elif a in ("--dbname", "-d"):
         if i + 1 >= len(args):
            print("Error: missing value for %s" % a)
            print(usage)
            sys.exit(1)
         filters_and_focuser_positions_database_file = args[i+1]
         ccdciel('LogMsg', 'Database name set from arguments: %s' % (filters_and_focuser_positions_database_file))
         i += 2
      elif a in ("--focuserposition", "-f"):
         if i + 1 >= len(args):
            print("Error: missing value for %s" % a)
            print(usage)
            sys.exit(1)
         try:
            initial_focuser_position = int(args[i+1])
         except ValueError:
            print("Error: invalid focuser position, must be integer: %s" % args[i+1])
            sys.exit(1)
         ccdciel('LogMsg', 'Initial focuser position set from arguments: %d' % (initial_focuser_position))
         i += 2
         
      elif a in ("--focustype", "-t"):
         if i + 1 >= len(args):
            print("Error: missing value for %s" % a)
            print(usage)
            sys.exit(1)
         mode_arg = args[i+1].upper()
         if mode_arg == "AUTO":
            focus_type = 0
         elif mode_arg == "INPLACE":
            focus_type = 1
         else:
            print("Error: invalid focus type for %s, must be AUTO, INPLACE" % a)
            print(usage)
            sys.exit(1)
         ccdciel('LogMsg', 'Script working mode set from arguments: %s' % (mode_arg))
         i += 2
         
      elif a in ("--filtername", "-n"):
         if filter_name_id_provided:
            print("Error: both filter name and filter index provided, please provide only one of them")
            print(usage)
            sys.exit(1)
         if i + 1 >= len(args):
            print("Error: missing value for %s" % a)
            print(usage)
            sys.exit(1)
         filter_name_to_set[2] = args[i+1]
         filter_name_id_provided = True
         ccdciel('LogMsg', 'Initial focuser position set from arguments: %d' % (initial_focuser_position))
         i += 2
      
      elif a in ("--filterid", "-i"):
         if filter_name_id_provided:
            print("Error: both filter name and filter index provided, please provide only one of them")
            print(usage)
            sys.exit(1)
         if i + 1 >= len(args):
            print("Error: missing value for %s" % a)
            print(usage)
            sys.exit(1)
         try:
            filter_name_to_set[3] = int(args[i+1])
         except ValueError:
            print("Error: invalid filter index, must be integer: %s" % args[i+1])
            sys.exit(1)
         filter_name_id_provided = True
         ccdciel('LogMsg', 'Filter index to set provided from arguments: %d' % (filter_name_to_set[3]))
         i += 2

      elif a in ("--subset", "-s"):
         if i + 1 >= len(args):
            print("Error: missing value for %s" % a)
            print(usage)
            sys.exit(1)
         subset_arg = args[i+1]
         try:
            filters_subset = [int(x) for x in subset_arg.strip('[]').split(',')]
         except ValueError:
            print("Error: invalid subset format for %s, must be a list of integers like [1,3,4]" % a)
            print(usage)
            sys.exit(1)
         ccdciel('LogMsg', 'Filter subset set from arguments: %s' % (filters_subset))
         i += 2

      elif a in ("--mode", "-m"):
         if i + 1 >= len(args):
            print("Error: missing value for %s" % a)
            print(usage)
            sys.exit(1)
         mode_arg = args[i+1].upper()
         if mode_arg == "CALCULATE":
            script_working_mode = 0
         elif mode_arg == "READ":
            script_working_mode = 1
         elif mode_arg == "RESET":
            script_working_mode = 2
         else:
            print("Error: invalid mode value for %s, must be CALCULATE, READ or RESET" % a)
            print(usage)
            sys.exit(1)
         ccdciel('LogMsg', 'Script working mode set from arguments: %s' % (mode_arg))
         i += 2
      else:
         print("Unknown argument: %s" % a)
         print(usage)
         sys.exit(1)

   return
   
# check_for_version_neq_0_9_92_3829
# @return status
# 1 - newer version
# 0 - older version
def check_for_version_neq_0_9_92_3829(display_log):
   global ccdciel_version
   status = 0 # Status of operation
   if ccdciel_version[0] == '0.9.92':
      if int(ccdciel_version[1]) >= 3829:
         status = 1
         if display_log == 1:
            ccdciel('LogMsg', 'Setting FILTERS OFFSETS for FOCUSER supported in script')
      else:
         if display_log == 1:
            ccdciel('LogMsg', 'Setting FILTERS OFFSETS for FOCUSER NOT supported in script, minimal version is 0.9.92-3829')
   else:
      if display_log == 1:
         ccdciel('LogMsg', 'Setting FILTERS OFFSETS for FOCUSER NOT supported in script, minimal version is 0.9.92-3829')
   return status

# check_necessary_components - check if necessary components are connected
# @return status - status of operation
# 0 - all necessary components are connected
# EXIT - script exit due to critical error
def check_necessary_components():
   status = 0 # Status of operation

   if 'sqlite3' in sys.modules:
      ccdciel('LogMsg','sqlite3 module is already imported.')
   else:
      ccdciel('LogMsg','[CRITICAL ERROR] sqlite3 module is not imported!')
      if os.name == 'posix':
         ccdciel('LogMsg','On Debian-based systems you can install it using: sudo apt-get install sqlite3 libsqlite3-dev')
      elif os.name == 'nt':
         ccdciel('LogMsg','On Windows systems you can install it using: pip install pysqlite3')
      else:
         ccdciel('LogMsg','Please refer to your system documentation for installing sqlite3 module.')       
      exit(1)

   # Check focuser is connected
   connected_f = (ccdciel('Focuser_connected')['result'])
   if not connected_f :
      ccdciel('LogMsg','[CRITICAL ERROR] Focuser not connected!')
      status = 11

   # Check filter wheel is connected
   connected_w = (ccdciel('Wheel_connected')['result'])
   if not connected_w :
      ccdciel('LogMsg','[CRITICAL ERROR] Filter wheel not connected!')
      status = 21

   # Offsets support
   check_for_version_neq_0_9_92_3829(1)

   # Exit script if necessary components are not connected
   if status != 0:
      ccdciel('LogMsg','[CRITICAL ERROR] Necessary components are not connected, script will exit!')
      exit(1)

   return status

# reset_focuser_positions_and_offsets - reset focuser positions and offsets for all filters
def reset_focuser_positions_and_offsets():
   global initial_focuser_position

   # Get list of filters in filter wheel
   list_of_filters = (ccdciel('Wheel_GetfiltersName')['result'])

   # Reset offset for each filter in filters wheel
   for idf,f in enumerate(list_of_filters):
      ccdciel('Set_FilterOffset',[f,0])
      ccdciel('LogMsg','Reset offset for filter index: %d name: %s to 0' % (idf+1,f))
   
   # Set filter in filter wheel to reference filter (first filter)
   ccdciel('Wheel_setfilter',1)
   
   # Set focuser position to initial focuser position if provided
   if initial_focuser_position >= 0:
      set_focuser_position(initial_focuser_position)
      ccdciel('LogMsg','Set focuser position to initial focuser position %d' % (initial_focuser_position))

   return

# get_reference_filter_from_application_arguments - get reference filter provided by application arguments
# @return Nothing
def get_reference_filter_from_application_arguments():
   global filter_name_to_set

   # Get current filter in filter wheel
   cur_fwheel_dict = ccdciel('Wheel_getfilter')['result']
   cur_filter_index = int(cur_fwheel_dict.get("status"))
   filter_name_to_set[0] = (ccdciel('Wheel_GetfiltersName')['result'])[cur_filter_index-1]
   filter_name_to_set[1] = cur_filter_index

   # Get list of filters in filter wheel
   list_of_filters = (ccdciel('Wheel_GetfiltersName')['result'])

   # Looking for filter provided by parameters
   if filter_name_to_set[2] != None or filter_name_to_set[3] != None:
      reference_filter_found = False
      for idf,f in enumerate(list_of_filters):
         if filter_name_to_set[2] != None:
            if f == filter_name_to_set[2]:
               filter_name_to_set[0] = f
               filter_name_to_set[1] = idf+1
               filter_name_to_set[3] = idf+1
               reference_filter_found = True
               break
         if filter_name_to_set[3] != None:
            if (idf+1) == filter_name_to_set[3]:
               filter_name_to_set[0] = f
               filter_name_to_set[1] = idf+1
               filter_name_to_set[2] = f
               reference_filter_found = True
               break

      if reference_filter_found == False:
         if filter_name_to_set[2] != None:
            ccdciel('LogMsg','[WARNING] Filter name %s not found in filter wheel use current' % (filter_name_to_set[2]))
         if filter_name_to_set[3] != None:
            ccdciel('LogMsg','[WARNING] Filter position %d not found in filter wheel use current' % (filter_name_to_set[3]))
         filter_name_to_set[2] = None
         filter_name_to_set[3] = None

# get_focuser_position_for_filter_from_database - get focuser position for selected filter from database
# @arguments
# db_name - name of file with database
# db_directory - directory with database file
# filter_name - name of filter for which data will be read
#
# @return status, array  with: focuser_position, reference flag, filter offset and filter usage flag
# 0 - no error / success
# 31 - can not open database
# 32 - can not ready any data for selected filter
# 33 - can not read focuser position for selected filter
# 34 - can not read reference flag for selected filter
# 35 - can not read offset for selected filter
# 36 - can not read reference flag and offset for selected filter
#
def get_focuser_position_for_filter_from_database(db_name, db_directory, filter_name):
   status = 0 # Status of operation
   status_array = [0,0,0, ] # Status array for focuser position, reference flag, offset and usage flag
   focuser_position_reference_flag_offset_and_usage_flag = [0, 0, 0, 0] # Focuser position, reference flag, offset and usage flag for selected filter

   ccdciel('LogMsg','Database directory: %s name: %s' %(db_directory, db_name))
   ccdciel('LogMsg','Selected filter name: %s' %(filter_name))

   # Open database
   try:
      conn = sqlite3.connect(os.path.join(db_directory, db_name))
      cursor = conn.cursor()
   except sqlite3.Error as e:
      ccdciel('LogMsg','[ERROR] Can not open database %s: %s' %(db_name, str(e)))
      status = 31
      return status, focuser_position_reference_flag_offset_and_usage_flag
   
   # Read focuser position for selected filter
   try:
      cursor.execute("SELECT focuser_position FROM filters_focuser_position WHERE filter_name = ?", (filter_name,))
      result = cursor.fetchone()
      if result:
         focuser_position_reference_flag_offset_and_usage_flag[0] = result[0]
      else:
         ccdciel('LogMsg','[ERROR] No focuser position for selected filter %s in database' %(filter_name))
         status_array[0] = 33

      cursor.execute("SELECT reference_flag FROM filters_focuser_position WHERE filter_name = ?", (filter_name,))
      result = cursor.fetchone()
      if result:
         focuser_position_reference_flag_offset_and_usage_flag[1] = result[0]
      else:
         ccdciel('LogMsg','[ERROR] No reference flag for selected filter %s in database' %(filter_name))
         status_array[1] = 34
      
      cursor.execute("SELECT offset_for_filter FROM filters_focuser_position WHERE filter_name = ?", (filter_name,))
      result = cursor.fetchone()
      if result:
         focuser_position_reference_flag_offset_and_usage_flag[2] = result[0]
         status = 0
      else:
         ccdciel('LogMsg','[ERROR] No focuser offset for selected filter %s in database' %(filter_name))
         status_array[2] = 35

      cursor.execute("SELECT usage_flag FROM filters_focuser_position WHERE filter_name = ?", (filter_name,))
      result = cursor.fetchone()
      if result:
         focuser_position_reference_flag_offset_and_usage_flag[3] = result[0]
         status = 0
      else:
         ccdciel('LogMsg','[WARNING] No usage flag for selected filter %s in database, mark filter as in use' %(filter_name))
         focuser_position_reference_flag_offset_and_usage_flag[3] = 1
         status = 0

      # Determine overall status
      if status_array[0] == 33 and status_array[1] == 34 and status_array[2] == 35:
         status = 32
      elif status_array[1] == 34 and status_array[2] == 35:
         status = 36
      elif status_array[0] == 33:
         status = 33
      elif status_array[1] == 34:
         status = 34
      elif status_array[2] == 35:
         status = 35
      else:
         status = 0

   except sqlite3.Error as e:
      ccdciel('LogMsg','[ERROR] Can not read focuser position for selected filter %s: %s' %(filter_name, str(e)))
      status = 32
   finally:
      conn.close()

   return status, focuser_position_reference_flag_offset_and_usage_flag

# store_position_per_filter_in_database - store information about filter and
#                                         caclulated focus point in database
# @arguments
# db_name - name of file with database
# db_directory - directory with database file
# filter_name - selected filter name
# focuser_position - focuser position
# reference_flag - reference flag for selected filter (0 - no, 1 - yes)
# offset_for_filter - offset for selected filter calculated from reference filter
# usage_flag - filter usage flag (0 - no, 1 - yes)
#
# @return status
# 0 - success
# 31 - can not open database
#
def store_position_per_filter_in_database(db_name, db_directory, filter_name, focuser_position, reference_flag, offset_for_filter, usage_flag):
   status = 0

   ccdciel('LogMsg','Save focuser position for \"%s\" filter in \"%s/%s\" database' %(filter_name, db_directory, db_name))

   try:
      # Open database connection
      conn = sqlite3.connect(os.path.join(db_directory, db_name))
      cursor = conn.cursor()

      # Create table if it does not exist
      cursor.execute('''CREATE TABLE IF NOT EXISTS filters_focuser_position (
                        filter_name TEXT PRIMARY KEY,
                        focuser_position INTEGER,
                        reference_flag INTEGER,
                        offset_for_filter INTEGER,
                        usage_flag INTEGER
                     )''')

      # Insert or update the filter name and focuser position
      cursor.execute('''INSERT INTO filters_focuser_position (filter_name, focuser_position, reference_flag, offset_for_filter, usage_flag)
                          VALUES (?, ?, ?, ?, ?)
                          ON CONFLICT(filter_name) DO UPDATE SET focuser_position=excluded.focuser_position,
                                                                 reference_flag=excluded.reference_flag,
                                                                 offset_for_filter=excluded.offset_for_filter,
                                                                 usage_flag=excluded.usage_flag''',
                       (filter_name, focuser_position, reference_flag, offset_for_filter, usage_flag))

      # Commit changes and close connection
      conn.commit()
      conn.close()
      ccdciel('LogMsg', 'Successfully stored \"%s\" filter focuser position in \"%s/%s\" database.' % (filter_name, db_directory, db_name))
   except sqlite3.Error as e:
      ccdciel('LogMsg', '[ERROR] Failed to store \"%s\" filter focuser position in database \"%s/%s\": %s' % (filter_name, db_directory, db_name, str(e)))
      status = 31

   return status

# set_focuser_position - set focuser position to selected value
# @arguments
# new_focuser_position - new focuser position
#
# @return status
# 0 - success
# 12 - can not set new focuser position
# 13 - can not return to intial focuser position
def set_focuser_position(new_focuser_position):
   status = 0 # Status of operation
   restore = 0 # Restore flag, 0 - normal operation, 1 - need to restore, 2 - in progress, 3 - can not restore
   max_time_array = [120,240] # max operation time [normal,restore]
   cur_max_time = [0,0] # current and max time
   foc_pos_array = [0,new_focuser_position,0] # focuser position array [initial,new,temporary]

   # Get the focuser position
   foc_pos_array[0] = ccdciel('FocuserPosition')['result']
   ccdciel('LogMsg','Initial focuser position is %d, target position is %d' %(foc_pos_array[0],foc_pos_array[1]))
   foc_pos_array[2] = foc_pos_array[0]

   # Set into new position
   while True:
      # Restore procedure
      if restore == 0:
         cur_max_time[1]=max_time_array[0] # Set max time for normal operation
      if restore == 1:
         cur_max_time[1]=max_time_array[1] # Set max time for restore operation
         cur_max_time[0]=0  # Clear timer
         foc_pos_array[1] = foc_pos_array[0] # Set target focus point as initial
         foc_pos_array[2] = ccdciel('FocuserPosition')['result'] # Get current focus point
         restore = 2 # Set restore flag to in progress
      if foc_pos_array[2] != foc_pos_array[1]:
         ccdciel('Focuser_setposition',foc_pos_array[1])
         foc_pos_array[2] = ccdciel('FocuserPosition')['result']
         while foc_pos_array[2] != foc_pos_array[1]:
            if cur_max_time[0] == cur_max_time[1]:
               if restore == 0:
                  ccdciel('LogMsg', '[ERROR] Focuser not set in position %d during %ds try to restore initial position!!!' %(foc_pos_array[1],cur_max_time[1]))
                  status = 12
                  restore = 1
                  break
               if restore == 2:
                  ccdciel('LogMsg', '[ERROR] Focuser can not restore focuser position %d during %ds something goes wrong!!!' %(foc_pos_array[0],cur_max_time[1]))
                  status = 13
                  restore = 3
                  break
            time.sleep(1)
            foc_pos_array[2] = ccdciel('FocuserPosition')['result']
            cur_max_time[0]=cur_max_time[0]+1
      # Check status after operation
      if status == 0 and restore == 0:
         foc_pos_array[2] = ccdciel('FocuserPosition')['result']
         ccdciel('LogMsg','Focuser after setting to %d position %d' %(foc_pos_array[1],foc_pos_array[2]))
         status = 0
         break
      if status == 12 and restore == 2:
         foc_pos_array[2] = ccdciel('FocuserPosition')['result']
         ccdciel('LogMsg','[ERROR] Focuser position not set to %d but restored to %d position is %d' %(new_focuser_position,foc_pos_array[1],foc_pos_array[2]))
         break
      if status == 13 and restore == 3:
         foc_pos_array[2] = ccdciel('FocuserPosition')['result']
         ccdciel('LogMsg','[CRITICAL ERROR] Focuser position not restored, position is %d' %(foc_pos_array[2]))
         exit(1)
   return status

# calculate_focuser_position - calculate focuser position for selected filter
#                              using autofocus tool and store in array
# @arguments
# filter_name - selected filter name
#
# @return status - status of operation
# 0 - success
# 22 - specified filter not found
# 23 - cannot set filter in filter wheel
# 24 - cannot restore filter in filter wheel (critical error)
# @return filter_index_and_name_focuser_position - array with filter index, name and focuser position
#
def calculate_focuser_position(filter_name):
   global filters_and_focuser_positions_database_file
   global filters_and_focuser_positions_database_directory
   global filters_subset
   global focus_type

   status = 0 # Status of operation
   restore = 0 # Restore flag, 0 - normal operation, 1 - need to restore, 2 - in progress, 3 - can not restore
   filter_index_and_name_focuser_position = [ 0, 'NONE', 0, 0, 0, 0 ] # array with filter index, name, focuser position, reference filter, offset and usage flag
   cur_init_fwheel_index = [0,0] # current and initial filter wheel index
   max_time_array = [30,60] # max operation time [normal,restore]
   cur_max_time = [0,0] # current and max time
   ccdciel('LogMsg','Selected filter name: %s' %(filter_name))
   
   # Looking for filter in filter wheel and display list of filters
   list_of_filters = (ccdciel('Wheel_GetfiltersName')['result'])
   for idf,f in enumerate(list_of_filters):
      if filter_name == f:
         filter_index_and_name_focuser_position[0] = idf+1
         filter_index_and_name_focuser_position[1] = f
         break
    
   if filter_index_and_name_focuser_position[1] != filter_name:
      ccdciel('LogMsg','[ERROR] Following filter %s not found: %s' % (filter_name,filter_index_and_name_focuser_position[1]))
      status = 22
      return status
       
   # Log found filter index and name
   ccdciel('LogMsg','Filter found index: %d name: %s' % (filter_index_and_name_focuser_position[0],filter_index_and_name_focuser_position[1]))

   # Select filter in wheel
   while True:
      if restore == 0:
         cur_max_time[1]=max_time_array[0] # Set max time for normal operation
         cur_max_time[0]=0  # Clear timer
      if restore == 1:
         cur_max_time[1]=max_time_array[1] # Set max time for restore operation
         cur_max_time[0]=0  # Clear timer
         restore = 2 # Set restore flag to in progress
      
      # Get current filter wheel position and set new filter wheel position
      cur_fwheel_dict = ccdciel('Wheel_getfilter')['result']
      cur_init_fwheel_index[0] = int(cur_fwheel_dict.get("status"))
      cur_init_fwheel_index[1] = cur_init_fwheel_index[0]
      if restore == 0:
         ccdciel('Wheel_setfilter',filter_index_and_name_focuser_position[0])
      if restore == 1:
         ccdciel('Wheel_setfilter',cur_init_fwheel_index[1])

      # Check filter wheel position
      while cur_init_fwheel_index[0] != filter_index_and_name_focuser_position[0]:
         if cur_max_time[0] == cur_max_time[1]:
            if restore == 0:
               ccdciel('LogMsg','[ERROR] Filter wheel not set to index: %d name: %s during %ds try to restore initial filter!!!' % (filter_index_and_name_focuser_position[0],filter_name,cur_max_time[1]))
               status = 23
               restore = 1
               break
            if restore == 2:
               ccdciel('LogMsg','[ERROR] Filter wheel can not restore filter index: %d name: %s during %ds something goes wrong!!!' % (cur_init_fwheel_index[1],list_of_filters[cur_init_fwheel_index[1]],cur_max_time[1]))
               status = 24
               restore = 3
               break
         time.sleep(1)
         ccdciel('LogMsg','[DEBUG] Step: %s' % (cur_max_time[0]))
         cur_fwheel_dict = ccdciel('Wheel_getfilter')['result']
         cur_init_fwheel_index[0] = int(cur_fwheel_dict.get("status"))
         ccdciel('LogMsg','[DEBUG] Step: %d filter %d expected filter %d' % (cur_max_time[0],cur_init_fwheel_index[0],filter_index_and_name_focuser_position[0]))
         cur_max_time[0]=cur_max_time[0]+1
      
      # Check status after operation
      if status == 0 and restore == 0:
         ccdciel('LogMsg','Filter wheel set to index: %d name: %s' % (filter_index_and_name_focuser_position[0],filter_name))
         break
      if status == 23 and restore == 2:
         ccdciel('LogMsg','[ERROR] Filter wheel not set to index: %d name: %s but restored to index: %d name: %s' % (filter_index_and_name_focuser_position[0],filter_name,cur_init_fwheel_index[1],list_of_filters[cur_init_fwheel_index[0]]))
         break
      if status == 24 and restore == 3:
         ccdciel('LogMsg','[CRITICAL ERROR] Filter wheel not restored, position is index: %d name: %s' % (cur_init_fwheel_index[0],list_of_filters[cur_init_fwheel_index[0]]))
         exit(1)

   # Get optimal position for filter from data base
   status, focuser_position_reference_flag_offset_and_usage_flag = get_focuser_position_for_filter_from_database(filters_and_focuser_positions_database_file,filters_and_focuser_positions_database_directory,filter_name)
   if status == 34 or status == 35 or status == 36 or status == 0:
      filter_index_and_name_focuser_position[2] = focuser_position_reference_flag_offset_and_usage_flag[0]
      ccdciel('LogMsg','Focuser position for filter %s read from database is %d' % (filter_name,filter_index_and_name_focuser_position[2]))
      set_focuser_position(filter_index_and_name_focuser_position[2])
      
      # Set reference filter and offset to 0 will be calculated after autofocus
      filter_index_and_name_focuser_position[3] = focuser_position_reference_flag_offset_and_usage_flag[1]
      filter_index_and_name_focuser_position[4] = 0
      filter_index_and_name_focuser_position[5] = focuser_position_reference_flag_offset_and_usage_flag[3]

      status = 0
   # Focuser position for selected filter not found in database
   else:
      ccdciel('LogMsg','[WARNING] Can not read focuser position for filter %s from database, script will use initial focuser position or current value' % (filter_name))
      if initial_focuser_position != 0:
         set_focuser_position(initial_focuser_position)
         ccdciel('LogMsg','Set initial focuser position to %d before autofocus' % (initial_focuser_position))
      else:
         cur_focuser_position = ccdciel('FocuserPosition')['result']
         if cur_focuser_position != 0:
            ccdciel('LogMsg','Use current focuser position before autofocus is %d' % (ccdciel('FocuserPosition')['result']))
         else:
            ccdciel('LogMsg','[CRITILAC ERROR] Focuser position for filter %s is set to 0, calculating using autofocus could be dangerous, set focuser manually near focus point and rerun script with parameter \"-f position\"' % (filter_name))
            exit(1)

   # Find filter on filters subset if subset is provided
   if len(filters_subset) > 0:
      filter_on_subset_list = 0
      for fs in filters_subset:
         if fs == filter_index_and_name_focuser_position[0]:
            filter_on_subset_list = 1
            break
      if filter_on_subset_list == 1 and filter_index_and_name_focuser_position[5] == 0:
         filter_index_and_name_focuser_position[5] = 1
         ccdciel('LogMsg','Filter %s index %d found in filters subset, mark filter as in use' % (filter_name,filter_index_and_name_focuser_position[0]))
      elif filter_on_subset_list == 0 and filter_index_and_name_focuser_position[5] == 1:
         filter_index_and_name_focuser_position[5] = 0
         ccdciel('LogMsg','Filter %s index %d not found in filters subset, mark filter as not in use' % (filter_name,filter_index_and_name_focuser_position[0]))
      
   # Calculate focuser position for selected filter using autofocus tool if filter is reference or usage flag is set to 1
   if filter_index_and_name_focuser_position[3] == 1 or filter_index_and_name_focuser_position[5] == 1:
      if filter_index_and_name_focuser_position[5] == 0:
         ccdciel('LogMsg','Calculate focuser position for selected filter %s, reference flag have priority over usage flag which set to 0' % (filter_name))
      if focus_type == 0:
         ccdciel('LogMsg','Calculate focuser position for selected filter using automatic autofocus tool')
         ccdciel('AutomaticAutofocus')
      elif focus_type == 1:
         ccdciel('LogMsg','Calculate focuser position for selected filter using autofocus tool')
         ccdciel('Autofocus')
      else:
         ccdciel('LogMsg','[CRITICAL ERROR] Unknown autofocus type %d' % (focus_type))
         exit(1)

      # Get calculated focuser position
      filter_index_and_name_focuser_position[2] = ccdciel('FocuserPosition')['result']
      ccdciel('LogMsg','Calculated focuser position for filter %s is %d' % (filter_name,filter_index_and_name_focuser_position[2]))

   else:
      ccdciel('LogMsg','Skip calculating focuser position for selected filter %s, usage flag is set to 0' % (filter_name))

   return status, filter_index_and_name_focuser_position

# select_filter_and_set_focuser_position - select filter in filter wheel and set focuser position from database
# @return status - status of operation
# 0 - success
# 15 - use current focuser position as initial position
def select_filter_and_set_focuser_position(db_name, db_directory, filter_name_and_index):
   status = 0 # Status of operation
   
   # Set filter in filter wheel
   ccdciel('Wheel_setfilter',filter_name_and_index[1])

   # Get current focuser position
   cur_focuser_position = ccdciel('FocuserPosition')['result']

   # Get focuser position for selected filter from database
   status, focuser_position_reference_flag_offset_and_usage_flag = get_focuser_position_for_filter_from_database(db_name, db_directory, filter_name_and_index[0])

   # Set focuser position for selected filter
   if status == 0 or status == 34 or status == 35 or status == 36:
      set_focuser_position(focuser_position_reference_flag_offset_and_usage_flag[0])
   else:
      ccdciel('LogMsg','[WARNING] Can not read focuser position for filter %s from database, script will use current focuser position %d' % (filter_name_and_index[0],cur_focuser_position))
      status = 15

   return status

# calculate_focuser_position_for_filter_wheel - calculate focuser position for used filter wheel
# @return status - status of operation
# 0 - success
def calculate_focuser_position_for_filter_wheel():
   global filter_name_to_set

   status = 0 # Status of operation
   focuser_position_per_filter = [ ] # array with focuser position per filter
   reference_filter_id = 0 # Reference filter id
   
   # Get reference filter from parameters if provided
   get_reference_filter_from_application_arguments()
   if filter_name_to_set[2] != None and filter_name_to_set[3] != None:
      reference_filter_id = filter_name_to_set[3]
      ccdciel('LogMsg','Reference filter provided by parameters name: %s position: %d' % (filter_name_to_set[2],filter_name_to_set[3]))
   
   # Get list of filters in filter wheel
   list_of_filters = (ccdciel('Wheel_GetfiltersName')['result'])

   # Reset offset for each filter in filters wheel
   if check_for_version_neq_0_9_92_3829(0) == 1:
      for idf,f in enumerate(list_of_filters):
         ccdciel('Set_FilterOffset',[f,0])

   # Calculate focuser position for each filter
   for idf,f in enumerate(list_of_filters):
      status, filter_and_focuser_position = calculate_focuser_position(f)
      if status == 0:
         # Reference filter id handling
         if (idf+1) == reference_filter_id:
            filter_and_focuser_position[3] = 1
         elif filter_and_focuser_position[3] == 1 and reference_filter_id == 0:
            reference_filter_id = idf+1
            ccdciel('LogMsg','Reference filter found index: %d name: %s' % (filter_and_focuser_position[0],filter_and_focuser_position[1]))
         elif filter_and_focuser_position[3] == 1:
            filter_and_focuser_position[3] = 0
            ccdciel('LogMsg','[WARNING] Multiple reference filters found reference flag will be removed, current index: %d name: %s index: %d' % (filter_and_focuser_position[0],filter_and_focuser_position[1],reference_filter_id))
         # Store calculated focuser position for filter in array
         focuser_position_per_filter.append(filter_and_focuser_position)
      else:
         filter_index_and_name_focuser_position = [ idf+1, f, ccdciel('FocuserPosition')['result'], 0, 0, 1 ] # array with filter index, name, focuser position, reference filter, offset and usage flag
         focuser_position_per_filter.append(filter_index_and_name_focuser_position)
         ccdciel('LogMsg','[ERROR] Can not calculate focuser position for filter %s' % (f))
   
   # Set filters wheel in reference filter position
   if reference_filter_id != 0:
      ccdciel('Wheel_setfilter',reference_filter_id)
      ccdciel('LogMsg','Filter wheel set to reference filter index: %d name: %s' % (reference_filter_id,(ccdciel('Wheel_GetfiltersName')['result'])[reference_filter_id-1]))

   # Calculate offset for each filter based on reference filter
   if(reference_filter_id != 0):
      filter_name_to_set[0] = (ccdciel('Wheel_GetfiltersName')['result'])[reference_filter_id-1]
      filter_name_to_set[1] = reference_filter_id
   for idf,f in enumerate(list_of_filters):
      focuser_position_per_filter[idf][4] = focuser_position_per_filter[idf][2] - focuser_position_per_filter[reference_filter_id-1][2]
      if check_for_version_neq_0_9_92_3829(0) == 1:
         ccdciel('Set_FilterOffset',[focuser_position_per_filter[idf][1],focuser_position_per_filter[idf][4]])
         ccdciel('LogMsg','Filter index: %d name: %s offset: %d' % (focuser_position_per_filter[idf][0],focuser_position_per_filter[idf][1],focuser_position_per_filter[idf][4]))

   # Store calculated focuser position for each filter in database
   for item in focuser_position_per_filter:
      status = store_position_per_filter_in_database(filters_and_focuser_positions_database_file,filters_and_focuser_positions_database_directory,item[1],item[2],item[3],item[4],item[5])
      if status != 0:
         ccdciel('LogMsg','[ERROR] Can not store focuser position %d for filter %d:%s in database' % (item[2], item[0], item[1]))
      else:
         ccdciel('LogMsg','Filter index: %d name: %s focuser position: %d' % (item[0], item[1], item[2]))

   # Switch to initial filter in filter wheel and set focuser position
   status = select_filter_and_set_focuser_position(filters_and_focuser_positions_database_file,filters_and_focuser_positions_database_directory, filter_name_to_set)

   return status

# read_focuser_position_for_filter - read focuser position for selected filter from database and set focuser position
# @return status - status of operation
# 0 - success
def read_focuser_position_for_filters():
   global filter_name_to_set
   status = 0 # Status of operation

   # Get reference filter from parameters if provided
   get_reference_filter_from_application_arguments()

   # Get list of filters in filter wheel
   list_of_filters = (ccdciel('Wheel_GetfiltersName')['result'])
   filters_configured_in_database = []
            
   # Get focuser position for filters from database
   for idf,f in enumerate(list_of_filters):
      status, focuser_position_reference_flag_offset_and_usage_flag = get_focuser_position_for_filter_from_database(filters_and_focuser_positions_database_file,filters_and_focuser_positions_database_directory,f)
      if status == 0:
         ccdciel('LogMsg','Filter %s configuration in database -> focuser position: %d reference flag: %d offset: %d' % (f,focuser_position_reference_flag_offset_and_usage_flag[0],focuser_position_reference_flag_offset_and_usage_flag[1],focuser_position_reference_flag_offset_and_usage_flag[2]))
         filters_configured_in_database.append(focuser_position_reference_flag_offset_and_usage_flag)
         if focuser_position_reference_flag_offset_and_usage_flag[1] == 1:
            if filter_name_to_set[2] == None and filter_name_to_set[3] == None:
               filter_name_to_set[0] = f
               filter_name_to_set[1] = idf+1
            else:
               ccdciel('LogMsg','[WARNING] Use filter provided by user %d:%s as reference over reference filter stored in database: %s' % (filter_name_to_set[3], filter_name_to_set[2], f))
      else:
         ccdciel('LogMsg','[CRITICAL ERROR] Can not read focuser position for filter %s from database' % (f))
         exit(1)

   # Reset offset for each filter in filters wheel
   if check_for_version_neq_0_9_92_3829(0) == 1:
      for idf,f in enumerate(list_of_filters):
         ccdciel('Set_FilterOffset',[f,0])

   # Apply configuration for selected filter
   status = select_filter_and_set_focuser_position(filters_and_focuser_positions_database_file,filters_and_focuser_positions_database_directory, filter_name_to_set)

   # Set offset for each filter in filters wheel
   if check_for_version_neq_0_9_92_3829(0) == 1:
      # Recalculate offsets
      if filter_name_to_set[2] == filter_name_to_set[0]:
         # Get current focuser position
         cur_focuser_position = ccdciel('FocuserPosition')['result']
         # Calculate and set offsets
         for idf,f in enumerate(list_of_filters):
            filter_offset = filters_configured_in_database[idf][0]-cur_focuser_position
            ccdciel('Set_FilterOffset',[f,filter_offset])
            ccdciel('LogMsg','Filter index: %d name: %s calculated offset: %d' % (idf+1,f,filter_offset))
      else:
         # Set offset from database
         for idf,f in enumerate(list_of_filters):
            ccdciel('Set_FilterOffset',[f,filters_configured_in_database[idf][2]])
            ccdciel('LogMsg','Filter index: %d name: %s offset: %d' % (idf+1,f,filters_configured_in_database[idf][2]))

   return status   

# ---------------------------------------------------------------------------- #
# --------------- MAIN - FOCUSER POSITION PER FILTER - MAIN ------------------ #
# ---------------------------------------------------------------------------- #

# Parse arguments from command line
arguments_parser()

ccdciel('LogMsg','[INFO] This script path %s' % (this_script_path))
ccdciel('LogMsg','[INFO] This script directory %s' % (this_script_dir))
ccdciel('LogMsg','[INFO] Database name %s' % (filters_and_focuser_positions_database_file))
ccdciel('LogMsg','[INFO] Initial focuser position %d' % (initial_focuser_position))

# Check necessary components are connected
check_necessary_components()

# Run script in selected working mode CALCULATE (0) - default or READ (1) or RESET (2)
if script_working_mode == 1:
   ccdciel('LogMsg','[INFO] Script working mode: READ focuser position for selected filter from database')
   read_focuser_position_for_filters()
elif script_working_mode == 2:
   ccdciel('LogMsg','[INFO] Script working mode: RESET focuser positions and offsets for all filters')
   reset_focuser_positions_and_offsets()
else:
   ccdciel('LogMsg','[INFO] Script working mode: CALCULATE focuser position for filter wheel')
   calculate_focuser_position_for_filter_wheel()

# ---------------------------------------------------------------------------- #
