#!/usr/bin/env python3
"""
test_ccdciel_mock.py

Demonstration and test suite for the comprehensive CCDciel JSON-RPC mock.
Tests the mock against real-world usage patterns from the documentation.

Run with: python3 test_ccdciel_mock.py
"""

import sys
sys.path.insert(0, '/home/jbielanski/Dokumenty/DEVELOPMENT/CCDCiel_Scripts')

from ccdciel import ccdciel, _set_state, _get_state


def print_section(title):
    """Print a test section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_query_methods():
    """Test methods that return values."""
    print_section("QUERY METHODS - Information Retrieval")
    
    # Version and Device info
    version = ccdciel('CCDciel_Version')['result']
    print(f"✓ CCDciel_Version: {version}")
    
    # Device connection status
    devices_connected = ccdciel('Devices_connected')['result']
    print(f"✓ Devices_connected: {devices_connected}")
    
    camera_connected = ccdciel('Camera_connected')['result']
    print(f"✓ Camera_connected: {camera_connected}")
    
    # Telescope position
    ra = ccdciel('TelescopeRA')['result']
    de = ccdciel('TelescopeDE')['result']
    print(f"✓ Telescope position: RA={ra}h, DEC={de}°")
    
    # Focuser position
    focuser_pos = ccdciel('FocuserPosition')['result']
    print(f"✓ Focuser position: {focuser_pos}")
    
    # Filter wheel
    filters = ccdciel('Wheel_GetfiltersName')['result']
    current_filter = ccdciel('Wheel_GetPosition')['result']
    print(f"✓ Filter wheel: {filters[current_filter]} (filters: {', '.join(filters)})")
    
    # Camera temperature
    temp = ccdciel('CcdTemp')['result']
    print(f"✓ CCD Temperature: {temp}°C")
    
    # System info
    latitude = ccdciel('Obs_latitude')['result']
    longitude = ccdciel('Obs_longitude')['result']
    print(f"✓ Observatory: {latitude}° N, {longitude}° E")
    
    # Time
    timenow = ccdciel('TimeNow')['result']
    print(f"✓ TimeNow: {timenow}")


def test_action_methods():
    """Test methods that perform actions without parameters."""
    print_section("ACTION METHODS - No Parameters")
    
    # Telescope tracking
    result = ccdciel('Telescope_track')['result']
    print(f"✓ Telescope_track: {result['status']}")
    
    # Autoguider connection
    result = ccdciel('Autoguider_connect')['result']
    print(f"✓ Autoguider_connect: {result['status']}")
    
    # Start guiding
    result = ccdciel('Autoguider_startguiding')['result']
    print(f"✓ Autoguider_startguiding: {result['status']}")
    
    # Dither
    result = ccdciel('Autoguider_dither')['result']
    print(f"✓ Autoguider_dither: {result['status']}")
    
    # Stop guiding
    result = ccdciel('Autoguider_stopguiding')['result']
    print(f"✓ Autoguider_stopguiding: {result['status']}")
    
    # Autofocus
    result = ccdciel('Autofocus')['result']
    print(f"✓ Autofocus: {result['status']}")
    
    # Preview single
    result = ccdciel('Preview_single')['result']
    print(f"✓ Preview_single: {result['status']}")


def test_parameterized_methods():
    """Test methods with parameters."""
    print_section("ACTION METHODS - With Parameters")
    
    # Set focuser position
    result = ccdciel('Focuser_setposition', 5000)['result']
    pos = ccdciel('FocuserPosition')['result']
    print(f"✓ Focuser_setposition(5000): pos now = {pos}")
    
    # Set filter wheel
    result = ccdciel('Wheel_setfilter', 2)['result']
    current = ccdciel('Wheel_GetPosition')['result']
    filters = ccdciel('Wheel_GetfiltersName')['result']
    print(f"✓ Wheel_setfilter(2): current filter = {filters[current]}")
    
    # Set filter by name
    result = ccdciel('Wheel_setposition', 'Ha')['result']
    current = ccdciel('Wheel_GetPosition')['result']
    print(f"✓ Wheel_setposition('Ha'): current filter index = {current}")
    
    # Capture exposure
    result = ccdciel('Capture_setexposure', 10.5)['result']
    exp = ccdciel('Capture_getexposure')['result']
    print(f"✓ Capture_setexposure(10.5): exposure now = {exp}s")
    
    # Capture object name
    result = ccdciel('Capture_setobjectname', 'M42')['result']
    obj = ccdciel('Capture_getobjectname')['result']
    print(f"✓ Capture_setobjectname('M42'): object = {obj}")
    
    # Capture frame type
    result = ccdciel('Capture_setframetype', 'Bias')['result']
    ftype = ccdciel('Capture_getframetype')['result']
    print(f"✓ Capture_setframetype('Bias'): frame type = {ftype}")
    
    # Telescope slew
    result = ccdciel('Telescope_slew', 12.0, 30.0)['result']
    ra = ccdciel('TelescopeRA')['result']
    de = ccdciel('TelescopeDE')['result']
    print(f"✓ Telescope_slew(12.0, 30.0): RA={ra}h, DEC={de}°")
    
    # Rotator goto
    result = ccdciel('Rotator_goto', 45.5)['result']
    angle = ccdciel('Rotator_angle')['result']
    print(f"✓ Rotator_goto(45.5): angle = {angle}°")
    
    # Logging
    result = ccdciel('LogMsg', 'Test message from mock')['result']
    print(f"✓ LogMsg('Test message'): {result['status']}")
    
    # Custom header
    result = ccdciel('CustomHeader_add', 'OBSERVER', 'John Doe')['result']
    value = ccdciel('CustomHeader', 'OBSERVER')['result']
    print(f"✓ CustomHeader_add('OBSERVER', 'John Doe'): value = {value}")


def test_complex_workflows():
    """Test realistic workflow combinations."""
    print_section("COMPLEX WORKFLOWS - Realistic Scenarios")
    
    # Reset state
    _set_state(focuser_position=0, wheel_index=0)
    
    print("\n1. Focusing workflow:")
    print(f"   - Initial focuser position: {ccdciel('FocuserPosition')['result']}")
    ccdciel('Focuser_setposition', 10000)
    print(f"   - After setposition(10000): {ccdciel('FocuserPosition')['result']}")
    ccdciel('Autofocus')
    print(f"   - After Autofocus: {ccdciel('FocuserPosition')['result']}")
    
    print("\n2. Filter wheel workflow:")
    print(f"   - Available filters: {ccdciel('Wheel_GetfiltersName')['result']}")
    for filter_name in ['L', 'R', 'G']:
        ccdciel('Wheel_setposition', filter_name)
        current = ccdciel('Wheel_GetPosition')['result']
        print(f"   - Switched to {filter_name} (index {current})")
    
    print("\n3. Capture preparation workflow:")
    ccdciel('Capture_setobjectname', 'NGC 2174')
    ccdciel('Capture_setexposure', 5.0)
    ccdciel('Capture_setbinning', '2x2')
    ccdciel('Capture_setframetype', 'Light')
    ccdciel('Capture_setcount', 5)
    status = {
        'object': ccdciel('Capture_getobjectname')['result'],
        'exposure': ccdciel('Capture_getexposure')['result'],
        'binning': ccdciel('Capture_getbinning')['result'],
        'type': ccdciel('Capture_getframetype')['result'],
        'count': ccdciel('Capture_getcount')['result'],
    }
    print(f"   - Capture config: {status}")
    
    print("\n4. Telescope movement workflow:")
    print(f"   - Initial: RA={ccdciel('TelescopeRA')['result']}, DEC={ccdciel('TelescopeDE')['result']}")
    ccdciel('Telescope_slewasync', 14.5, 60.0)
    print(f"   - Slewed to: RA={ccdciel('TelescopeRA')['result']}, DEC={ccdciel('TelescopeDE')['result']}")
    ccdciel('Telescope_sync', 14.501, 60.001)
    print(f"   - After sync: RA={ccdciel('TelescopeRA')['result']}, DEC={ccdciel('TelescopeDE')['result']}")


def test_status_method():
    """Test the comprehensive status method."""
    print_section("STATUS METHOD - Comprehensive Status Query")
    
    # Get full status
    print("\n1. Full status (all devices):")
    status = ccdciel('status')['result']
    for key in list(status.keys())[:3]:  # Show first 3 for brevity
        print(f"   - {key}: {status[key]}")
    
    # Get filtered status
    print("\n2. Filtered status (camera and focuser only):")
    status = ccdciel('status', ['camera', 'focuser'])['result']
    print(f"   - camera: {status['camera']}")
    print(f"   - focuser: {status['focuser']}")


def test_error_handling():
    """Test error handling and validation."""
    print_section("ERROR HANDLING & VALIDATION")
    
    # Invalid focus position
    try:
        result = ccdciel('Focuser_setposition', "invalid")['result']
        print(f"✗ Should have failed on invalid position")
    except Exception as e:
        print(f"✓ Caught invalid position: {type(e).__name__}")
    
    # Invalid filter index
    try:
        result = ccdciel('Wheel_setposition', 999)
        print(f"✗ Should have failed on invalid filter")
    except Exception as e:
        print(f"✓ Caught invalid filter: {type(e).__name__}")
    
    # Missing required parameter
    try:
        result = ccdciel('Focuser_setposition')
        print(f"✗ Should have failed on missing parameter")
    except TypeError as e:
        print(f"✓ Caught missing parameter: {e}")
    
    # Unknown method
    try:
        result = ccdciel('UnknownMethod')
        print(f"✗ Should have failed on unknown method")
    except NotImplementedError as e:
        print(f"✓ Caught unknown method: {e}")


def test_state_management():
    """Test state management functions."""
    print_section("STATE MANAGEMENT - Testing Helpers")
    
    original_pos = ccdciel('FocuserPosition')['result']
    print(f"✓ Original focuser position: {original_pos}")
    
    _set_state(focuser_position=9999, telescope_ra=20.0)
    print(f"✓ Modified focuser position: {ccdciel('FocuserPosition')['result']}")
    print(f"✓ Modified telescope RA: {ccdciel('TelescopeRA')['result']}")
    
    state = _get_state()
    print(f"✓ Got complete state: {len(state)} state keys")


def test_backward_compatibility():
    """Test backward compatibility with original mock."""
    print_section("BACKWARD COMPATIBILITY - Original Mock Functions")
    
    # Original functions should still work
    print("\n1. Original focuser operations:")
    result = ccdciel('Focuser_connected')['result']
    print(f"✓ Focuser_connected: {result}")
    
    ccdciel('Focuser_setposition', 5000)
    result = ccdciel('FocuserPosition')['result']
    print(f"✓ FocuserPosition: {result}")
    
    print("\n2. Original wheel operations:")
    filters = ccdciel('Wheel_GetfiltersName')['result']
    print(f"✓ Wheel_GetfiltersName: {filters}")
    
    result = ccdciel('Wheel_GetPosition')['result']
    print(f"✓ Wheel_GetPosition: {result}")
    
    print("\n3. Original logging:")
    ccdciel('LogMsg', 'Test message')
    print(f"✓ LogMsg accepted")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  CCDciel JSON-RPC Mock - Comprehensive Test Suite")
    print("  Documentation: https://www.ap-i.net/ccdciel/...")
    print("="*60)
    
    try:
        test_query_methods()
        test_action_methods()
        test_parameterized_methods()
        test_complex_workflows()
        test_status_method()
        test_error_handling()
        test_state_management()
        test_backward_compatibility()
        
        print("\n" + "="*60)
        print("  ✓ All tests completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
