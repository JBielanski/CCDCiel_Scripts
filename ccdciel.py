"""
ccdciel.py
SPDX-FileCopyrightText: 2026 Jan Bielanski
SPDX-License-Identifier: GPL-3.0-or-later
https://github.com/JBielanski/CCDCiel_Scripts

Mock of CCDciel JSON-RPC interface used for local testing.

Implements most methods from the CCDciel JSON-RPC reference documentation:
- Methods that return a value (query/status)
- Methods that invoke command without parameter (actions)
- Methods that invoke command with parameter (parameterized actions)
- Status method for comprehensive device information

The mock keeps persistent internal state for all devices and can be
reset/modified for testing purposes.

Documentation: https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference
"""

from typing import Any, Dict, List, Union
import copy
from datetime import datetime

# Internal mock state - comprehensive device and system state
_state = {
    # Devices connection
    "devices_connected": True,
    "camera_connected": True,
    "telescope_connected": True,
    "dome_connected": True,
    "focuser_connected": True,
    "wheel_connected": True,
    "rotator_connected": True,
    "autoguider_connected": True,
    "planetarium_connected": False,

    # Camera settings
    "ccd_temperature": 20.0,
    "camera_frame": [0, 0, 1280, 1024],  # [x, y, width, height]
    "camera_binning": "1x1",
    "cooler_enabled": False,

    # Preview settings
    "preview_exposure": 1.0,
    "preview_binning": "1x1",
    "preview_running": False,
    "preview_loop_running": False,

    # Capture settings
    "capture_exposure": 5.0,
    "capture_binning": "1x1",
    "capture_object_name": "Object",
    "capture_count": 10,
    "capture_frametype": "Light",
    "capture_dither": 0,
    "capture_running": False,
    "capture_last_filename": "/tmp/capture_001.fits",

    # Telescope state
    "telescope_ra": 12.5,  # hours
    "telescope_de": 45.0,  # degrees
    "telescope_parked": False,
    "telescope_tracking": True,
    "telescope_tracking_rate": "SIDEREAL",
    "telescope_pier_side": "pierEast",
    "telescope_slewing": False,

    # Focuser
    "focuser_position": 0,
    "focuser_temperature": 15.0,
    "focuser_message": "Ready",

    # Filter wheel
    "filters": ["L", "R", "G", "B", "Ha"],
    "wheel_index": 0,

    # Rotator
    "rotator_angle": 0.0,

    # Dome
    "dome_parked": False,
    "dome_shutter_open": False,
    "dome_slaved": False,

    # Autoguider
    "autoguider_running": False,
    "autoguider_guiding": False,
    "autoguider_lockposition": [640, 512],  # [x, y]

    # System info
    "logs": [],
    "custom_headers": {},

    # Observatory location
    "obs_latitude": 50.0,
    "obs_longitude": 10.0,
    "obs_elevation": 300.0,

    # Calibrator
    "calibrator_brightness": 0,

    # Astrometry
    "astrometry_goto_running": False,
    "astrometry_goto_result": False,
}


def _result(value: Any) -> Dict[str, Any]:
    """Return a JSON-RPC like result container for compatibility."""
    return {"result": copy.deepcopy(value)}

def _status(status: str) -> Dict[str, Any]:
    """Return an action status response."""
    return {"result": {"status": status}}

def ccdciel(method: str, *params) -> Dict[str, Any]:
    """Main entry point. Implements CCDciel JSON-RPC interface.

    Supports all three method categories from CCDciel JSON-RPC reference:
    - Query methods (return values)
    - Action methods without parameters
    - Action methods with parameters

    Examples:
      ccdciel('Focuser_connected')
      ccdciel('FocuserPosition')
      ccdciel('Focuser_setposition', 100)
      ccdciel('Telescope_slew', 12.5, 45.0)
      ccdciel('status', ['camera', 'focuser'])
    """
    m = method.lower()

    # Normalize method names: handle both "TelescopeRA" and "Telescope_RA" formats
    m_normalized = m.replace('_', '')

    # Helper function for case-insensitive method matching
    def matches(method_str: str) -> bool:
        """Check if method matches (handles underscore variations)."""
        return m == method_str or m_normalized == method_str.lower().replace('_', '')

    # ============================================================================
    # QUERY METHODS - Methods that return a value
    # ============================================================================

    # Version and Device Info
    if matches('ccdciel_version'):
        return _result(["0.9.93", "3961", "0.9.93_3961"])

    if matches('devices'):
        return _result({
            "camera": "Fake Camera",
            "telescope": "Fake Telescope",
            "focuser": "Fake Focuser",
            "wheel": "Fake Wheel",
            "rotator": "Fake Rotator",
            "dome": "Fake Dome",
            "autoguider": "Fake Guider"
        })

    # Device Connection Status
    if matches('devices_connected'):
        return _result(_state["devices_connected"])
    if matches('camera_connected'):
        return _result(_state["camera_connected"])
    if matches('telescope_connected'):
        return _result(_state["telescope_connected"])
    if matches('dome_connected'):
        return _result(_state["dome_connected"])
    if matches('focuser_connected'):
        return _result(_state["focuser_connected"])
    if matches('wheel_connected'):
        return _result(_state["wheel_connected"])
    if matches('rotator_connected'):
        return _result(_state["rotator_connected"])
    if matches('autoguider_connected'):
        return _result(_state["autoguider_connected"])
    if matches('planetarium_connected'):
        return _result(_state["planetarium_connected"])

    # Camera Information
    if matches('camera_getframe'):
        return _result(_state["camera_frame"])
    if matches('ccdtemp'):
        return _result(round(_state["ccd_temperature"], 1))

    # Preview Status
    if matches('preview_getexposure'):
        return _result(_state["preview_exposure"])
    if matches('preview_getbinning'):
        return _result(_state["preview_binning"])
    if matches('preview_running'):
        return _result(_state["preview_running"])
    if matches('preview_loop_running'):
        return _result(_state["preview_loop_running"])

    # Capture Status
    if matches('capture_getexposure'):
        return _result(_state["capture_exposure"])
    if matches('capture_getbinning'):
        return _result(_state["capture_binning"])
    if matches('capture_getobjectname'):
        return _result(_state["capture_object_name"])
    if matches('capture_getcount'):
        return _result(_state["capture_count"])
    if matches('capture_getframetype'):
        return _result(_state["capture_frametype"])
    if matches('capture_getdither'):
        return _result(_state["capture_dither"])
    if matches('capture_running'):
        return _result(_state["capture_running"])
    if matches('capture_getlastfilename'):
        return _result(_state["capture_last_filename"])

    # Telescope Status and Position
    if matches('telescope_ra') or matches('telescopera'):
        return _result(round(_state["telescope_ra"], 6))
    if matches('telescope_de') or matches('telescopede'):
        return _result(round(_state["telescope_de"], 6))
    if matches('telescope_parked'):
        return _result(_state["telescope_parked"])
    if matches('telescope_tracking'):
        return _result(_state["telescope_tracking"])
    if matches('telescope_trackingrate'):
        return _result(_state["telescope_tracking_rate"])
    if matches('telescope_pierside'):
        return _result(_state["telescope_pier_side"])
    if matches('telescope_slewing'):
        return _result(_state["telescope_slewing"])

    # Focuser Status and Position
    if matches('focuserposition'):
        return _result(int(_state["focuser_position"]))

    # Filter Wheel
    if matches('wheel_getfiltersname'):
        return _result(list(_state["filters"]))
    if matches('wheel_getposition'):
        return _result(int(_state["wheel_index"]))
    if matches('wheel_getfilter'):
        # Returns current filter position as a dict with "status" key
        # Status is 1-indexed (1-based position)
        return _result({"status": int(_state["wheel_index"] + 1)})

    # Rotator
    if matches('rotator_angle'):
        return _result(round(_state["rotator_angle"], 2))

    # Dome
    if matches('dome_parked'):
        return _result(_state["dome_parked"])
    if matches('dome_opened'):
        return _result(_state["dome_shutter_open"])
    if matches('dome_slaved'):
        return _result(_state["dome_slaved"])

    # Autoguider Status
    if matches('autoguider_running'):
        return _result(_state["autoguider_running"])
    if matches('autoguider_guiding'):
        return _result(_state["autoguider_guiding"])
    if matches('autoguider_getlockposition'):
        return _result(_state["autoguider_lockposition"])

    # Astrometry
    if matches('astrometry_goto_running'):
        return _result(_state["astrometry_goto_running"])
    if matches('astrometry_goto_result'):
        return _result(_state["astrometry_goto_result"])

    # System Information
    if matches('timenow'):
        return _result(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if matches('siderealtime'):
        return _result(round(10.5, 6))
    if matches('obs_latitude'):
        return _result(_state["obs_latitude"])
    if matches('obs_longitude'):
        return _result(_state["obs_longitude"])
    if matches('obs_elevation'):
        return _result(_state["obs_elevation"])
    if matches('hostos'):
        import platform
        return _result(platform.system())
    if matches('directoryseparator'):
        import os
        return _result(os.sep)
    if matches('appdir'):
        return _result("/usr/share/ccdciel")
    if matches('tmpdir'):
        return _result("/tmp")
    if matches('capturedir'):
        return _result("/home/user/Pictures/ccdciel")
    if matches('calibratorbrightness'):
        return _result(_state["calibrator_brightness"])
    if matches('coverstatus'):
        return _result("open")

    # Custom Headers
    if matches('customheader'):
        if params:
            key = str(params[0])
            return _result(_state["custom_headers"].get(key, ""))
        return _result(_state["custom_headers"])
    if matches('currentheader'):
        return _result({
            "SIMPLE": "T",
            "BITPIX": 16,
            "NAXIS": 2,
            "NAXIS1": 1280,
            "NAXIS2": 1024,
            "TELESCOP": "Fake Telescope",
            "INSTRUME": "Fake Camera"
        })

    # ============================================================================
    # ACTION METHODS - Methods that invoke a command without parameter
    # ============================================================================

    if matches('camera_resetframe'):
        _state["camera_frame"] = [0, 0, 1280, 1024]
        return _status("OK!")

    if matches('preview_single'):
        if not _state["camera_connected"]:
            return _status("Failed! Camera not connected")
        _state["preview_running"] = True
        _state["preview_running"] = False
        return _status("OK!")

    if matches('preview_loop'):
        if not _state["camera_connected"]:
            return _status("Failed! Camera not connected")
        _state["preview_loop_running"] = True
        return _status("OK!")

    if matches('preview_stop'):
        _state["preview_running"] = False
        _state["preview_loop_running"] = False
        return _status("OK!")

    if matches('capture_start'):
        if not _state["camera_connected"]:
            return _status("Failed! Camera not connected")
        _state["capture_running"] = True
        _state["capture_running"] = False
        _state["capture_last_filename"] = "/tmp/capture_mock.fits"
        return _status("OK!")

    if matches('capture_stop'):
        _state["capture_running"] = False
        return _status("OK!")

    if matches('telescope_track'):
        if not _state["telescope_connected"]:
            return _status("Failed! Telescope not connected")
        _state["telescope_tracking"] = True
        return _status("OK!")

    if matches('telescope_abortmotion'):
        _state["telescope_slewing"] = False
        return _status("OK!")

    if matches('autofocus'):
        if not _state["focuser_connected"]:
            return _status("Failed! Focuser not connected")
        _state["focuser_position"] = _state["focuser_position"] + 10
        _state["focuser_message"] = "AutoFocus successful; HFD=4.2"
        return _status("OK!")

    if matches('automaticautofocus'):
        if not _state["focuser_connected"]:
            return _status("Failed! Focuser not connected")
        _state["focuser_position"] = _state["focuser_position"] + 15
        _state["focuser_message"] = "AutomaticAutoFocus successful; HFD=3.8"
        return _status("OK!")

    if matches('autoguider_connect'):
        _state["autoguider_connected"] = True
        return _status("OK!")

    if matches('autoguider_calibrate'):
        if not _state["autoguider_connected"]:
            return _status("Failed! Autoguider not connected")
        return _status("OK!")

    if matches('autoguider_startguiding'):
        if not _state["autoguider_connected"]:
            return _status("Failed! Autoguider not connected")
        _state["autoguider_running"] = True
        _state["autoguider_guiding"] = True
        return _status("OK!")

    if matches('autoguider_stopguiding'):
        _state["autoguider_running"] = False
        _state["autoguider_guiding"] = False
        return _status("OK!")

    if matches('autoguider_pause'):
        _state["autoguider_guiding"] = False
        return _status("OK!")

    if matches('autoguider_unpause'):
        if _state["autoguider_running"]:
            _state["autoguider_guiding"] = True
        return _status("OK!")

    if matches('autoguider_dither'):
        if not _state["autoguider_guiding"]:
            return _status("Failed! Autoguider not guiding")
        _state["autoguider_lockposition"][0] += 5
        _state["autoguider_lockposition"][1] += 5
        return _status("OK!")

    if matches('dome_park'):
        _state["dome_parked"] = True
        return _status("OK!")

    if matches('dome_open'):
        _state["dome_shutter_open"] = True
        return _status("OK!")

    if matches('dome_close'):
        _state["dome_shutter_open"] = False
        return _status("OK!")

    if matches('astrometry_solve'):
        return _status("OK!")

    if matches('astrometry_sync'):
        return _status("OK!")

    if matches('eqmod_clearpoints'):
        return _status("OK!")

    if matches('program_shutdown'):
        return _status("OK!")

    if matches('customheader_clear'):
        _state["custom_headers"].clear()
        return _status("OK!")

    if matches('finder_stoploop'):
        return _status("OK!")

    if matches('calibrator_light_off'):
        _state["calibrator_brightness"] = 0
        return _status("OK!")

    # ============================================================================
    # PARAMETERIZED ACTION METHODS - Methods with parameters
    # ============================================================================

    if matches('devices_connection'):
        if not params:
            raise TypeError('Devices_connection expects a boolean parameter')
        connect = bool(params[0])
        _state["devices_connected"] = connect
        return _status("OK!")

    if matches('ccd_settemperature'):
        if not params:
            raise TypeError('Ccd_settemperature expects a temperature value')
        temp = float(params[0])
        _state["ccd_temperature"] = temp
        _state["cooler_enabled"] = temp < 15
        return _status("OK!")

    if matches('camera_setframe'):
        if not params:
            raise TypeError('Camera_Setframe expects [x,y,width,height]')
        frame = list(params[0]) if isinstance(params[0], (list, tuple)) else list(params[:4])
        if len(frame) != 4:
            raise ValueError("Frame must have 4 elements")
        _state["camera_frame"] = [int(v) for v in frame]
        return _status("OK!")

    if matches('preview_setexposure'):
        if not params:
            raise TypeError('Preview_setexposure expects exposure time')
        _state["preview_exposure"] = float(params[0])
        return _status("OK!")

    if matches('preview_setbinning'):
        if not params:
            raise TypeError('Preview_setbinning expects binning string')
        _state["preview_binning"] = str(params[0])
        return _status("OK!")

    if matches('capture_setexposure'):
        if not params:
            raise TypeError('Capture_setexposure expects exposure time')
        _state["capture_exposure"] = float(params[0])
        return _status("OK!")

    if matches('capture_setbinning'):
        if not params:
            raise TypeError('Capture_setbinning expects binning string')
        _state["capture_binning"] = str(params[0])
        return _status("OK!")

    if matches('capture_setobjectname'):
        if not params:
            raise TypeError('Capture_setobjectname expects object name')
        _state["capture_object_name"] = str(params[0])
        return _status("OK!")

    if matches('capture_setcount'):
        if not params:
            raise TypeError('Capture_setcount expects count')
        _state["capture_count"] = int(params[0])
        return _status("OK!")

    if matches('capture_setframetype'):
        if not params:
            raise TypeError('Capture_setframetype expects frame type')
        frame_type = str(params[0]).capitalize()
        if frame_type not in ["Light", "Bias", "Dark", "Flat"]:
            return _status("Failed! Invalid frame type")
        _state["capture_frametype"] = frame_type
        return _status("OK!")

    if matches('capture_setdither'):
        if not params:
            raise TypeError('Capture_setdither expects dither count')
        _state["capture_dither"] = int(params[0])
        return _status("OK!")

    if matches('telescope_slew'):
        if len(params) < 2:
            raise TypeError('Telescope_slew expects [RA, DEC]')
        ra = float(params[0])
        de = float(params[1])
        if ra < 0 or ra > 24:
            raise ValueError("RA must be between 0 and 24")
        if de < -90 or de > 90:
            raise ValueError("DEC must be between -90 and 90")
        _state["telescope_slewing"] = True
        _state["telescope_ra"] = ra
        _state["telescope_de"] = de
        _state["telescope_slewing"] = False
        return _status("OK!")

    if matches('telescope_slewasync'):
        if len(params) < 2:
            raise TypeError('Telescope_slewasync expects [RA, DEC]')
        ra = float(params[0])
        de = float(params[1])
        _state["telescope_slewing"] = True
        _state["telescope_ra"] = ra
        _state["telescope_de"] = de
        return _status("OK!")

    if matches('telescope_sync'):
        if len(params) < 2:
            raise TypeError('Telescope_sync expects [RA, DEC]')
        _state["telescope_ra"] = float(params[0])
        _state["telescope_de"] = float(params[1])
        return _status("OK!")

    if matches('telescope_park'):
        if not params:
            raise TypeError('Telescope_park expects boolean')
        park = bool(params[0])
        _state["telescope_parked"] = park
        _state["telescope_tracking"] = not park
        return _status("OK!")

    if matches('telescope_settrackingrate'):
        if not params:
            raise TypeError('Telescope_settrackingrate expects rate')
        rate = str(params[0]).upper()
        valid_rates = ["SIDEREAL", "LUNAR", "SOLAR", "CUSTOM"]
        if rate not in valid_rates:
            return _status(f"Failed! Rate must be one of {valid_rates}")
        _state["telescope_tracking_rate"] = rate
        return _status("OK!")

    if matches('wheel_setposition'):
        if not params:
            raise TypeError('Wheel_SetPosition expects filter index or name')
        arg = params[0]
        try:
            if isinstance(arg, int):
                idx = arg
            else:
                idx = _state["filters"].index(str(arg))
            if idx < 0 or idx >= len(_state["filters"]):
                raise IndexError('Filter index out of range')
            _state["wheel_index"] = idx
            return _status("OK!")
        except ValueError:
            return _status("Failed! Filter name not found")

    if matches('wheel_setfilter'):
        if not params:
            raise TypeError('Wheel_setfilter expects filter number')
        idx = int(params[0])
        if idx < 0 or idx >= len(_state["filters"]):
            raise IndexError('Filter index out of range')
        _state["wheel_index"] = idx
        return _status("OK!")

    if matches('set_filteroffset'):
        if len(params) < 2 and not isinstance(params[0], (list, tuple)):
            raise TypeError('Set_FilterOffset expects [filter_name, offset]')
        if isinstance(params[0], (list, tuple)):
            filter_name = str(params[0][0])
            offset = int(params[0][1])
        else:
            filter_name = str(params[0])
            offset = int(params[1]) if len(params) > 1 else 0
        # Store offset in state for tracking (could be persisted in real implementation)
        if "filter_offsets" not in _state:
            _state["filter_offsets"] = {}
        _state["filter_offsets"][filter_name] = offset
        return _status("OK!")

    if matches('focuser_setposition'):
        if not _state["focuser_connected"]:
            return _status("Failed! Focuser not connected")
        if not params:
            raise TypeError('Focuser_setposition expects position')
        pos = int(params[0])
        _state["focuser_position"] = pos
        return _status("OK!")

    if matches('rotator_goto'):
        if not params:
            raise TypeError('Rotator_Goto expects angle in degrees')
        angle = float(params[0])
        _state["rotator_angle"] = angle % 360
        return _status("OK!")

    if matches('rotator_sync'):
        if not params:
            raise TypeError('Rotator_Sync expects angle in degrees')
        angle = float(params[0])
        _state["rotator_angle"] = angle % 360
        return _status("OK!")

    if matches('dome_shutter'):
        if not params:
            raise TypeError('Dome_Shutter expects boolean')
        _state["dome_shutter_open"] = bool(params[0])
        return _status("OK!")

    if matches('dome_slave'):
        if not params:
            raise TypeError('Dome_Slave expects boolean')
        _state["dome_slaved"] = bool(params[0])
        return _status("OK!")

    if matches('logmsg'):
        msg = str(params[0]) if params else ''
        _state["logs"].append(msg)
        print(f"[ccdciel mock LogMsg] {msg}")
        return _status("OK!")

    if matches('customheader_add'):
        if len(params) < 2:
            raise TypeError('CustomHeader_add expects [key, value]')
        key = str(params[0])
        value = str(params[1])
        _state["custom_headers"][key] = value
        return _status("OK!")

    if matches('customheader_del'):
        if not params:
            raise TypeError('CustomHeader_del expects key')
        key = str(params[0])
        if key in _state["custom_headers"]:
            del _state["custom_headers"][key]
        return _status("OK!")

    if matches('save_fits_file'):
        if not params:
            raise TypeError('Save_fits_file expects filename')
        _state["capture_last_filename"] = str(params[0])
        return _status("OK!")

    if matches('open_fits_file'):
        if not params:
            raise TypeError('Open_fits_file expects filename')
        return _status("OK!")

    if matches('autoguider_setlockposition'):
        if len(params) < 2:
            raise TypeError('Autoguider_Setlockposition expects [x, y]')
        _state["autoguider_lockposition"] = [int(params[0]), int(params[1])]
        return _status("OK!")

    if matches('autoguider_settletolerance'):
        if len(params) < 3:
            raise TypeError('Autoguider_SetSettleTolerance expects px, min, timeout')
        return _status("OK!")

    if matches('calibrator_light_on'):
        if not params:
            raise TypeError('Calibrator_light_on expects brightness')
        brightness = int(params[0])
        if brightness < 0 or brightness > 100:
            return _status("Failed! Brightness must be 0-100")
        _state["calibrator_brightness"] = brightness
        return _status("OK!")

    if matches('j2000_to_apparent'):
        if len(params) < 2:
            raise TypeError('J2000_to_Apparent expects [RA, DEC]')
        ra = float(params[0])
        de = float(params[1])
        return _result([ra + 0.001, de + 0.001])

    if matches('apparent_to_j2000'):
        if len(params) < 2:
            raise TypeError('Apparent_to_J2000 expects [RA, DEC]')
        ra = float(params[0])
        de = float(params[1])
        return _result([ra - 0.001, de - 0.001])

    if matches('eq2hz'):
        if len(params) < 2:
            raise TypeError('Eq2hz expects [RA, DEC]')
        ra = float(params[0])
        de = float(params[1])
        alt = 45 + de / 2
        az = 180 + ra * 15 / 2
        return _result([az % 360, alt % 90])

    # ============================================================================
    # SPECIAL STATUS METHOD
    # ============================================================================

    if matches('status'):
        status_dict = {
            "devices": _get_devices_status(),
            "camera": _get_camera_status(),
            "telescope": _get_telescope_status(),
            "focuser": _get_focuser_status(),
            "wheel": _get_wheel_status(),
            "rotator": _get_rotator_status(),
            "dome": _get_dome_status(),
            "autoguider": _get_autoguider_status(),
            "capture": _get_capture_status(),
            "sequence": _get_sequence_status(),
            "safety": _get_safety_status(),
            "planetarium": _get_planetarium_status(),
            "weather": _get_weather_status(),
        }

        # Filter by requested params if provided
        if params and isinstance(params[0], (list, tuple)):
            filtered = {}
            for key in params[0]:
                if key in status_dict:
                    filtered[key] = status_dict[key]
            return _result(filtered)

        return _result(status_dict)

    # Unknown method
    raise NotImplementedError(f"Mock: Method '{method}' is not implemented")

# ============================================================================
# HELPER FUNCTIONS - Status response builders
# ============================================================================

def _get_devices_status() -> Dict[str, Any]:
    """Build devices status for status() method."""
    return {
        "all_connected": _state["devices_connected"],
        "camera": _state["camera_connected"],
        "telescope": _state["telescope_connected"],
        "dome": _state["dome_connected"],
        "focuser": _state["focuser_connected"],
        "wheel": _state["wheel_connected"],
        "rotator": _state["rotator_connected"],
        "autoguider": _state["autoguider_connected"],
        "planetarium": _state["planetarium_connected"],
    }

def _get_camera_status() -> Dict[str, Any]:
    """Build camera status."""
    return {
        "connected": _state["camera_connected"],
        "binning": _state["camera_binning"],
        "frame": "/".join(map(str, _state["camera_frame"])),
        "cooler": _state["cooler_enabled"],
        "temperature": _state["ccd_temperature"],
    }

def _get_telescope_status() -> Dict[str, Any]:
    """Build telescope status."""
    return {
        "connected": _state["telescope_connected"],
        "parked": _state["telescope_parked"],
        "tracking": _state["telescope_tracking"],
        "tracking_rate": _state["telescope_tracking_rate"],
        "slewing": _state["telescope_slewing"],
        "pier_side": _state["telescope_pier_side"],
        "ra": _state["telescope_ra"],
        "de": _state["telescope_de"],
    }

def _get_focuser_status() -> Dict[str, Any]:
    """Build focuser status."""
    return {
        "connected": _state["focuser_connected"],
        "position": _state["focuser_position"],
        "temperature": _state["focuser_temperature"],
        "message": _state["focuser_message"],
    }

def _get_wheel_status() -> Dict[str, Any]:
    """Build filter wheel status."""
    return {
        "connected": _state["wheel_connected"],
        "current_filter": _state["filters"][_state["wheel_index"]] if _state["wheel_index"] < len(_state["filters"]) else "unknown",
        "position": _state["wheel_index"],
        "filters": _state["filters"],
    }

def _get_rotator_status() -> Dict[str, Any]:
    """Build rotator status."""
    return {
        "connected": _state["rotator_connected"],
        "angle": _state["rotator_angle"],
    }

def _get_dome_status() -> Dict[str, Any]:
    """Build dome status."""
    return {
        "connected": _state["dome_connected"],
        "parked": _state["dome_parked"],
        "shutter_open": _state["dome_shutter_open"],
        "slaved": _state["dome_slaved"],
    }

def _get_autoguider_status() -> Dict[str, Any]:
    """Build autoguider status."""
    return {
        "connected": _state["autoguider_connected"],
        "running": _state["autoguider_running"],
        "guiding": _state["autoguider_guiding"],
        "lock_position": _state["autoguider_lockposition"],
    }

def _get_capture_status() -> Dict[str, Any]:
    """Build capture status."""
    return {
        "connected": _state["camera_connected"],
        "running": _state["capture_running"],
        "exposure": _state["capture_exposure"],
        "binning": _state["capture_binning"],
        "object": _state["capture_object_name"],
        "count": _state["capture_count"],
        "frame_type": _state["capture_frametype"],
        "dither": _state["capture_dither"],
        "last_file": _state["capture_last_filename"],
    }

def _get_sequence_status() -> Dict[str, Any]:
    """Build sequence status."""
    return {
        "running": False,
        "current_step": 0,
    }


def _get_safety_status() -> Dict[str, Any]:
    """Build safety status."""
    return {
        "telescope_parked": _state["telescope_parked"],
        "dome_parked": _state["dome_parked"],
        "cover_closed": True,
    }

def _get_planetarium_status() -> Dict[str, Any]:
    """Build planetarium status."""
    return {
        "connected": _state["planetarium_connected"],
    }

def _get_weather_status() -> Dict[str, Any]:
    """Build weather status."""
    return {
        "temperature": 15.0,
        "humidity": 65,
        "pressure": 1013.25,
    }

# ============================================================================
# CONVENIENCE FUNCTIONS - Testing helpers
# ============================================================================

def _set_state(**kwargs):
    """Set mock state values for testing. Useful for initializing conditions."""
    for k, v in kwargs.items():
        if k in _state:
            _state[k] = v

def _get_state() -> Dict[str, Any]:
    """Get a deep copy of the current mock state."""
    return copy.deepcopy(_state)
