@echo off
REM Sungrow Modbus Capture Script
REM Captures Modbus TCP traffic to/from 192.168.1.5

echo Starting Modbus TCP capture from Sungrow Logger 192.168.1.5...
echo Filter: Modbus TCP traffic (port 502) to/from 192.168.1.5
echo.
echo Make sure Wireshark is available in PATH or installed in default location
echo.

REM Create output directory
if not exist "captures" mkdir captures

REM Get timestamp for filename
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set filename=captures\modbus_%mydate%_%mytime%.pcapng

REM Wireshark capture with Modbus filter
REM Filter captures Modbus TCP (port 502) traffic to/from the Sungrow logger
tshark -i Ethernet -f "tcp port 502 and (host 192.168.1.5)" -w "%filename%" -b duration:300 -b filesize:10000

echo.
echo Capture saved to: %filename%
echo.
echo To analyze with Modbus dissector, use:
echo   wireshark "%filename%"
