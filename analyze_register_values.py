#!/usr/bin/env python3
"""
Deep analysis of PCAP to extract actual register values from Modbus responses.
Focus on weather station and wind speed device data.
"""

import struct
from pathlib import Path

def find_modbus_responses(filename):
    """Extract Modbus response data with actual register values"""
    
    print(f"\n{'='*80}")
    print(f"MODBUS RESPONSE VALUE EXTRACTION FROM PCAP")
    print(f"{'='*80}\n")
    
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Find all 0x03 and 0x04 function codes (reads)
    # Response pattern: slave_id, function_code, byte_count, [register_data...]
    
    responses = {}
    
    for i in range(len(data) - 10):
        # Look for function code 3 or 4 (read function)
        if data[i] in [0x03, 0x04]:
            try:
                slave_id = data[i-1] if i > 0 else 0x00
                func_code = data[i]
                
                # Read starting address and count
                start_addr = struct.unpack('>H', data[i+1:i+3])[0]
                reg_count = struct.unpack('>H', data[i+3:i+5])[0]
                
                # Sanity checks
                if not (0 <= slave_id <= 127 and 1 <= reg_count <= 125):
                    continue
                
                # Look ahead for response (function code | 0x80 for error, or same code for response)
                # Response has: slave_id, function, byte_count, data...
                
                key = f"Slave 0x{slave_id:02x} - Regs 0x{start_addr:04x}(count:{reg_count})"
                
                if key not in responses:
                    # Try to find response data
                    if i + 10 < len(data):
                        # Response typically follows after a few bytes
                        for j in range(i+6, min(i+50, len(data))):
                            if data[j] == slave_id and data[j+1] in [func_code, func_code | 0x80]:
                                # Found potential response
                                if data[j+1] == func_code and j+2 < len(data):
                                    byte_count = data[j+2]
                                    if j+3+byte_count <= len(data):
                                        register_data = data[j+3:j+3+byte_count]
                                        responses[key] = {
                                            'slave_id': slave_id,
                                            'function': func_code,
                                            'start_addr': f'0x{start_addr:04x}',
                                            'count': reg_count,
                                            'byte_count': byte_count,
                                            'raw_data': register_data.hex(),
                                            'values': extract_values(register_data, reg_count)
                                        }
                                        break
            except:
                pass
    
    return responses

def extract_values(data, reg_count):
    """Extract floating point or integer values from register data"""
    values = []
    
    # Try as Float32 (2 registers per float)
    if len(data) >= reg_count * 2:
        try:
            for i in range(0, min(len(data)-3, reg_count*2), 2):
                # Big-endian float32
                val = struct.unpack('>f', data[i:i+4])[0]
                if -1000 < val < 10000:  # Reasonable sensor range
                    values.append({
                        'format': 'Float32',
                        'value': round(val, 2),
                        'hex': data[i:i+4].hex()
                    })
        except:
            pass
    
    # Try as Int16
    try:
        for i in range(0, min(len(data)-1, reg_count*2), 2):
            val = struct.unpack('>H', data[i:i+2])[0]
            values.append({
                'format': 'UInt16',
                'value': val,
                'hex': data[i:i+2].hex()
            })
    except:
        pass
    
    return values

def main():
    pcap_file = Path('captures/modbus_test_2min.pcapng')
    
    if not pcap_file.exists():
        print(f"Error: {pcap_file} not found")
        return
    
    responses = find_modbus_responses(str(pcap_file))
    
    print(f"Found {len(responses)} unique register queries\n")
    
    # Focus on weather station devices (small register counts at 0x0000)
    weather_devices = {}
    for key, data in responses.items():
        if data['start_addr'] == '0x0000' and 5 <= data['count'] <= 10:
            print(f"WEATHER STATION CANDIDATE: {key}")
            print(f"  Slave ID: 0x{data['slave_id']:02x}")
            print(f"  Start Address: {data['start_addr']}")
            print(f"  Register Count: {data['count']}")
            print(f"  Byte Count: {data['byte_count']}")
            print(f"  Raw Hex: {data['raw_data']}")
            if data['values']:
                print(f"  Extracted Values:")
                for v in data['values'][:6]:  # Show first 6 values
                    print(f"    - {v['format']}: {v['value']} (hex: {v['hex']})")
            print()
            weather_devices[key] = data

if __name__ == '__main__':
    main()
