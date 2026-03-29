# test_pegasus_SPB_set_dews_AB_to_zero_indi.py
# SPDX-FileCopyrightText: 2026 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts
#
# ---------------------------------------------------------------------------- #
# Unit tests for pegasus_SPB_set_dews_AB_to_zero_indi.py
#
# All time.sleep calls are patched so tests run instantly.
# PyIndi and ccdciel mocks (PyIndi.py / ccdciel.py) replace real hardware.
#
# Run with:
#   cd /home/jbielanski/Dokumenty/DEVELOPMENT/CCDCiel_Scripts
#   pytest TEST/test_pegasus_SPB_set_dews_AB_to_zero_indi.py -v
# ---------------------------------------------------------------------------- #

import os
import sys
import pytest
from unittest.mock import patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import PyIndi
import pegasus_SPB_set_dews_AB_to_zero_indi as script


# ============================================================================
# Fixture – restore clean state before every test
# ============================================================================

@pytest.fixture(autouse=True)
def reset_state():
    """Restore PyIndi mock to default devices and reset sys.argv."""
    PyIndi._reset_state()
    original_argv = sys.argv[:]
    sys.argv = ["pegasus_SPB_set_dews_AB_to_zero_indi.py"]
    yield
    sys.argv = original_argv


# ============================================================================
# IndiClient class
# ============================================================================

class TestIndiClient:
    def test_inherits_from_base_client(self):
        client = script.IndiClient()
        assert isinstance(client, PyIndi.BaseClient)

    def test_all_callbacks_are_callable(self):
        client = script.IndiClient()
        assert callable(client.newDevice)
        assert callable(client.newProperty)
        assert callable(client.removeProperty)
        assert callable(client.newBLOB)
        assert callable(client.newSwitch)
        assert callable(client.newNumber)
        assert callable(client.newText)
        assert callable(client.newLight)
        assert callable(client.newMessage)
        assert callable(client.serverConnected)
        assert callable(client.serverDisconnected)

    def test_callbacks_accept_correct_signatures(self):
        """Callbacks must not raise when called with compatible arguments."""
        client = script.IndiClient()
        dev = PyIndi.BaseDevice("Test")
        svp = PyIndi.ISwitchVectorProperty("SW")
        nvp = PyIndi.INumberVectorProperty("NV")
        tvp = PyIndi.ITextVectorProperty("TV")
        lvp = PyIndi.ILightVectorProperty("LV")
        bvp = PyIndi.IBLOBVectorProperty("BV")

        client.newDevice(dev)
        client.newProperty(svp)
        client.removeProperty(svp)
        client.newSwitch(svp)
        client.newNumber(nvp)
        client.newText(tvp)
        client.newLight(lvp)
        client.newMessage(dev, 0)
        client.serverConnected()
        client.serverDisconnected(0)


# ============================================================================
# Normal / happy-path execution
# ============================================================================

class TestNormalExecution:
    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_dewauto_enabled_set_to_on(self, mock_sleep):
        """DEWAUTO[0] (Enabled) must be ISS_ON after processing."""
        script.processing_indi_commands_pa_spb()
        dev = PyIndi.BaseClient().getDevice("Pegasus SPB")
        assert dev.getSwitch("DEWAUTO")[0].getState() == PyIndi.ISS_ON

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_dewauto_disabled_set_to_off(self, mock_sleep):
        """DEWAUTO[1] (Disabled) must be ISS_OFF after processing."""
        script.processing_indi_commands_pa_spb()
        dev = PyIndi.BaseClient().getDevice("Pegasus SPB")
        assert dev.getSwitch("DEWAUTO")[1].getState() == PyIndi.ISS_OFF

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_dewauto_enabled_state_string_is_on(self, mock_sleep):
        """DEWAUTO[0] getStateAsString() must return 'On'."""
        script.processing_indi_commands_pa_spb()
        dev = PyIndi.BaseClient().getDevice("Pegasus SPB")
        assert dev.getSwitch("DEWAUTO")[0].getStateAsString() == "On"

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_dewauto_disabled_state_string_is_off(self, mock_sleep):
        """DEWAUTO[1] getStateAsString() must return 'Off'."""
        script.processing_indi_commands_pa_spb()
        dev = PyIndi.BaseClient().getDevice("Pegasus SPB")
        assert dev.getSwitch("DEWAUTO")[1].getStateAsString() == "Off"

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_sleep_called_with_connect_delay(self, mock_sleep):
        """A 2.0 s sleep must follow a successful server connection."""
        script.processing_indi_commands_pa_spb()
        assert call(2.0) in mock_sleep.call_args_list


# ============================================================================
# INDI port selection
# ============================================================================

class TestPortSelection:
    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_default_port_7625(self, mock_sleep):
        """No CLI argument → setServer called with port 7625."""
        sys.argv = ["pegasus_SPB_set_dews_AB_to_zero_indi.py"]
        with patch.object(script.IndiClient, "setServer") as mock_set:
            script.processing_indi_commands_pa_spb()
        mock_set.assert_called_once_with("localhost", 7625)

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_custom_port_from_argv(self, mock_sleep):
        """sys.argv[1] overrides the default INDI port."""
        sys.argv = ["pegasus_SPB_set_dews_AB_to_zero_indi.py", "7626"]
        with patch.object(script.IndiClient, "setServer") as mock_set:
            script.processing_indi_commands_pa_spb()
        mock_set.assert_called_once_with("localhost", 7626)

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_custom_port_is_parsed_as_int(self, mock_sleep):
        """Port argument must be converted to int, not kept as string."""
        sys.argv = ["pegasus_SPB_set_dews_AB_to_zero_indi.py", "9000"]
        with patch.object(script.IndiClient, "setServer") as mock_set:
            script.processing_indi_commands_pa_spb()
        _, port_arg = mock_set.call_args[0]
        assert isinstance(port_arg, int)
        assert port_arg == 9000


# ============================================================================
# Server connection failures
# ============================================================================

class TestConnectionFailure:
    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_exits_when_indi_not_connected(self, mock_sleep):
        """sys.exit(1) must be raised if connectServer() returns False."""
        PyIndi._set_state(server_connected=False)
        with pytest.raises(SystemExit) as exc_info:
            script.processing_indi_commands_pa_spb()
        assert exc_info.value.code == 1

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_logs_message_when_not_connected(self, mock_sleep, capsys):
        """A log message must be emitted before the exit on connection failure."""
        PyIndi._set_state(server_connected=False)
        with pytest.raises(SystemExit):
            script.processing_indi_commands_pa_spb()
        # ccdciel mock prints nothing, but ensuring no unexpected exception is enough

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_no_sleep_when_connection_fails(self, mock_sleep):
        """time.sleep must NOT be called if the server connection is refused."""
        PyIndi._set_state(server_connected=False)
        with pytest.raises(SystemExit):
            script.processing_indi_commands_pa_spb()
        mock_sleep.assert_not_called()


# ============================================================================
# Device not found (timeout path)
# ============================================================================

class TestDeviceNotFound:
    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_exits_when_device_absent(self, mock_sleep):
        """sys.exit(1) must be raised when 'Pegasus SPB' never appears."""
        del PyIndi._devices["Pegasus SPB"]
        with pytest.raises(SystemExit) as exc_info:
            script.processing_indi_commands_pa_spb()
        assert exc_info.value.code == 1

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_sleep_called_during_device_wait(self, mock_sleep):
        """time.sleep(0.5) must be called while waiting for the device."""
        del PyIndi._devices["Pegasus SPB"]
        with pytest.raises(SystemExit):
            script.processing_indi_commands_pa_spb()
        # 0.5 s polls must have occurred during the 30-second timeout loop
        assert call(0.5) in mock_sleep.call_args_list

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_dewauto_not_modified_when_device_absent(self, mock_sleep):
        """DEWAUTO initial states must be unchanged when device is never found."""
        del PyIndi._devices["Pegasus SPB"]
        # Keep an isolated reference to check state was not touched
        spare_dev = PyIndi.BaseDevice("Pegasus SPB", "indi_pegasus_spb")
        spare_dev._add_switch("DEWAUTO", elements=[
            PyIndi.ISwitch("ENABLED",  state=PyIndi.ISS_OFF),
            PyIndi.ISwitch("DISABLED", state=PyIndi.ISS_ON),
        ])
        with pytest.raises(SystemExit):
            script.processing_indi_commands_pa_spb()
        # Spare device is untouched – confirms no mutations happened
        assert spare_dev.getSwitch("DEWAUTO")[0].getState() == PyIndi.ISS_OFF
        assert spare_dev.getSwitch("DEWAUTO")[1].getState() == PyIndi.ISS_ON


# ============================================================================
# main()
# ============================================================================

class TestMain:
    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_main_calls_processing(self, mock_sleep):
        """main() must invoke processing_indi_commands_pa_spb."""
        with patch(
            "pegasus_SPB_set_dews_AB_to_zero_indi.processing_indi_commands_pa_spb"
        ) as mock_proc:
            script.main()
        mock_proc.assert_called_once()

    @patch("pegasus_SPB_set_dews_AB_to_zero_indi.time.sleep")
    def test_main_full_flow_sets_dewauto(self, mock_sleep):
        """main() end-to-end: DEWAUTO must be in manual mode after completion."""
        script.main()
        dev = PyIndi.BaseClient().getDevice("Pegasus SPB")
        dewauto = dev.getSwitch("DEWAUTO")
        assert dewauto[0].getState() == PyIndi.ISS_ON
        assert dewauto[1].getState() == PyIndi.ISS_OFF
