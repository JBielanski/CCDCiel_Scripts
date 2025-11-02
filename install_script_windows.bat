@echo off
REM Script to install focuser_position_per_filter script in CCDciel
REM (C) 2025 Jan Bielanski

echo Creating script file...
copy /Y focuser_position_per_filter.py focuser_position_per_filter.script
if errorlevel 1 (
    echo Error: Failed to create script file
    exit /b 1
)

echo Installing script in CCDciel directory...
if not exist "%APPDATA%\ccdciel" (
    echo Error: Failed to CCDciel directory does not exist
    exit /b 1
)

copy /Y focuser_position_per_filter.script "%APPDATA%\ccdciel\"
if errorlevel 1 (
    echo Error: Failed to install script
    exit /b 1
)

echo.
echo Script installed successfully!
echo Location: %APPDATA%\ccdciel\focuser_position_per_filter.script
echo.

dir /B "%APPDATA%\ccdciel\focuser_position_per_filter.script"