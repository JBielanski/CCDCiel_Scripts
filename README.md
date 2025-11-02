# CCDCiel_Scripts
Repository contains the CCDCiel python scripts for making easier some complex operations.

# focuser_position_per_filter
(C) Jan Bielanski 2025

Script to manage focuser position per filter
- calculate focuser position for selected filter using autofocus tool
- store information about filter and calculated focus point in database
- read and set focuser position from/to database
- work in three modes:
   - 'CALCULATE' [default] calculate focuser position for all filters in filter wheel and store in database
   - 'READ'      read configuration for focuser and filters from database
   - 'RESET'     reset focuser position to 0, set first filter in filters wheel, reomove all offsets for filters

Requirements:
## Supports for OFFSETS in scripts is new in CCDCiel and needs:
## CCDCiel 0.9.92-3829 or newer: https://vega.ap-i.net/pub/ccdciel/daily_build/

Script use the CCDciel JSON-RPC interface.
For more information and reference of the available methods see: 
https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference

 Script usage, scenarios:
1) First usage
- set manually focuser in position near focuse point
- run script with parameters:
--> "-f <position>" - provide position near focus point
--> "-d <name>" - name of database, default "focuser_position_per_filter.db"

2) Usage when database has been created:
- run script with parameters:
--> "-d <name>" - name of database if you provide own name, default "focuser_position_per_filter.db"

3) Read data from database without running autofocus
- run script with parameters:
--> "-m READ" - script will read data from database
--> "-d <name>" - name of database if you provide own name, default "focuser_position_per_filter.db"

4) Reset focuser and filter wheel data, useful at the end off session
- run script with parameters:
--> "-m RESET"

5) Display help
- run script with parameters:
--> "--help"

 List of changes:
# [26-10-2025] Initial version
 - calculate focuser position for selected filter using autofocus tool
 - store information about filter and calculated focus point in database
# [28-10-2025]
 - script remember filter which was set before script has been started
 - script try to use current focuser position to initial for autofocus if:
 -- can not read position from database
 -- focuser position send as parameter to script is 0
 - script exit if focuser position is 0 and ask to set it manually
 - script at the end return to filter which was set before script has 
   been started and set focuser position to calculated value for this filter
# [29-10-2025]
 - added reference filter and offset for each filter in database
 - move to reference filter after calculate focuser position for all filters in filters wheel
# [01-11-2025]
 - added working modes: CALCULATE (default) and READ
 - added command line arguments parser
# [02-11-2025]
 - added RESET working mode to reset focuser positions and offsets for all filters
 - added check for sqlite3 module
