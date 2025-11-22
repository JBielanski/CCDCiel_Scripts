# CCDCiel_Scripts
Repository contains the CCDCiel python scripts for making easier some complex operations.
https://github.com/JBielanski/CCDCiel_Scripts

## List of scripts:
- `focuser_position_per_filter` - setting focuser position per filter and store them in database
Additional simple scripts:
- `log_filterwheel_position` - simple script which log filter wheel position
- `log_focuser_position` - simple script which log focuser position
- `camera_warm_up` - simple script for warm up camera
Following scripts needs INDI and thera are dedicated to specific equipments:
- `end_session_indi` - script finish session:
                        set filter wheel on first position and reset all offsets
                        set focuser on position ZERO
                        set iEQ (iOptron CEM-60-EC) in ZERO position (use INDI commands: iEQ)
- `i`EQ_scope_go_home_indi` - set iEQ (iOptron CEM-60-EC) in ZERO position (use INDI commands: iEQ)
- `pegasus_SPB_set_dews_AB_to_zero_indi` - set dews ports A and B to ZERO for Pegasus Astro Saddle PowerBox (use INDI commands: pegasus_SPB)

## Compilation

- By `Makefile`:

   `make all` - build and install `focuser_position_per_filter`

   `make additional` - build and install additional scripts: `log_filterwheel_position`, `log_focuser_position`, `camera_warm_up`

   `make additional_indi` - build and install additional scripts with INDI dependency: `end_session_indi`, `iEQ_scope_go_home_indi`, `pegasus_SPB_set_dews_AB_to_zero_indi`
   
   `make clean` - remove compiled files

- By `install_script_windows.bat`:

   `.\install_script_windows.bat` - install `focuser_position_per_filter`

- Simple installation:

   rename `*.py` to `*.script` and put into CCDCiel directory

Note:

   CCDCiel do not support compiled Python `*.pyc` files, compilation is useful for checking problem in scripts after any modification.
   Into CCDCiel directory should be put files with `*.script` extension.

# `focuser_position_per_filter`

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the top-level `LICENSE` file for the full license text.

Copyright (c) 2025 Jan Bielanski

Script to manage focuser position per filter
- calculate focuser position for selected filter using autofocus tool
- store information about filter and calculated focus point in database
- read and set focuser position from/to database
- work in three modes:
   - 'CALCULATE' [DEFAULT] calculate focuser position for all filters in filter wheel and store in database
   - 'READ'      read configuration for focuser and filters from database
   - 'RESET'     reset focuser position to 0, set first filter in filters wheel, reomove all offsets for filters
- allow to select focus method:
   - 'AUTO' [DEFAULT] can move to focus star
   - 'INPLACE' perform autofocus in current position
- allow to provide reference/current filter name (for CCDCiel older than 0.9.92-3829) as parameter
- allow to select subsets of filters for session

Requirements:
## Supports for OFFSETS in scripts is new in CCDCiel and needs:
## CCDCiel 0.9.92-3829 or newer: https://vega.ap-i.net/pub/ccdciel/daily_build/
## For older vesion script works differently for READ mode and disable all operation in script which try to modify offsets in CCDCiel

Script use the CCDciel JSON-RPC interface.
For more information and reference of the available methods see: 
https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference

 Script usage, scenarios:
1) First usage
- set manually focuser in position near focuse point
- run script with parameters:

--> "-m CALCULATE" - [OPTIONAL] calculate is default mode

--> "-f <position>" - [OBLIGATORY] provide position near focus point

--> "-n <filter name>" OR "-i <filter index>" - [OBLIGATORY] to set reference filter

--> -s <list of filters IDs> - [OPTIONAL] run autofocus for selected filters, provide list as array like: [1,3,4,5] (*) 

--> "-d <name>" - [OPTIONAL] name of database, default "focuser_position_per_filter.db"

--> "-t <autofocus type>" - [OPTIONAL] set autofocus method AUTO or INPLACE, AUTO is default and could move telescope to focus star 

2) Usage when database has been created:
- run script with parameters:

--> "-m CALCULATE" - [OPTIONAL] calculate is default mode

--> "-d <name>" - [OBLIGATORY/OPTIONAL] name of database if you provide own name, default "focuser_position_per_filter.db"

--> "-t <autofocus type>" - [OPTIONAL] set autofocus method AUTO or INPLACE, AUTO is default and could move telescope to focus star

--> "-n <filter name>" OR "-i <filter index>" - [OPTIONAL] to change reference filter, if not provided used reference filter from database

--> -s <list of filters IDs> - [OPTIONAL] run autofocus for selected filters, provide list as array like: [1,3,4,5] (*) 

3) Read data from database without running autofocus
- run script with parameters:

--> "-m READ" - [OBLIGATORY] script will read data from database

--> "-d <name>" - [OBLIGATORY/OPTIONAL] name of database if you provide own name, default "focuser_position_per_filter.db"

--> "-n <filter name>" - [OBLIGATORY/OPTIONAL] set reference filter optional for new CCDCiel, for CCDCiel older than 0.9.92-3829 set current filter and read position, so parameter is obligatory

4) Reset focuser and filter wheel data, useful at the end off session
- run script with parameters:

--> "-m RESET" - [OBLIGATORY] reset configuration in CCDCiel (Remove all offsets / set filter wheel on FIRST position / set focuser on ZERO position)

5) Display help
- run script with parameters:

--> "--help" - display help

(*) for calculation will be used filters with index 1,3,4 and 5 if they are in filters wheel others filters will be marked as not in use.


## List of changes:

### [26-10-2025] Initial version
 - calculate focuser position for selected filter using autofocus tool
 - store information about filter and calculated focus point in database
### [28-10-2025]
 - script remember filter which was set before script has been started
 - script try to use current focuser position to initial for autofocus if:
 -- can not read position from database
 -- focuser position send as parameter to script is 0
 - script exit if focuser position is 0 and ask to set it manually
 - script at the end return to filter which was set before script has 
   been started and set focuser position to calculated value for this filter
### [29-10-2025]
 - added reference filter and offset for each filter in database
 - move to reference filter after calculate focuser position for all filters in filters wheel
### [01-11-2025]
 - added working modes: CALCULATE (default) and READ
 - added command line arguments parser
### [02-11-2025]
 - added RESET working mode to reset focuser positions and offsets for all filters
 - added check for sqlite3 module
### [07-11-2025]
 - support recognize CCDCiel version in script
 - disable setting OFFSET for CCDCiel older than 0.9.92.3829
 - added option which allow to provide reference filter: --filtername, -n <filter name>
 - added selection between AutomaticAutofocus and Autofocus by: --focustype, -t <autofocus type: AUTO, INPLACE>
### [09-11-2025]
- added filter usage flag in database, allow to reduce filters for which will autofocus to selected subset: SELECTED FILTERS + REFERENCE FILTER
- for other filters only offset will be recalculated
- release under GPL-3.0 license
### [12-11-2025]
- added command line argument to select filters subset: --subset, -s <list of filter indexes>
### [14-11-2025]
- added selection of reference filter by ID --filterid, -i <filter index>
- selection reference filter by name and index can not be use together, use: --filtername, -n <filter name> OR --filterid, -i <filter index>
### [15-11-2025]
- RESET - remove all offsets, set filter wheel on FIRST position, set focuser on ZERO position

# `camera_warm_up`

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the top-level `LICENSE` file for the full license text.

Copyright (c) 2025 Jan Bielanski

Script to manage focuser position per filter
 - warm up the camera to constant 20C

## List of changes:
### [21-11-2025] Initial version, simple camera warm up script to 20C

# `log_focuser_position`

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the top-level `LICENSE` file for the full license text.

Copyright (c) 2025 Jan Bielanski

Script for log focuser position

## List of changes:
### [22-11-2025] Log focuser current position

# `log_filters_wheel_position`

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the top-level `LICENSE` file for the full license text.

Copyright (c) 2025 Jan Bielanski

Script for log filters wheel current position

## List of changes:
### [22-11-2025] Log filters wheel current position

# `end_session_indi`

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the top-level `LICENSE` file for the full license text.

Copyright (c) 2025 Jan Bielanski

Script finish the session, it's dedicated for setups with INDI server
controlling mount (iOptron CEM-60-EC), focuser and filter wheel.
The script will do the following operations:
   - set filter wheel on first position and reset all offsets
   - set focuser on position ZERO
   - set iEQ (iOptron CEM-60-EC) in ZERO position (use INDI commands: iEQ)

Script needs installed pyindi_client
`sudo apt-get install swig libz3-dev libcfitsio-dev libnova-dev`
`pip3 install --user --break-system-packages pyindi-client`

## List of changes:
### [22-11-2025] Working version

# `iEQ_scope_go_home_indi`

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the top-level `LICENSE` file for the full license text.

Copyright (c) 2025 Jan Bielanski

This script setting in HOME POSITION the telescope mount.
Beware the action is immediate and without confirmation message!
The script is dedicated for setups with INDI server controlling iOptron CEM-60-EC mount.

Script needs installed pyindi_client
`sudo apt-get install swig libz3-dev libcfitsio-dev libnova-dev`
`pip3 install --user --break-system-packages pyindi-client`

## List of changes:
### [22-11-2025] Working version

# `pegasus_SPB_set_dews_AB_to_zero_indi`

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
See the top-level `LICENSE` file for the full license text.

Copyright (c) 2025 Jan Bielanski

This script setting dews power to manual and zero values for A and B port in Pegasus Astro Saddle Power Box.
Beware the action is immediate and without confirmation message!
The script is dedicated for setups with INDI server controlling Pegasus Astro Saddle Power Box.

Script needs installed pyindi_client
`sudo apt-get install swig libz3-dev libcfitsio-dev libnova-dev`
`pip3 install --user --break-system-packages pyindi-client`

## List of changes:
### [22-11-2025] Initial working version