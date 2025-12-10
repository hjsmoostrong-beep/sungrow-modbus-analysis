# Sungrow Modbus Capture & Decode Toolkit

Complete toolkit for capturing, analyzing, and mapping Modbus TCP registers from a Sungrow Logger (192.168.1.5) connected to inverters and weather station.

## Quick Start

### 1. Capture Raw Modbus Traffic

Use the batch script to capture traffic from the Sungrow logger:

```batch
capture_modbus.bat
```

This will:
- Start capturing on interface `Ethernet`
- Filter for Modbus TCP (port 502) traffic to/from 192.168.1.5
- Auto-save to `captures\modbus_YYYYMMDD_HHMM.pcapng`
- Capture for 5 minutes (configurable)

**Alternative: Manual Wireshark Capture**
```
Display Filter: tcp.port == 502 and ip.addr == 192.168.1.5
Capture Filter: tcp port 502 and host 192.168.1.5
```

### 2. Extract Modbus Frames from Capture

```bash
python pcap_extractor.py captures\modbus_20251210_1430.pcapng extracted_frames.json
```

Output: JSON file with parsed Modbus TCP frames

### 3. Analyze and Generate Register Map

```bash
python modbus_pipeline.py captures\modbus_20251210_1430.pcapng sungrow_logger
```

This generates:
- `sungrow_logger_map.json` - Register mapping with grouping
- `sungrow_logger_report.txt` - Analysis report

### 4. Interactive Workflow (Optional)

```batch
workflow.bat
```

Menu-driven script for capture, extraction, analysis.

## File Structure

```
modbus/
├── README.md (this file)
├── capture_modbus.bat - Batch script to capture traffic
├── workflow.bat - Interactive workflow menu
├── modbus_decoder.py - Core decoder with heuristics
├── pcap_extractor.py - PCAP/PCAPNG reader
├── modbus_pipeline.py - End-to-end analysis pipeline
└── captures/ - Output directory for PCAP files
    └── modbus_*.pcapng
```

## How It Works

### Capture Phase
- **Tool**: Wireshark (tshark)
- **Target**: 192.168.1.5 (Sungrow logger)
- **Port**: 502 (Modbus TCP)
- **Output**: PCAPNG with all frames

### Analysis Phase

1. **Frame Extraction** (pcap_extractor.py)
   - Parses Ethernet/IP/TCP headers
   - Extracts Modbus TCP payload
   - Validates Modbus protocol
   - Outputs JSON

2. **Pattern Recognition** (modbus_decoder.py)
   - Identifies register access patterns
   - Groups registers by function
   - Applies Sungrow heuristics
   - Infers data types

3. **Mapping Generation**
   - Creates register suggestions
   - Groups by category:
     - Inverter Info (0-50)
     - Grid/AC Data (100-199)
     - DC/PV Input (200-299)
     - Weather Station (300-399)
     - Energy Counters (500-599)
     - Faults/Alarms (1000+)

## Register Mapping Features

### Automatic Grouping
Registers are organized by function based on address ranges:

```json
{
  "groups": {
    "Inverter_Info": [...],
    "Grid_AC_Data": [...],
    "DC_PV_Input": [...],
    "Weather_Station": [...],
    "Energy_Counters": [...],
    "Faults_Alarms": [...]
  }
}
```

### Heuristic Suggestions
- **Address ranges** → Function groups
- **Access frequency** → Importance rating
- **Read patterns** → Data type inference
  - Single reads → UINT16
  - Double reads → UINT32/INT32
- **Function codes** → Access type (read-only, write-able)

### Data Type Inference
- **UINT16**: Single register reads
- **INT16**: Signed single values
- **UINT32/INT32**: Multi-register values
- **FLOAT32**: Decimal values (power, energy)
- **STRING**: Sequential text values

## Typical Sungrow Register Layout

| Address Range | Group | Count | Examples |
|---|---|---|---|
| 0-50 | Inverter Info | ~30 | Model, Serial, Firmware version |
| 100-199 | Grid/AC Data | ~50 | Phase voltages, currents, frequency, power |
| 200-299 | DC/PV Input | ~50 | PV1/2 voltage/current/power |
| 300-399 | Weather Station | ~20 | Temperature, humidity, irradiance, wind |
| 500-599 | Energy Counters | ~50 | Daily/total energy, import/export |
| 1000+ | Faults/Alarms | ~100 | Fault codes, alarm codes |

## Requirements

### Windows System (Already Have)
- ✅ Windows 11
- ✅ Python 3.x
- ✅ Wireshark/tshark
- ✅ Network access to 192.168.1.5

### Python Packages (Optional)
For advanced PCAPNG parsing (if built-in parser isn't sufficient):
```bash
pip install pyshark scapy
```

## Usage Examples

### Example 1: Full Capture & Analysis Workflow
```batch
REM Start capture (5 minutes)
capture_modbus.bat

REM Let PCVue query the logger...
REM Stop capture when done

REM Process the capture
python modbus_pipeline.py captures\modbus_20251210_1430.pcapng my_sungrow
```

### Example 2: Analyze Existing Capture
```bash
python pcap_extractor.py old_capture.pcapng extracted.json
python modbus_pipeline.py old_capture.pcapng analysis_output
```

### Example 3: Interactive Menu
```batch
workflow.bat
REM Then select options 1-3
```

## Output Files

### extracted_frames.json
Raw Modbus frames with transaction details:
```json
{
  "source_file": "modbus_20251210_1430.pcapng",
  "total_frames": 245,
  "frames": [
    {
      "transaction_id": 1,
      "function_code": 3,
      "function_name": "Read Holding Registers",
      "starting_address": 10,
      "quantity": 2,
      "raw_hex": "000100000006010300000A0002"
    }
  ]
}
```

### register_map.json
Mapping with suggestions and grouping:
```json
{
  "decoder_version": "1.0",
  "device": "Sungrow_Logger",
  "device_ip": "192.168.1.5",
  "total_frames_captured": 245,
  "groups": {
    "Inverter_Info": [
      {
        "address": 0,
        "name": "inverter_info_model",
        "type": "uint16",
        "count": 1,
        "unit": "",
        "description": "Device model code"
      }
    ],
    "Grid_AC_Data": [...]
  }
}
```

### analysis_report.txt
Human-readable summary:
```
=====================================
SUNGROW MODBUS ANALYSIS REPORT
=====================================

Total Frames: 245
Valid Modbus Frames: 245

TRAFFIC BREAKDOWN:
  Read Operations: 200
  Write Operations: 45

FUNCTION CODE BREAKDOWN:
  Read Holding Registers: 180
  Read Input Registers: 20
  Write Single Register: 45

ADDRESS RANGES:
  Min Address: 0
  Max Address: 1050
  Unique Addresses: 87

EXPECTED REGISTER GROUPS:
  Inverter Info (0-50): 15 addresses
  Grid/AC Data (100-199): 25 addresses
  DC/PV Input (200-299): 18 addresses
  Weather Station (300-399): 8 addresses
  Energy Counters (500-599): 15 addresses
  Faults/Alarms (1000-1100): 6 addresses
```

## Troubleshooting

### No Frames Captured
1. Check if network interface name is correct (use `ipconfig`)
2. Verify 192.168.1.5 is reachable (`ping 192.168.1.5`)
3. Ensure PCVue is actively communicating with logger
4. Check Windows Firewall isn't blocking capture

### Invalid/Incomplete Frames
- Frames may be fragmented at TCP layer
- Use the pipeline tool to filter valid frames
- Check Wireshark dissector is enabled for Modbus

### No Modbus Detected
- Verify Sungrow logger is on port 502
- Check network cable connections
- Ensure PCVue is configured for 192.168.1.5:502
- Capture wider filter: `tcp port 502` (all hosts)

## Advanced Customization

### Modify Register Hints
Edit `_load_sungrow_hints()` in `modbus_decoder.py` to add/update known register groups.

### Add Custom Heuristics
Extend the decoder class in `modbus_decoder.py`:
```python
def custom_analysis(self):
    # Your custom logic here
    pass
```

### Change Capture Duration
Edit `capture_modbus.bat`:
```batch
REM Change from 300 seconds (5 min) to desired value
-b duration:600  # 10 minutes
```

## References

- **Modbus TCP Spec**: https://modbus.org/docs/Modbus_Messaging_on_TCP_IP_V1_0b3.pdf
- **Sungrow Documentation**: Check your installer package
- **Wireshark Modbus Dissector**: Built-in support
- **PCAP Format**: https://www.tcpdump.org/papers/sniffing-faq.html

## Next Steps

1. **Run Initial Capture**: Execute `capture_modbus.bat` while PCVue is active
2. **Analyze Results**: Use `modbus_pipeline.py` to process captures
3. **Validate Mapping**: Cross-reference with Sungrow technical docs
4. **Build Integration**: Use mapping JSON in your application
5. **Monitor Production**: Deploy decoder to continuous monitoring

## Support

For issues:
1. Check capture with Wireshark GUI to verify data
2. Review generated JSON files for patterns
3. Ensure 192.168.1.5 is responding to Modbus queries
4. Verify network connectivity and permissions

---

**Toolkit Version**: 1.0  
**Last Updated**: December 2025  
**Target Device**: Sungrow Logger 192.168.1.5
