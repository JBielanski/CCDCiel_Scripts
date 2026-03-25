"""
ccdciel.py
SPDX-FileCopyrightText: 2026 Jan Bielanski
SPDX-License-Identifier: GPL-3.0-or-later
https://github.com/JBielanski/CCDCiel_Scripts

Mock of CCDciel JSON-RPC interface used for local testing.

This mock implements a simple `ccdciel(method, *params)` function that
returns dict-like responses similar to the real JSON-RPC wrapper used in
`focuser_position_per_filter.py`.

It implements the subset of methods used in the example script plus a
few helpers from the JSON-RPC reference so it's easy to expand.

The mock keeps an internal state for focuser position and wheel filters.
"""

from typing import Any, Dict, List
import copy

# Internal mock state
_state = {
    "focuser_connected": True,
    "wheel_connected": True,
    "focuser_position": 0,
    "filters": ["L", "R", "G", "B", "Ha"],
    # simulate filter wheel current index (0-based)
    "wheel_index": 0,
    # captured log messages for tests
    "logs": [],
}


def _result(value: Any) -> Dict[str, Any]:
    """Return a JSON-RPC like result container for compatibility."""
    return {"result": copy.deepcopy(value)}


def ccdciel(method: str, *params) -> Dict[str, Any]:
    """Mock entry point. Call with the same signature as the real wrapper.

    Examples:
      ccdciel('Focuser_connected') -> {'result': True}
      ccdciel('Focuser_setposition', 100) -> {'result': None}
    """
    m = method

    # Connection checks
    if m == 'Focuser_connected':
        return _result(_state['focuser_connected'])
    if m == 'Wheel_connected':
        return _result(_state['wheel_connected'])

    # Focuser operations
    if m == 'FocuserPosition':
        return _result(int(_state['focuser_position']))

    if m == 'Focuser_setposition':
        if not _state['focuser_connected']:
            raise RuntimeError('Focuser not connected')
        if not params:
            raise TypeError('Focuser_setposition expects a position argument')
        try:
            pos = int(params[0])
        except Exception:
            raise TypeError('Position must be an integer')
        # Simulate move: set immediately
        _state['focuser_position'] = pos
        return _result(None)

    # Wheel operations
    if m == 'Wheel_GetfiltersName':
        return _result(list(_state['filters']))

    if m == 'Wheel_GetPosition':
        return _result(int(_state['wheel_index']))

    if m == 'Wheel_SetPosition':
        if not params:
            raise TypeError('Wheel_SetPosition expects an index or filter name')
        arg = params[0]
        if isinstance(arg, int):
            idx = arg
            if idx < 0 or idx >= len(_state['filters']):
                raise IndexError('Filter index out of range')
            _state['wheel_index'] = idx
            return _result(None)
        else:
            # try treat as name
            try:
                idx = _state['filters'].index(str(arg))
            except ValueError:
                raise ValueError('Filter name not found')
            _state['wheel_index'] = idx
            return _result(None)

    # Logging helper (no-op)
    if m == 'LogMsg':
        # Emulate returning None but accept variable args
        msg = params[0] if params else ''
        # store log message in state for test assertions
        _state['logs'].append(str(msg))
        print(f"[ccdciel mock LogMsg] {msg}")
        return _result(None)

    # Retrieve captured logs for testing
    if m == 'GetLogs':
        return _result(list(_state['logs']))

    # Autoguider/autofocus placeholder
    if m == 'Autofocus_Start':
        # Pretend autofocus finds best focus near current + 10
        best = _state['focuser_position'] + 10
        _state['focuser_position'] = best
        return _result(best)
    
    # CCDciel_Version
    if m == 'CCDciel_Version':
        # Return a mock version tuple
        return _result(["0.9.93", "3961", "0.9.93_3961"])

    # Unknown method: raise for visibility in tests
    raise NotImplementedError(f"Mock: Method '{m}' is not implemented")


# Small convenience to allow tests to reset/mock state
def _set_state(**kwargs):
    for k, v in kwargs.items():
        if k in _state:
            _state[k] = v


def _get_state() -> Dict[str, Any]:
    return copy.deepcopy(_state)
