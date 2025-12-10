@echo off
REM Modbus Capture and Decode Workflow Script
REM For Sungrow Logger 192.168.1.5

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo Sungrow Modbus Capture and Analysis Workflow
echo ============================================================
echo.
echo This script helps you:
echo 1. Capture raw Modbus TCP traffic to/from 192.168.1.5
echo 2. Extract Modbus frames from the capture
echo 3. Analyze and generate register mapping
echo.

:menu
echo.
echo Select an operation:
echo 1 - Start Wireshark capture
echo 2 - Extract Modbus frames from PCAP
echo 3 - Analyze and generate register map
echo 4 - View capture samples
echo 5 - Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto capture
if "%choice%"=="2" goto extract
if "%choice%"=="3" goto analyze
if "%choice%"=="4" goto samples
if "%choice%"=="5" goto end

echo Invalid choice
goto menu

:capture
echo.
echo Starting Wireshark with Modbus filter...
echo Filter: tcp port 502 and host 192.168.1.5
echo.
echo This will capture Modbus TCP traffic to/from the Sungrow logger.
echo You may need to:
echo  - Switch Wireshark interface if Ethernet isn't correct
echo  - Wait for PCVue to start communicating with the logger
echo  - Stop capture manually when done (Ctrl+E or button)
echo.
set /p start="Press Enter to start..."

REM Start Wireshark if available
where wireshark >nul 2>&1
if %ERRORLEVEL% equ 0 (
    start wireshark -i Ethernet -f "tcp port 502 and host 192.168.1.5"
) else (
    echo Wireshark not found in PATH
    echo Trying default installation location...
    if exist "C:\Program Files\Wireshark\wireshark.exe" (
        start "C:\Program Files\Wireshark\wireshark.exe" -i Ethernet -f "tcp port 502 and host 192.168.1.5"
    ) else (
        echo Wireshark not found. Please install it or run manually.
    )
)
goto menu

:extract
echo.
echo Extract Modbus frames from capture file
echo.
echo Available captures in .\captures\ directory:
dir .\captures\ /b 2>nul
if %ERRORLEVEL% neq 0 (
    echo No captures found in .\captures\ directory
    goto menu
)
echo.
set /p pcapfile="Enter capture filename (e.g., modbus_20251210_1430.pcapng): "

if not exist ".\captures\%pcapfile%" (
    echo File not found: .\captures\%pcapfile%
    goto menu
)

set "jsonfile=extracted_%pcapfile:~0,-7%.json"
echo.
echo Extracting frames from .\captures\%pcapfile%...
echo Output: %jsonfile%
echo.

python pcap_extractor.py ".\captures\%pcapfile%" "%jsonfile%"

if %ERRORLEVEL% equ 0 (
    echo.
    echo Successfully extracted frames!
    set /p open="Open in notepad? (y/n): "
    if /i "%open%"=="y" notepad "%jsonfile%"
) else (
    echo Error during extraction
)

goto menu

:analyze
echo.
echo Analyze extracted frames and generate register map
echo.
echo Available frame extracts:
for %%f in (extracted_*.json) do echo  - %%f
echo.
set /p framefile="Enter frame file (e.g., extracted_modbus_20251210_1430.json): "

if not exist "%framefile%" (
    echo File not found: %framefile%
    goto menu
)

set "mapfile=register_map_%framefile:~10,-5%.json"
echo.
echo Analyzing frames and generating mapping suggestions...
echo Output: %mapfile%
echo.

REM Python would analyze the extracted frames and generate mapping
echo This requires the ModbusDecoder to process the extracted frames.
echo File will be saved as: %mapfile%

set /p view="View register mapping? (y/n): "
if /i "%view%"=="y" notepad "%mapfile%"

goto menu

:samples
echo.
echo Sample Modbus TCP Frames (Raw Hex)
echo ===================================
echo.
echo Read Holding Registers (Function 3):
echo   Transaction ID: 00 01
echo   Protocol ID:    00 00
echo   Length:         00 06
echo   Unit ID:        01
echo   Function:       03 (Read Holding Registers)
echo   Start Address:  00 0A
echo   Quantity:       00 02
echo   Frame: 00 01 00 00 00 06 01 03 00 0A 00 02
echo.
echo Write Single Register (Function 6):
echo   Transaction ID: 00 02
echo   Protocol ID:    00 00
echo   Length:         00 06
echo   Unit ID:        01
echo   Function:       06 (Write Single Register)
echo   Register:       00 14
echo   Value:          12 34
echo   Frame: 00 02 00 00 00 06 01 06 00 14 12 34
echo.
echo Expected Sungrow Logger Registers:
echo   0000-0050: Inverter Info (model, serial, firmware)
echo   0100-0199: Grid/AC Data (voltages, currents, power)
echo   0200-0299: DC/PV Input (PV voltages, currents)
echo   0300-0399: Weather Station (temp, humidity, irradiance)
echo   0500-0599: Energy Counters (daily/total energy)
echo   1000+:     Faults and Alarms
echo.
pause
goto menu

:end
echo.
echo Goodbye!
echo.
endlocal
