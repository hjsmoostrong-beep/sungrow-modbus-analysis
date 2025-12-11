#!/usr/bin/env python3
"""
Analyze PCAP file to extract Modbus traffic and identify physical hardware devices.
Focus on actual Modbus transactions, not simulated data.
"""

import struct
import json
from pathlib import Path
from collections import defaultdict

def read_pcapng(filename):
    """Parse PCAPNG file format"""
    devices = defaultdict(lambda: {'registers': defaultdict(list), 'packets': []})
    
    try:
        with open(filename, 'rb') as f:
            data = f.read()
        
        # PCAPNG format
        offset = 0
        while offset < len(data):
            if offset + 8 > len(data):
                break
                
            # Block Type
            block_type = struct.unpack('<I', data[offset:offset+4])[0]
            block_len = struct.unpack('<I', data[offset+4:offset+8])[0]
            
            if block_type == 0x0A0D0D0A:  # Section Header Block
                offset += block_len
                continue
            elif block_type == 0x00000001:  # Interface Description Block
                offset += block_len
                continue
            elif block_type == 0x00000006:  # Enhanced Packet Block
                # Parse packet data
                if offset + block_len > len(data):
                    break
                    
                # Extract packet info
                packet_data = data[offset+28:offset+block_len-4]
                
                # Look for Modbus TCP (port 502)
                if b'\x01f' in packet_data or b'f\x01' in packet_data:
                    # Found potential Modbus data
                    try:
                        parse_modbus_packet(packet_data, devices)
                    except:
                        pass
                
                offset += block_len
            else:
                offset += block_len if block_len > 0 else 1
        
        return devices
    except Exception as e:
        print(f"Error reading PCAP: {e}")
        return devices

def parse_modbus_packet(packet_data, devices):
    """Extract Modbus transactions from raw packet data"""
    # Look for Modbus function codes
    for i in range(len(packet_data) - 8):
        # Check for Modbus function code 3 (Read Holding Registers) or 4 (Read Input Registers)
        if packet_data[i] in [0x03, 0x04]:
            try:
                slave_id = packet_data[i-1] if i > 0 else 0
                func_code = packet_data[i]
                
                if i + 6 < len(packet_data):
                    start_addr = struct.unpack('>H', packet_data[i+1:i+3])[0]
                    reg_count = struct.unpack('>H', packet_data[i+3:i+5])[0]
                    
                    # Skip responses (they have different format)
                    if func_code in [0x03, 0x04]:
                        devices[f'0x{slave_id:02x}']['packets'].append({
                            'slave_id': slave_id,
                            'function': func_code,
                            'start_address': f'0x{start_addr:04x}',
                            'register_count': reg_count,
                            'raw_bytes': packet_data[max(0,i-2):min(len(packet_data),i+10)].hex()
                        })
            except:
                pass

def extract_modbus_transactions(filename):
    """Extract Modbus transactions from PCAP file"""
    print(f"\n{'='*70}")
    print(f"Analyzing PCAP File: {filename}")
    print(f"{'='*70}\n")
    
    devices = read_pcapng(filename)
    
    if not devices:
        print("No Modbus transactions found in PCAP file")
        print("\nTrying alternative parsing method...")
        
        # Alternative: Simple binary search for Modbus patterns
        with open(filename, 'rb') as f:
            data = f.read()
        
        print(f"File size: {len(data)} bytes")
        
        # Search for Modbus function codes
        modbus_devices = defaultdict(set)
        
        for i in range(len(data) - 8):
            # Look for patterns: function code + starting address
            if data[i] in [0x03, 0x04]:  # Modbus read functions
                try:
                    # Potential Modbus request
                    slave_id = data[i-1] if i > 0 else 0x00
                    func = data[i]
                    start_addr = struct.unpack('>H', data[i+1:i+3])[0]
                    count = struct.unpack('>H', data[i+3:i+5])[0]
                    
                    # Sanity checks
                    if 0 <= slave_id <= 127 and 1 <= count <= 125:
                        modbus_devices[f'0x{slave_id:02x}'].add(
                            (f'0x{start_addr:04x}', count, func)
                        )
                except:
                    pass
        
        print(f"\nFound {len(modbus_devices)} potential Modbus devices\n")
        
        for slave_id in sorted(modbus_devices.keys()):
            print(f"Slave ID: {slave_id}")
            for addr, count, func in sorted(modbus_devices[slave_id]):
                func_name = "Read Holding Registers" if func == 0x03 else "Read Input Registers"
                print(f"  - Function {func} ({func_name})")
                print(f"    Starting Register: {addr}")
                print(f"    Register Count: {count}")
            print()
        
        return modbus_devices
    
    return devices

if __name__ == '__main__':
    pcap_file = Path('captures/modbus_test_2min.pcapng')
    
    if not pcap_file.exists():
        print(f"PCAP file not found: {pcap_file}")
        exit(1)
    
    devices = extract_modbus_transactions(str(pcap_file))
