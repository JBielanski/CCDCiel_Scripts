# PyIndi.py
# SPDX-FileCopyrightText: 2026 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
# Mock implementation of the PyIndi (pyindi-client) library for testing.
#
# Based on:
#   - PyIndi documentation   : https://docs.indilib.org/pyindi-client/
#   - SWIG interface file     : https://github.com/indilib/pyindi-client/blob/master/indiclientpython.i
#   - INDI C++ API            : http://www.indilib.org/api/index.html
#
# This mock replaces the real PyIndi module in environments without a running
# INDI server and is intended for unit testing of scripts that use PyIndi.
#
# Coverage:
#   - Constants : ISS_OFF/ON, IPS_IDLE/OK/BUSY/ALERT, INDI_NUMBER/SWITCH/TEXT/
#                 LIGHT/BLOB, B_NEVER/ALSO/ONLY
#   - BaseClient: setServer, connectServer, disconnectServer, getHost, getPort,
#                 getDevices, getDevice, sendNewSwitch, sendNewNumber, sendNewText,
#                 setBLOBMode, sendOneBlobFromBuffer; all virtual callbacks
#   - BaseDevice: getDeviceName, getDriverName, getSwitch, getNumber, getText,
#                 getLight, getProperties, messageQueue
#   - Legacy vector-property types (ISwitchVectorProperty, INumberVectorProperty,
#     ITextVectorProperty, ILightVectorProperty, IBLOBVectorProperty) with
#     indexing, __len__, __iter__ and state/label/name accessors
#   - Widget types (ISwitch, INumber, IText, ILight, IBLOB) with attribute and
#     method access; `.s` / `.value` shorthands stay in sync with getState/setState
#   - New-API wrapper classes: PropertySwitch, PropertyNumber, PropertyText,
#     PropertyLight, PropertyBlob with findWidgetByName support
#   - Configurable mock state via _set_state() / _reset_state() / _add_device() /
#     _add_switch / _add_number / _add_text
#
# Default pre-configured devices:
#   "iEQ"        – iOptron CEM60-EC mount
#                    HOME    switch  : [0=SET_CURRENT_AS_HOME, 1=GO_HOME, 2=FIND_HOME]
#                    TELESCOPE_TRACK_STATE switch: [0=TRACK_ON, 1=TRACK_OFF]
#                    EQUATORIAL_EOD_COORD  number: [0=RA, 1=DEC]
#   "Pegasus SPB" – Pegasus Astro Saddle Power Box
#                    DEWAUTO switch  : [0=Enabled, 1=Disabled]
#                    DEW_PWM number  : [0=DEW_A, 1=DEW_B]
#
# List of changes:
# [30-03-2026] Initial mock implementation
# ---------------------------------------------------------------------------- #

from typing import Any, Dict, List, Optional
import copy

# ============================================================================
# CONSTANTS
# ============================================================================

# Switch Element State (ISState)
ISS_OFF = 0
ISS_ON  = 1

# Property State (IPState)
IPS_IDLE  = 0
IPS_OK    = 1
IPS_BUSY  = 2
IPS_ALERT = 3

# Property Type (INDI_PROPERTY_TYPE)
INDI_NUMBER  = 0
INDI_SWITCH  = 1
INDI_TEXT    = 2
INDI_LIGHT   = 3
INDI_BLOB    = 4
INDI_UNKNOWN = 5

# BLOB Handling Mode (BLOBHandling)
B_NEVER = 0
B_ALSO  = 1
B_ONLY  = 2

# -- internal string maps --
_ISS_STR  = {ISS_OFF: "Off", ISS_ON: "On"}
_IPS_STR  = {IPS_IDLE: "Idle", IPS_OK: "Ok", IPS_BUSY: "Busy", IPS_ALERT: "Alert"}
_TYPE_STR = {
    INDI_NUMBER: "Number",
    INDI_SWITCH: "Switch",
    INDI_TEXT:   "Text",
    INDI_LIGHT:  "Light",
    INDI_BLOB:   "Blob",
}


# ============================================================================
# WIDGET CLASSES  (individual elements inside a vector property)
# ============================================================================

class ISwitch:
    """Mock of a single INDI switch element (ISwitch struct).

    Both the legacy attribute `.s` and the methods `getState()` / `setState()`
    are kept in sync so that code using either style works correctly.
    """

    def __init__(self, name: str, label: str = "", state: int = ISS_OFF):
        self.name  = name
        self.label = label or name
        self._state = state

    # Legacy struct attribute `.s`
    @property
    def s(self) -> int:
        return self._state

    @s.setter
    def s(self, value: int) -> None:
        self._state = int(value)

    def getState(self) -> int:
        return self._state

    def setState(self, state: int) -> None:
        self._state = int(state)

    def getStateAsString(self) -> str:
        return _ISS_STR.get(self._state, "Unknown")

    def getName(self) -> str:
        return self.name

    def getLabel(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"ISwitch(name={self.name!r}, state={self.getStateAsString()!r})"


class INumber:
    """Mock of a single INDI number element (INumber struct).

    Both the legacy attribute `.value` and the methods `getValue()` / `setValue()`
    are kept in sync.
    """

    def __init__(self, name: str, label: str = "", value: float = 0.0,
                 min_val: float = 0.0, max_val: float = 1_000_000.0,
                 step: float = 1.0, format: str = "%f"):
        self.name   = name
        self.label  = label or name
        self._value = float(value)
        self.min    = float(min_val)
        self.max    = float(max_val)
        self.step   = float(step)
        self.format = format

    # Legacy struct attribute `.value`
    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float) -> None:
        self._value = float(v)

    def getValue(self) -> float:
        return self._value

    def setValue(self, v: float) -> None:
        self._value = float(v)

    def getName(self) -> str:
        return self.name

    def getLabel(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"INumber(name={self.name!r}, value={self._value})"


class IText:
    """Mock of a single INDI text element (IText struct)."""

    def __init__(self, name: str, label: str = "", text: str = ""):
        self.name   = name
        self.label  = label or name
        self._text  = str(text)

    # Legacy struct attribute `.text`
    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, v: str) -> None:
        self._text = str(v)

    def getText(self) -> str:
        return self._text

    def setText(self, v: str) -> None:
        self._text = str(v)

    def getName(self) -> str:
        return self.name

    def getLabel(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"IText(name={self.name!r}, text={self._text!r})"


class ILight:
    """Mock of a single INDI light element (ILight struct)."""

    def __init__(self, name: str, label: str = "", state: int = IPS_IDLE):
        self.name   = name
        self.label  = label or name
        self._state = state

    def getState(self) -> int:
        return self._state

    def setState(self, state: int) -> None:
        self._state = int(state)

    def getStateAsString(self) -> str:
        return _IPS_STR.get(self._state, "Unknown")

    def getName(self) -> str:
        return self.name

    def getLabel(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f"ILight(name={self.name!r}, state={self.getStateAsString()!r})"


class IBLOB:
    """Mock of a single INDI BLOB element (IBLOB struct)."""

    def __init__(self, name: str, label: str = "", blob: bytes = b"",
                 blob_format: str = ".fits"):
        self.name    = name
        self.label   = label or name
        self._blob   = bytes(blob)
        self.format  = blob_format
        self.size    = len(self._blob)

    def getblob(self) -> bytes:
        return self._blob

    def getblobdata(self) -> bytearray:
        return bytearray(self._blob)

    def getSize(self) -> int:
        return len(self._blob)

    def getFormat(self) -> str:
        return self.format

    def getName(self) -> str:
        return self.name

    def getLabel(self) -> str:
        return self.label

    def setBlob(self, data: bytes) -> None:
        self._blob = bytes(data)
        self.size  = len(data)

    def __repr__(self) -> str:
        return f"IBLOB(name={self.name!r}, size={self.size})"


# ============================================================================
# VECTOR PROPERTY CLASSES  (legacy ISwitchVectorProperty / INumber… style)
# ============================================================================

class _BaseVectorProperty:
    """Common base for all legacy INDI vector-property mock types."""

    def __init__(self, name: str, label: str = "", device_name: str = "",
                 state: int = IPS_OK, elements: Optional[List] = None,
                 prop_type: int = INDI_UNKNOWN):
        self._name        = name
        self._label       = label or name
        self._device_name = device_name
        self._state       = state
        self._elements    = list(elements) if elements else []
        self._prop_type   = prop_type

    # ---- container protocol -------------------------------------------------
    def __getitem__(self, index: int):
        if index < 0 or index >= len(self._elements):
            raise IndexError("VectorProperty index out of bounds")
        return self._elements[index]

    def __len__(self) -> int:
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    # ---- accessors ----------------------------------------------------------
    def getName(self) -> str:
        return self._name

    def getLabel(self) -> str:
        return self._label

    def getDeviceName(self) -> str:
        return self._device_name

    def getState(self) -> int:
        return self._state

    def setState(self, state: int) -> None:
        self._state = int(state)

    def getStateAsString(self) -> str:
        return _IPS_STR.get(self._state, "Unknown")

    def getType(self) -> int:
        return self._prop_type

    def getTypeAsString(self) -> str:
        return _TYPE_STR.get(self._prop_type, "Unknown")

    def findWidgetByName(self, name: str):
        for elem in self._elements:
            if elem.name == name:
                return elem
        return None

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(name={self._name!r}, "
                f"device={self._device_name!r}, "
                f"state={self.getStateAsString()!r}, "
                f"elements={self._elements!r})")


class ISwitchVectorProperty(_BaseVectorProperty):
    """Mock of INDI ISwitchVectorProperty."""
    def __init__(self, name: str, label: str = "", device_name: str = "",
                 state: int = IPS_OK, elements: Optional[List[ISwitch]] = None):
        super().__init__(name, label, device_name, state, elements, INDI_SWITCH)


class INumberVectorProperty(_BaseVectorProperty):
    """Mock of INDI INumberVectorProperty."""
    def __init__(self, name: str, label: str = "", device_name: str = "",
                 state: int = IPS_OK, elements: Optional[List[INumber]] = None):
        super().__init__(name, label, device_name, state, elements, INDI_NUMBER)


class ITextVectorProperty(_BaseVectorProperty):
    """Mock of INDI ITextVectorProperty."""
    def __init__(self, name: str, label: str = "", device_name: str = "",
                 state: int = IPS_OK, elements: Optional[List[IText]] = None):
        super().__init__(name, label, device_name, state, elements, INDI_TEXT)


class ILightVectorProperty(_BaseVectorProperty):
    """Mock of INDI ILightVectorProperty."""
    def __init__(self, name: str, label: str = "", device_name: str = "",
                 state: int = IPS_OK, elements: Optional[List[ILight]] = None):
        super().__init__(name, label, device_name, state, elements, INDI_LIGHT)


class IBLOBVectorProperty(_BaseVectorProperty):
    """Mock of INDI IBLOBVectorProperty."""
    def __init__(self, name: str, label: str = "", device_name: str = "",
                 state: int = IPS_OK, elements: Optional[List[IBLOB]] = None):
        super().__init__(name, label, device_name, state, elements, INDI_BLOB)


# ============================================================================
# NEW-API PROPERTY WRAPPERS  (INDI 2.0 PropertySwitch / PropertyNumber …)
# These wrap any _BaseVectorProperty and add findWidgetByName support. They
# mirror how PropertySwitch(p) / PropertyNumber(p) are used in INDI 2.0 code.
# ============================================================================

class PropertySwitch:
    """INDI 2.0 PropertySwitch wrapper – wraps an ISwitchVectorProperty."""
    def __init__(self, prop: _BaseVectorProperty):
        self._prop = prop

    def __iter__(self):     return iter(self._prop)
    def __getitem__(self, i):  return self._prop[i]
    def __len__(self):      return len(self._prop)

    def getName(self) -> str:          return self._prop.getName()
    def getLabel(self) -> str:         return self._prop.getLabel()
    def getDeviceName(self) -> str:    return self._prop.getDeviceName()
    def getStateAsString(self) -> str: return self._prop.getStateAsString()
    def getType(self) -> int:          return INDI_SWITCH
    def getTypeAsString(self) -> str:  return "Switch"

    def findWidgetByName(self, name: str) -> Optional[ISwitch]:
        return self._prop.findWidgetByName(name)


class PropertyNumber:
    """INDI 2.0 PropertyNumber wrapper – wraps an INumberVectorProperty."""
    def __init__(self, prop: _BaseVectorProperty):
        self._prop = prop

    def __iter__(self):     return iter(self._prop)
    def __getitem__(self, i):  return self._prop[i]
    def __len__(self):      return len(self._prop)

    def getName(self) -> str:          return self._prop.getName()
    def getLabel(self) -> str:         return self._prop.getLabel()
    def getDeviceName(self) -> str:    return self._prop.getDeviceName()
    def getStateAsString(self) -> str: return self._prop.getStateAsString()
    def getType(self) -> int:          return INDI_NUMBER
    def getTypeAsString(self) -> str:  return "Number"

    def findWidgetByName(self, name: str) -> Optional[INumber]:
        return self._prop.findWidgetByName(name)


class PropertyText:
    """INDI 2.0 PropertyText wrapper – wraps an ITextVectorProperty."""
    def __init__(self, prop: _BaseVectorProperty):
        self._prop = prop

    def __iter__(self):     return iter(self._prop)
    def __getitem__(self, i):  return self._prop[i]
    def __len__(self):      return len(self._prop)

    def getName(self) -> str:          return self._prop.getName()
    def getLabel(self) -> str:         return self._prop.getLabel()
    def getDeviceName(self) -> str:    return self._prop.getDeviceName()
    def getStateAsString(self) -> str: return self._prop.getStateAsString()
    def getType(self) -> int:          return INDI_TEXT
    def getTypeAsString(self) -> str:  return "Text"

    def findWidgetByName(self, name: str) -> Optional[IText]:
        return self._prop.findWidgetByName(name)


class PropertyLight:
    """INDI 2.0 PropertyLight wrapper – wraps an ILightVectorProperty."""
    def __init__(self, prop: _BaseVectorProperty):
        self._prop = prop

    def __iter__(self):     return iter(self._prop)
    def __getitem__(self, i):  return self._prop[i]
    def __len__(self):      return len(self._prop)

    def getName(self) -> str:          return self._prop.getName()
    def getLabel(self) -> str:         return self._prop.getLabel()
    def getDeviceName(self) -> str:    return self._prop.getDeviceName()
    def getStateAsString(self) -> str: return self._prop.getStateAsString()
    def getType(self) -> int:          return INDI_LIGHT
    def getTypeAsString(self) -> str:  return "Light"

    def findWidgetByName(self, name: str) -> Optional[ILight]:
        return self._prop.findWidgetByName(name)


class PropertyBlob:
    """INDI 2.0 PropertyBlob wrapper – wraps an IBLOBVectorProperty."""
    def __init__(self, prop: _BaseVectorProperty):
        self._prop = prop

    def __iter__(self):     return iter(self._prop)
    def __getitem__(self, i):  return self._prop[i]
    def __len__(self):      return len(self._prop)

    def getName(self) -> str:          return self._prop.getName()
    def getLabel(self) -> str:         return self._prop.getLabel()
    def getDeviceName(self) -> str:    return self._prop.getDeviceName()
    def getStateAsString(self) -> str: return self._prop.getStateAsString()
    def getType(self) -> int:          return INDI_BLOB
    def getTypeAsString(self) -> str:  return "Blob"

    def findWidgetByName(self, name: str) -> Optional[IBLOB]:
        return self._prop.findWidgetByName(name)


# ============================================================================
# BASE DEVICE
# ============================================================================

class BaseDevice:
    """Mock of INDI BaseDevice – represents a single INDI device."""

    def __init__(self, name: str, driver_name: str = ""):
        self._name        = name
        self._driver_name = driver_name or name
        self._switches: Dict[str, ISwitchVectorProperty] = {}
        self._numbers:  Dict[str, INumberVectorProperty] = {}
        self._texts:    Dict[str, ITextVectorProperty]   = {}
        self._lights:   Dict[str, ILightVectorProperty]  = {}
        self._blobs:    Dict[str, IBLOBVectorProperty]   = {}
        self._messages: List[str] = []

    # ---- INDI interface -----------------------------------------------------
    def getDeviceName(self) -> str:
        return self._name

    def getDriverName(self) -> str:
        return self._driver_name

    def getSwitch(self, name: str) -> Optional[ISwitchVectorProperty]:
        return self._switches.get(name)

    def getNumber(self, name: str) -> Optional[INumberVectorProperty]:
        return self._numbers.get(name)

    def getText(self, name: str) -> Optional[ITextVectorProperty]:
        return self._texts.get(name)

    def getLight(self, name: str) -> Optional[ILightVectorProperty]:
        return self._lights.get(name)

    def getBlob(self, name: str) -> Optional[IBLOBVectorProperty]:
        return self._blobs.get(name)

    def getProperties(self) -> list:
        """Return all properties as a flat list (generic property objects)."""
        props: list = []
        props.extend(self._switches.values())
        props.extend(self._numbers.values())
        props.extend(self._texts.values())
        props.extend(self._lights.values())
        props.extend(self._blobs.values())
        return props

    def messageQueue(self, index: int) -> str:
        if 0 <= index < len(self._messages):
            return self._messages[index]
        return ""

    # ---- helpers for test configuration ------------------------------------
    def _add_switch(self, name: str, label: str = "",
                    elements: Optional[List[ISwitch]] = None) -> ISwitchVectorProperty:
        vec = ISwitchVectorProperty(name, label, self._name, IPS_OK, elements)
        self._switches[name] = vec
        return vec

    def _add_number(self, name: str, label: str = "",
                    elements: Optional[List[INumber]] = None) -> INumberVectorProperty:
        vec = INumberVectorProperty(name, label, self._name, IPS_OK, elements)
        self._numbers[name] = vec
        return vec

    def _add_text(self, name: str, label: str = "",
                  elements: Optional[List[IText]] = None) -> ITextVectorProperty:
        vec = ITextVectorProperty(name, label, self._name, IPS_OK, elements)
        self._texts[name] = vec
        return vec

    def _add_light(self, name: str, label: str = "",
                   elements: Optional[List[ILight]] = None) -> ILightVectorProperty:
        vec = ILightVectorProperty(name, label, self._name, IPS_OK, elements)
        self._lights[name] = vec
        return vec

    def _add_blob(self, name: str, label: str = "",
                  elements: Optional[List[IBLOB]] = None) -> IBLOBVectorProperty:
        vec = IBLOBVectorProperty(name, label, self._name, IPS_OK, elements)
        self._blobs[name] = vec
        return vec

    def _add_message(self, message: str) -> None:
        self._messages.append(message)

    def __repr__(self) -> str:
        return f"BaseDevice(name={self._name!r}, driver={self._driver_name!r})"


# ============================================================================
# BASE CLIENT  (inherit from this to create your IndiClient)
# ============================================================================

class BaseMediator:
    """Mock of INDI BaseMediator – base for BaseClient callbacks."""
    pass


class BaseClient(BaseMediator):
    """Mock of INDI BaseClient.

    Inherit from this class exactly as you would from the real PyIndi.BaseClient.
    Override any of the virtual callback methods as needed.

    Mock behaviour:
        - connectServer() returns the value of PyIndi._state["server_connected"]
        - getDevice(name) looks up PyIndi._devices
        - sendNewSwitch / sendNewNumber / sendNewText record the call in
          PyIndi._state["sent_properties"] for test assertions
    """

    def __init__(self):
        super().__init__()
        self._host = "localhost"
        self._port = 7624

    # ---- server connection --------------------------------------------------
    def setServer(self, host: str, port: int) -> None:
        self._host = str(host)
        self._port = int(port)

    def connectServer(self) -> bool:
        return bool(_state["server_connected"])

    def disconnectServer(self) -> None:
        pass

    def isServerConnected(self) -> bool:
        return bool(_state["server_connected"])

    def getHost(self) -> str:
        return self._host

    def getPort(self) -> int:
        return self._port

    # ---- device discovery ---------------------------------------------------
    def getDevices(self) -> List[BaseDevice]:
        return list(_devices.values())

    def getDevice(self, name: str) -> Optional[BaseDevice]:
        return _devices.get(name)

    # ---- property send methods ----------------------------------------------
    def sendNewSwitch(self, svp: ISwitchVectorProperty) -> None:
        _state["sent_properties"].append(copy.deepcopy(svp))

    def sendNewNumber(self, nvp: INumberVectorProperty) -> None:
        _state["sent_properties"].append(copy.deepcopy(nvp))

    def sendNewText(self, tvp: ITextVectorProperty) -> None:
        _state["sent_properties"].append(copy.deepcopy(tvp))

    def setBLOBMode(self, mode: int, device_name: str,
                    property_name: Optional[str]) -> None:
        pass

    def sendOneBlobFromBuffer(self, name: str, blob_type: str,
                               data: bytes, length: int) -> None:
        pass

    # ---- virtual callbacks (override in your IndiClient) --------------------
    def newDevice(self, d: BaseDevice) -> None:            pass
    def removeDevice(self, d: BaseDevice) -> None:         pass
    def newProperty(self, p: _BaseVectorProperty) -> None: pass
    def updateProperty(self, p: _BaseVectorProperty) -> None: pass
    def removeProperty(self, p: _BaseVectorProperty) -> None: pass
    def newBLOB(self, bp: IBLOBVectorProperty) -> None:    pass
    def newSwitch(self, svp: ISwitchVectorProperty) -> None: pass
    def newNumber(self, nvp: INumberVectorProperty) -> None: pass
    def newText(self, tvp: ITextVectorProperty) -> None:   pass
    def newLight(self, lvp: ILightVectorProperty) -> None: pass
    def newMessage(self, d: BaseDevice, m: int) -> None:   pass
    def serverConnected(self) -> None:                     pass
    def serverDisconnected(self, code: int) -> None:       pass


# ============================================================================
# MOCK STATE  – configurable at the module level for testing
# ============================================================================

# Core mock state flags
_state: Dict[str, Any] = {
    "server_connected": True,    # connectServer() return value
    "sent_properties":  [],      # list of properties sent via sendNew*
}

# Registry of mock devices
_devices: Dict[str, BaseDevice] = {}


# ============================================================================
# DEFAULT DEVICE FACTORY  – builds the project-specific pre-configured devices
# ============================================================================

def _build_default_devices() -> Dict[str, BaseDevice]:
    """Return the default set of devices used by the CCDCiel_Scripts project."""
    devices: Dict[str, BaseDevice] = {}

    # --- iOptron CEM60-EC mount ----------------------------------------------
    ieq = BaseDevice("iEQ", driver_name="indi_ioptronv3")

    ieq._add_switch("HOME", "Home Operation", [
        ISwitch("SET_CURRENT_AS_HOME", "Set Current As Home",  ISS_OFF),
        ISwitch("GO_HOME",             "Go Home",              ISS_OFF),
        ISwitch("FIND_HOME",           "Find Home",            ISS_OFF),
    ])
    ieq._add_switch("TELESCOPE_TRACK_STATE", "Tracking State", [
        ISwitch("TRACK_ON",  "Enable Tracking",  ISS_ON),
        ISwitch("TRACK_OFF", "Disable Tracking", ISS_OFF),
    ])
    ieq._add_number("EQUATORIAL_EOD_COORD", "Eq. Coordinates", [
        INumber("RA",  "RA (hh:mm:ss)",  value=0.0, min_val=0.0, max_val=24.0),
        INumber("DEC", "DEC (dd:mm:ss)", value=0.0, min_val=-90.0, max_val=90.0),
    ])
    ieq._add_switch("TELESCOPE_PARK", "Parking", [
        ISwitch("PARK",   "Park",   ISS_OFF),
        ISwitch("UNPARK", "Unpark", ISS_OFF),
    ])
    devices["iEQ"] = ieq

    # --- Pegasus Astro Saddle Power Box --------------------------------------
    pa_spb = BaseDevice("Pegasus SPB", driver_name="indi_pegasus_spb")

    pa_spb._add_switch("DEWAUTO", "Dew Control Auto", [
        ISwitch("ENABLED",  "Enabled",  ISS_OFF),
        ISwitch("DISABLED", "Disabled", ISS_ON),
    ])
    pa_spb._add_number("DEW_PWM", "Dew Heater Power", [
        INumber("DEW_A", "Dew A", value=0.0, min_val=0.0, max_val=255.0),
        INumber("DEW_B", "Dew B", value=0.0, min_val=0.0, max_val=255.0),
    ])
    pa_spb._add_switch("POWER_CONTROL", "Power Control", [
        ISwitch("POWER_CONTROL_1", "Port 1", ISS_ON),
        ISwitch("POWER_CONTROL_2", "Port 2", ISS_ON),
        ISwitch("POWER_CONTROL_3", "Port 3", ISS_ON),
        ISwitch("POWER_CONTROL_4", "Port 4", ISS_ON),
    ])
    devices["Pegasus SPB"] = pa_spb

    # --- Generic CCD (for documentation-style examples) ----------------------
    ccd = BaseDevice("CCD Simulator", driver_name="indi_simulator_ccd")

    ccd._add_number("CCD_EXPOSURE", "CCD Exposure", [
        INumber("CCD_EXPOSURE_VALUE", "Duration (s)", value=1.0, min_val=0.001, max_val=3600.0),
    ])
    ccd._add_number("CCD_TEMPERATURE", "CCD Temperature", [
        INumber("CCD_TEMPERATURE_VALUE", "Temperature (C)", value=20.0, min_val=-60.0, max_val=40.0),
    ])
    ccd._add_number("CCD_FRAME", "CCD Frame", [
        INumber("X",      "Left (px)",   value=0.0),
        INumber("Y",      "Top (px)",    value=0.0),
        INumber("WIDTH",  "Width (px)",  value=1280.0),
        INumber("HEIGHT", "Height (px)", value=1024.0),
    ])
    ccd._add_blob("CCD1", "CCD1 BLOB", [
        IBLOB("CCD1", "Image", b"", ".fits"),
    ])
    devices["CCD Simulator"] = ccd

    # --- Generic Telescope simulator (for documentation-style examples) ------
    scope = BaseDevice("Telescope Simulator", driver_name="indi_simulator_telescope")

    scope._add_switch("TELESCOPE_TRACK_STATE", "Tracking State", [
        ISwitch("TRACK_ON",  "Enable Tracking",  ISS_ON),
        ISwitch("TRACK_OFF", "Disable Tracking", ISS_OFF),
    ])
    scope._add_number("EQUATORIAL_EOD_COORD", "Eq. Coordinates", [
        INumber("RA",  "RA (hh:mm:ss)",  value=0.0, min_val=0.0, max_val=24.0),
        INumber("DEC", "DEC (dd:mm:ss)", value=0.0, min_val=-90.0, max_val=90.0),
    ])
    scope._add_switch("TELESCOPE_PARK", "Parking", [
        ISwitch("PARK",   "Park",   ISS_OFF),
        ISwitch("UNPARK", "Unpark", ISS_OFF),
    ])
    scope._add_switch("TELESCOPE_MOTION_NS", "Move N/S", [
        ISwitch("MOTION_NORTH", "Move North", ISS_OFF),
        ISwitch("MOTION_SOUTH", "Move South", ISS_OFF),
    ])
    scope._add_switch("TELESCOPE_MOTION_WE", "Move W/E", [
        ISwitch("MOTION_WEST", "Move West",  ISS_OFF),
        ISwitch("MOTION_EAST", "Move East",  ISS_OFF),
    ])
    devices["Telescope Simulator"] = scope

    return devices


def _reset_state() -> None:
    """Reset mock state and devices to the default configuration.

    Call this in test setUp / setup_function to guarantee a clean state.
    """
    global _state, _devices
    _state.update({
        "server_connected": True,
        "sent_properties":  [],
    })
    _devices.clear()
    _devices.update(_build_default_devices())


def _set_state(**kwargs) -> None:
    """Partially update mock state without resetting devices.

    Supported keys:
        server_connected (bool)  – connectServer() return value
        sent_properties  (list)  – pre-populate sent-properties log

    Example::
        PyIndi._set_state(server_connected=False)
    """
    for key, value in kwargs.items():
        if key not in _state:
            raise KeyError(f"Unknown PyIndi mock state key: {key!r}")
        _state[key] = value


def _add_device(device: BaseDevice) -> None:
    """Register a custom BaseDevice in the mock device registry.

    Example::
        dev = PyIndi.BaseDevice("My Device", "indi_my_driver")
        dev._add_switch("MY_PROPERTY", elements=[PyIndi.ISwitch("SW1")])
        PyIndi._add_device(dev)
    """
    _devices[device.getDeviceName()] = device


def _get_sent_properties() -> list:
    """Return a copy of all properties sent via sendNew* calls since last reset."""
    return list(_state["sent_properties"])


def _clear_sent_properties() -> None:
    """Clear the sent-properties log."""
    _state["sent_properties"].clear()


# ---- Populate default devices on module load --------------------------------
_reset_state()
