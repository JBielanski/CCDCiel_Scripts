# test_pyindi_mock.py
# SPDX-FileCopyrightText: 2026 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
# Test suite for the PyIndi mock (PyIndi.py).
# Covers every public class, constant, and helper function exported by the mock.
#
# Run with:
#   cd /home/jbielanski/Dokumenty/DEVELOPMENT/CCDCiel_Scripts
#   pytest TEST/test_pyindi_mock.py -v
# ---------------------------------------------------------------------------- #

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import PyIndi


# ============================================================================
# Helpers / fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_pyindi_state():
    """Reset mock state before every test (works for both function- and class-based tests)."""
    PyIndi._reset_state()


# ============================================================================
# Constants
# ============================================================================

class TestConstants:
    def test_switch_states(self):
        assert PyIndi.ISS_OFF == 0
        assert PyIndi.ISS_ON  == 1

    def test_property_states(self):
        assert PyIndi.IPS_IDLE  == 0
        assert PyIndi.IPS_OK    == 1
        assert PyIndi.IPS_BUSY  == 2
        assert PyIndi.IPS_ALERT == 3

    def test_property_types(self):
        assert PyIndi.INDI_NUMBER  == 0
        assert PyIndi.INDI_SWITCH  == 1
        assert PyIndi.INDI_TEXT    == 2
        assert PyIndi.INDI_LIGHT   == 3
        assert PyIndi.INDI_BLOB    == 4
        assert PyIndi.INDI_UNKNOWN == 5

    def test_blob_handling(self):
        assert PyIndi.B_NEVER == 0
        assert PyIndi.B_ALSO  == 1
        assert PyIndi.B_ONLY  == 2


# ============================================================================
# ISwitch widget
# ============================================================================

class TestISwitch:
    def test_default_state_is_off(self):
        sw = PyIndi.ISwitch("SW1")
        assert sw.getState() == PyIndi.ISS_OFF
        assert sw.getStateAsString() == "Off"

    def test_set_state_via_method(self):
        sw = PyIndi.ISwitch("SW1")
        sw.setState(PyIndi.ISS_ON)
        assert sw.getState() == PyIndi.ISS_ON
        assert sw.getStateAsString() == "On"
        assert sw.s == PyIndi.ISS_ON

    def test_set_state_via_attribute(self):
        sw = PyIndi.ISwitch("SW1")
        sw.s = PyIndi.ISS_ON
        assert sw.getState() == PyIndi.ISS_ON
        assert sw.s == PyIndi.ISS_ON

    def test_s_and_getState_are_synced(self):
        sw = PyIndi.ISwitch("SW1")
        sw.s = 1
        assert sw.getState() == 1
        sw.setState(0)
        assert sw.s == 0

    def test_name_and_label(self):
        sw = PyIndi.ISwitch("SW1", "My Switch", PyIndi.ISS_ON)
        assert sw.getName()  == "SW1"
        assert sw.getLabel() == "My Switch"

    def test_label_defaults_to_name(self):
        sw = PyIndi.ISwitch("SW1")
        assert sw.getLabel() == "SW1"


# ============================================================================
# INumber widget
# ============================================================================

class TestINumber:
    def test_default_value(self):
        n = PyIndi.INumber("N1")
        assert n.getValue() == 0.0
        assert n.value == 0.0

    def test_set_value_via_method(self):
        n = PyIndi.INumber("N1", value=10.5)
        n.setValue(42.0)
        assert n.getValue() == 42.0
        assert n.value == 42.0

    def test_set_value_via_attribute(self):
        n = PyIndi.INumber("N1")
        n.value = 7.7
        assert n.getValue() == 7.7

    def test_value_and_getValue_are_synced(self):
        n = PyIndi.INumber("N1")
        n.value = 5.0
        assert n.getValue() == 5.0
        n.setValue(3.0)
        assert n.value == 3.0

    def test_name_label_min_max(self):
        n = PyIndi.INumber("N1", "Number One", 5.0, 0.0, 100.0, 0.5)
        assert n.getName()  == "N1"
        assert n.getLabel() == "Number One"
        assert n.min  == 0.0
        assert n.max  == 100.0
        assert n.step == 0.5


# ============================================================================
# IText widget
# ============================================================================

class TestIText:
    def test_default_empty(self):
        t = PyIndi.IText("T1")
        assert t.getText() == ""
        assert t.text == ""

    def test_set_text_via_method(self):
        t = PyIndi.IText("T1")
        t.setText("hello")
        assert t.getText() == "hello"
        assert t.text == "hello"

    def test_set_text_via_attribute(self):
        t = PyIndi.IText("T1")
        t.text = "world"
        assert t.getText() == "world"


# ============================================================================
# ILight widget
# ============================================================================

class TestILight:
    def test_default_idle(self):
        l = PyIndi.ILight("L1")
        assert l.getState() == PyIndi.IPS_IDLE
        assert l.getStateAsString() == "Idle"

    def test_set_ok_state(self):
        l = PyIndi.ILight("L1", state=PyIndi.IPS_OK)
        assert l.getStateAsString() == "Ok"

    def test_set_state_via_method(self):
        l = PyIndi.ILight("L1")
        l.setState(PyIndi.IPS_ALERT)
        assert l.getState() == PyIndi.IPS_ALERT
        assert l.getStateAsString() == "Alert"


# ============================================================================
# IBLOB widget
# ============================================================================

class TestIBLOB:
    def test_empty_blob(self):
        b = PyIndi.IBLOB("B1")
        assert b.getSize()   == 0
        assert b.getblob()   == b""
        assert b.getFormat() == ".fits"

    def test_set_blob(self):
        data = b"\x00\x01\x02"
        b = PyIndi.IBLOB("B1", blob=data)
        assert b.getSize()       == 3
        assert b.getblob()       == data
        assert b.getblobdata()   == bytearray(data)

    def test_set_blob_via_method(self):
        b = PyIndi.IBLOB("B1")
        b.setBlob(b"\xFF\xFF")
        assert b.getSize() == 2


# ============================================================================
# Vector property base
# ============================================================================

class TestBaseVectorProperty:
    def _make_vec(self):
        elements = [
            PyIndi.ISwitch("ENABLED",  "Enabled",  PyIndi.ISS_OFF),
            PyIndi.ISwitch("DISABLED", "Disabled", PyIndi.ISS_ON),
        ]
        return PyIndi.ISwitchVectorProperty("DEWAUTO", "Dew Auto", "Pegasus SPB",
                                            PyIndi.IPS_OK, elements)

    def test_len(self):
        vec = self._make_vec()
        assert len(vec) == 2

    def test_indexing(self):
        vec = self._make_vec()
        assert vec[0].name == "ENABLED"
        assert vec[1].name == "DISABLED"

    def test_index_out_of_bounds(self):
        vec = self._make_vec()
        with pytest.raises(IndexError):
            _ = vec[5]

    def test_iteration(self):
        vec = self._make_vec()
        names = [sw.name for sw in vec]
        assert names == ["ENABLED", "DISABLED"]

    def test_get_name_label_device(self):
        vec = self._make_vec()
        assert vec.getName()       == "DEWAUTO"
        assert vec.getLabel()      == "Dew Auto"
        assert vec.getDeviceName() == "Pegasus SPB"

    def test_state_as_string(self):
        vec = self._make_vec()
        assert vec.getStateAsString() == "Ok"

    def test_type_info(self):
        vec = self._make_vec()
        assert vec.getType()       == PyIndi.INDI_SWITCH
        assert vec.getTypeAsString() == "Switch"

    def test_find_widget_by_name(self):
        vec = self._make_vec()
        widget = vec.findWidgetByName("ENABLED")
        assert widget is not None
        assert widget.name == "ENABLED"

    def test_find_widget_not_found(self):
        vec = self._make_vec()
        assert vec.findWidgetByName("NONEXISTENT") is None

    def test_set_state(self):
        vec = self._make_vec()
        vec.setState(PyIndi.IPS_BUSY)
        assert vec.getState() == PyIndi.IPS_BUSY
        assert vec.getStateAsString() == "Busy"


# ============================================================================
# New-API PropertySwitch wrapper
# ============================================================================

class TestPropertySwitchWrapper:
    def _make_prop(self):
        elements = [PyIndi.ISwitch("ON", "On", PyIndi.ISS_ON),
                    PyIndi.ISwitch("OFF", "Off", PyIndi.ISS_OFF)]
        vec = PyIndi.ISwitchVectorProperty("TRACK", "Track", "Scope",
                                           PyIndi.IPS_OK, elements)
        return PyIndi.PropertySwitch(vec)

    def test_iteration(self):
        prop = self._make_prop()
        names = [w.name for w in prop]
        assert names == ["ON", "OFF"]

    def test_indexing(self):
        prop = self._make_prop()
        assert prop[0].name == "ON"

    def test_len(self):
        assert len(self._make_prop()) == 2

    def test_find_widget_by_name(self):
        prop = self._make_prop()
        widget = prop.findWidgetByName("OFF")
        assert widget is not None
        assert widget.name == "OFF"

    def test_metadata(self):
        prop = self._make_prop()
        assert prop.getName()        == "TRACK"
        assert prop.getLabel()       == "Track"
        assert prop.getDeviceName()  == "Scope"
        assert prop.getType()        == PyIndi.INDI_SWITCH
        assert prop.getTypeAsString() == "Switch"


class TestPropertyNumberWrapper:
    def _make_prop(self):
        elements = [PyIndi.INumber("RA", "RA", 5.5)]
        vec = PyIndi.INumberVectorProperty("COORD", "Coord", "Scope",
                                           PyIndi.IPS_OK, elements)
        return PyIndi.PropertyNumber(vec)

    def test_iteration(self):
        prop = self._make_prop()
        names = [w.name for w in prop]
        assert names == ["RA"]

    def test_type(self):
        assert self._make_prop().getType() == PyIndi.INDI_NUMBER


# ============================================================================
# BaseDevice
# ============================================================================

class TestBaseDevice:
    def _make_device(self):
        dev = PyIndi.BaseDevice("Test Device", "indi_test")
        dev._add_switch("MYSW", "My Switch", [
            PyIndi.ISwitch("SW_A", "A", PyIndi.ISS_OFF),
            PyIndi.ISwitch("SW_B", "B", PyIndi.ISS_ON),
        ])
        dev._add_number("MYNUM", "My Number", [
            PyIndi.INumber("VAL", "Value", 99.0),
        ])
        dev._add_text("MYTXT", "My Text", [
            PyIndi.IText("TXT1", "Text1", "hello"),
        ])
        return dev

    def test_name_and_driver(self):
        dev = self._make_device()
        assert dev.getDeviceName() == "Test Device"
        assert dev.getDriverName() == "indi_test"

    def test_get_switch(self):
        dev = self._make_device()
        sw = dev.getSwitch("MYSW")
        assert sw is not None
        assert sw.getName() == "MYSW"
        assert sw[1].name == "SW_B"

    def test_get_switch_not_found(self):
        dev = self._make_device()
        assert dev.getSwitch("NOEXIST") is None

    def test_get_number(self):
        dev = self._make_device()
        nv = dev.getNumber("MYNUM")
        assert nv is not None
        assert nv[0].getValue() == 99.0

    def test_get_text(self):
        dev = self._make_device()
        tv = dev.getText("MYTXT")
        assert tv is not None
        assert tv[0].getText() == "hello"

    def test_get_properties_returns_all(self):
        dev = self._make_device()
        props = dev.getProperties()
        names = [p.getName() for p in props]
        assert "MYSW"  in names
        assert "MYNUM" in names
        assert "MYTXT" in names

    def test_message_queue(self):
        dev = self._make_device()
        dev._add_message("Test message")
        assert dev.messageQueue(0) == "Test message"
        assert dev.messageQueue(1) == ""

    def test_message_queue_empty(self):
        dev = self._make_device()
        assert dev.messageQueue(0) == ""


# ============================================================================
# BaseClient
# ============================================================================

class IndiClient(PyIndi.BaseClient):
    """Minimal IndiClient for testing – mirrors the pattern in the real scripts."""
    def __init__(self):
        super().__init__()
    def newDevice(self, d):          pass
    def newProperty(self, p):        pass
    def removeProperty(self, p):     pass
    def newBLOB(self, bp):           pass
    def newSwitch(self, svp):        pass
    def newNumber(self, nvp):        pass
    def newText(self, tvp):          pass
    def newLight(self, lvp):         pass
    def newMessage(self, d, m):      pass
    def serverConnected(self):       pass
    def serverDisconnected(self, c): pass


class TestBaseClient:
    def test_connect_success(self):
        client = IndiClient()
        client.setServer("localhost", 7625)
        assert client.connectServer() is True

    def test_connect_failure(self):
        PyIndi._set_state(server_connected=False)
        client = IndiClient()
        client.setServer("localhost", 7625)
        assert client.connectServer() is False

    def test_get_host_port(self):
        client = IndiClient()
        client.setServer("192.168.1.1", 9000)
        assert client.getHost() == "192.168.1.1"
        assert client.getPort() == 9000

    def test_get_device_found(self):
        client = IndiClient()
        device = client.getDevice("iEQ")
        assert device is not None
        assert device.getDeviceName() == "iEQ"

    def test_get_device_not_found(self):
        client = IndiClient()
        assert client.getDevice("NONEXISTENT") is None

    def test_get_devices_returns_all(self):
        client = IndiClient()
        devices = client.getDevices()
        names = {d.getDeviceName() for d in devices}
        assert "iEQ" in names
        assert "Pegasus SPB" in names

    def test_send_new_switch_recorded(self):
        client = IndiClient()
        device = client.getDevice("iEQ")
        svp = device.getSwitch("HOME")
        svp[1].setState(PyIndi.ISS_ON)
        client.sendNewSwitch(svp)
        sent = PyIndi._get_sent_properties()
        assert len(sent) == 1
        assert sent[0].getName() == "HOME"

    def test_send_new_number_recorded(self):
        client = IndiClient()
        device = client.getDevice("iEQ")
        nvp = device.getNumber("EQUATORIAL_EOD_COORD")
        nvp[0].setValue(10.0)
        client.sendNewNumber(nvp)
        sent = PyIndi._get_sent_properties()
        assert len(sent) == 1
        assert sent[0].getName() == "EQUATORIAL_EOD_COORD"

    def test_clear_sent_properties(self):
        client = IndiClient()
        device = client.getDevice("Pegasus SPB")
        svp = device.getSwitch("DEWAUTO")
        client.sendNewSwitch(svp)
        PyIndi._clear_sent_properties()
        assert PyIndi._get_sent_properties() == []

    def test_disconnect_server_no_error(self):
        client = IndiClient()
        client.disconnectServer()  # should not raise

    def test_set_blob_mode_no_error(self):
        client = IndiClient()
        client.setBLOBMode(PyIndi.B_ALSO, "CCD Simulator", None)


# ============================================================================
# Default device: iEQ
# ============================================================================

class TestDefaultDeviceIEQ:
    def _get(self):
        client = IndiClient()
        return client.getDevice("iEQ")

    def test_device_exists(self):
        assert self._get() is not None

    def test_driver_name(self):
        assert self._get().getDriverName() == "indi_ioptronv3"

    def test_home_switch_has_three_elements(self):
        dev = self._get()
        home = dev.getSwitch("HOME")
        assert home is not None
        assert len(home) == 3

    def test_home_switch_element_names(self):
        dev = self._get()
        home = dev.getSwitch("HOME")
        assert home[0].name == "SET_CURRENT_AS_HOME"
        assert home[1].name == "GO_HOME"
        assert home[2].name == "FIND_HOME"

    def test_go_home_set_via_dot_s(self):
        """Mirrors the pattern in iEQ_scope_go_home_indi.py."""
        dev = self._get()
        home = dev.getSwitch("HOME")
        home[1].s = 1
        assert home[1].getState() == PyIndi.ISS_ON

    def test_equatorial_coord_ra_dec(self):
        dev = self._get()
        coord = dev.getNumber("EQUATORIAL_EOD_COORD")
        assert len(coord) == 2
        assert coord[0].name == "RA"
        assert coord[1].name == "DEC"

    def test_set_ra_dec(self):
        dev = self._get()
        coord = dev.getNumber("EQUATORIAL_EOD_COORD")
        coord[0].setValue(5.5)
        coord[1].setValue(-10.0)
        assert coord[0].getValue() == 5.5
        assert coord[1].getValue() == -10.0


# ============================================================================
# Default device: Pegasus SPB
# ============================================================================

class TestDefaultDevicePegasusSPB:
    def _get(self):
        client = IndiClient()
        return client.getDevice("Pegasus SPB")

    def test_device_exists(self):
        assert self._get() is not None

    def test_dewauto_switch_exists(self):
        dev = self._get()
        sw = dev.getSwitch("DEWAUTO")
        assert sw is not None
        assert len(sw) == 2

    def test_dewauto_element_names(self):
        dev = self._get()
        sw = dev.getSwitch("DEWAUTO")
        assert sw[0].name == "ENABLED"
        assert sw[1].name == "DISABLED"

    def test_set_dew_manual_via_setState(self):
        """Mirrors the pattern in pegasus_SPB_set_dews_AB_to_zero_indi.py."""
        dev = self._get()
        dewauto = dev.getSwitch("DEWAUTO")
        dewauto[0].setState(1)
        dewauto[1].setState(0)
        assert dewauto[0].getState() == PyIndi.ISS_ON
        assert dewauto[1].getState() == PyIndi.ISS_OFF
        assert dewauto[0].getStateAsString() == "On"
        assert dewauto[1].getStateAsString() == "Off"

    def test_dewauto_getlabel(self):
        dev = self._get()
        dewauto = dev.getSwitch("DEWAUTO")
        assert dewauto.getLabel() == "Dew Control Auto"

    def test_dewauto_getstateasstring(self):
        dev = self._get()
        dewauto = dev.getSwitch("DEWAUTO")
        assert dewauto.getStateAsString() == "Ok"

    def test_dew_pwm_numbers(self):
        dev = self._get()
        pwm = dev.getNumber("DEW_PWM")
        assert pwm is not None
        assert len(pwm) == 2
        assert pwm[0].name == "DEW_A"
        assert pwm[1].name == "DEW_B"

    def test_set_dew_power_to_zero(self):
        dev = self._get()
        pwm = dev.getNumber("DEW_PWM")
        pwm[0].setValue(0.0)
        pwm[1].setValue(0.0)
        assert pwm[0].getValue() == 0.0
        assert pwm[1].getValue() == 0.0


# ============================================================================
# Mock state helpers
# ============================================================================

class TestMockStateHelpers:
    def test_reset_state_restores_default_devices(self):
        PyIndi._devices.clear()
        PyIndi._reset_state()
        assert "iEQ" in PyIndi._devices
        assert "Pegasus SPB" in PyIndi._devices

    def test_reset_state_restores_server_connected(self):
        PyIndi._set_state(server_connected=False)
        PyIndi._reset_state()
        assert PyIndi._state["server_connected"] is True

    def test_reset_state_clears_sent_properties(self):
        client = IndiClient()
        dev = client.getDevice("iEQ")
        client.sendNewSwitch(dev.getSwitch("HOME"))
        PyIndi._reset_state()
        assert PyIndi._get_sent_properties() == []

    def test_set_state_server_connected(self):
        PyIndi._set_state(server_connected=False)
        assert PyIndi._state["server_connected"] is False

    def test_set_state_unknown_key_raises(self):
        with pytest.raises(KeyError):
            PyIndi._set_state(nonexistent_key=True)

    def test_add_custom_device(self):
        custom = PyIndi.BaseDevice("My Hub", "indi_my_hub")
        custom._add_switch("RELAY", elements=[PyIndi.ISwitch("R1", state=PyIndi.ISS_OFF)])
        PyIndi._add_device(custom)
        client = IndiClient()
        dev = client.getDevice("My Hub")
        assert dev is not None
        assert dev.getSwitch("RELAY")[0].name == "R1"

    def test_get_sent_properties_returns_copy(self):
        """Mutating the returned list must not affect internal state."""
        client = IndiClient()
        dev = client.getDevice("iEQ")
        client.sendNewSwitch(dev.getSwitch("HOME"))
        sent = PyIndi._get_sent_properties()
        sent.clear()
        assert len(PyIndi._get_sent_properties()) == 1


# ============================================================================
# Scenario: script pattern from pegasus_SPB_set_dews_AB_to_zero_indi.py
# ============================================================================

class TestPegasusScriptPattern:
    """Reproduce the exact call pattern used in the Pegasus script."""

    def test_full_script_flow(self):
        pa_spb = "Pegasus SPB"

        indiclient = IndiClient()
        indiclient.setServer("localhost", 7625)

        # Server must be reachable
        assert indiclient.connectServer() is True

        # Device must appear
        device_pa_spb = indiclient.getDevice(pa_spb)
        assert device_pa_spb is not None

        # Inspect the driver name (used in the script via print)
        assert isinstance(device_pa_spb.getDriverName(), str)

        # Get the DEWAUTO switch – the script accesses [0] and [1]
        dewauto = device_pa_spb.getSwitch("DEWAUTO")
        assert dewauto is not None

        # getStateAsString / getLabel / dir() equivalent
        assert isinstance(dewauto.getStateAsString(), str)
        assert isinstance(dewauto.getLabel(), str)

        # Element introspection used by the script
        e0 = dewauto[0]
        e1 = dewauto[1]
        assert isinstance(e0.getState(), int)
        assert isinstance(e0.getStateAsString(), str)

        # Set manual mode (script replicates this exact sequence)
        e0.setState(1)
        e1.setState(0)
        assert e0.getState() == PyIndi.ISS_ON
        assert e1.getState() == PyIndi.ISS_OFF


# ============================================================================
# Scenario: script pattern from iEQ_scope_go_home_indi.py
# ============================================================================

class TestIEQScriptPattern:
    """Reproduce the exact call pattern used in the iEQ go-home script."""

    def test_full_script_flow(self):
        indiclient = IndiClient()
        indiclient.setServer("localhost", 7625)
        assert indiclient.connectServer() is True

        device_mount = indiclient.getDevice("iEQ")
        assert device_mount is not None

        mount_home = device_mount.getSwitch("HOME")
        assert mount_home is not None

        # Legacy attribute assignment: mount_home_operation[1].s = 1
        mount_home[1].s = 1
        assert mount_home[1].getState() == PyIndi.ISS_ON

        indiclient.sendNewSwitch(mount_home)
        sent = PyIndi._get_sent_properties()
        assert len(sent) == 1
        assert sent[0].getName() == "HOME"
        assert sent[0][1].getState() == PyIndi.ISS_ON
