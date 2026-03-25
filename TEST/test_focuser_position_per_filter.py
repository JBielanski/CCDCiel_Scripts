# test_focuser_position_per_filter.py
# SPDX-FileCopyrightText: 2026 Jan Bielanski
# SPDX-License-Identifier: GPL-3.0-or-later
# https://github.com/JBielanski/CCDCiel_Scripts

import os
import sys
import pytest

# allow direct import when tests run from TEST/ subdir
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ccdciel
from ccdciel import ccdciel as ccd
import focuser_position_per_filter as fp


def setup_function():
    # Make sure mock state is in a known base state before each test.
    ccdciel_module = ccdciel
    ccdciel_module._set_state(focuser_connected=True, wheel_connected=True, focuser_position=0, wheel_index=0, filters=['L', 'R', 'G', 'B', 'Ha'])
    # reset script global variables to defaults
    fp.script_working_mode = 0
    fp.initial_focuser_position = 0
    fp.filter_name_to_set = ['', 0, None, None]
    fp.filters_subset = []


def test_check_for_version_neq_0_9_93_3961():
    fp.ccdciel_version = ['0.9.93', '3961', '0.9.93_3961']
    assert fp.check_for_version_neq_0_9_93_3961(display_log=0) == 1

    fp.ccdciel_version = ['0.9.92', '3775', '0.9.92_3775']
    assert fp.check_for_version_neq_0_9_93_3961(display_log=0) == 0

    fp.ccdciel_version = ['1.0.0', '1000', '1.0.0_1000']
    assert fp.check_for_version_neq_0_9_93_3961(display_log=0) == 1


def test_arguments_parser_mode_and_subset_and_reference():
    old_argv = sys.argv
    sys.argv = ['focuser_position_per_filter.py', '--mode', 'READ', '--dbname', 'abc.db', '--subset', '[1,3]']

    try:
        fp.arguments_parser()
        assert fp.script_working_mode == 1
        assert fp.filters_and_focuser_positions_database_file == 'abc.db'
        assert fp.filters_subset == [1, 3]
    finally:
        sys.argv = old_argv


def test_store_and_get_database(tmp_path):
    db_name = 'test_focuser.db'
    db_dir = str(tmp_path)

    status = fp.store_position_per_filter_in_database(db_name, db_dir, 'L', 1500, 1, 0, 1)
    assert status == 0

    status, data = fp.get_focuser_position_for_filter_from_database(db_name, db_dir, 'L')
    assert status == 0
    assert data == [1500, 1, 0, 1]


def test_set_focuser_position_changes_position():
    ccdciel._set_state(focuser_position=10)

    status = fp.set_focuser_position(200)
    assert status == 0
    assert ccd('FocuserPosition')['result'] == 200


def test_main_in_test_mode():
    old_argv = sys.argv
    sys.argv = ['focuser_position_per_filter.py', '--mode', 'TEST']
    try:
        ret = fp.main()
        assert ret == 0
    finally:
        sys.argv = old_argv
