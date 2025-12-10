#!/usr/bin/env python3
"""
Enhanced Modbus Frame Extractor from PCAPNG
Extracts frames, analyzes addresses, and builds detailed register mapping
"""

import struct
import json
from collections import defaultdict
from pathlib import Path


class PCAPNGFrameExtractor:
    """Extract Modbus frames from PCAPNG with detailed analysis"""

    def __init__(self):
        self.frames = []
        self.unit_data = defaultdict(lambda: {'reads_3': [], 'reads_4': [], 'responses': []})
        self.register_map = {}

    def extract_from_pcapng(self, pcapng_file):
        """Extract all Modbus frames from PCAPNG file"""
        try:
            with open(pcapng_file, 'rb') as f:
                return self._parse_pcapng(f)
        except Exception as e:
            print(f"Error reading PCAPNG: {e}")
            return []

    def _parse_pcapng(self, f):
        """Parse PCAPNG file format"""
        frames = []
        f.seek(0)
        magic = f.read(4)
        
        if magic == b'\x0a\x0d\x0d\x0a':  # PCAPNG magic
            f.seek(0)
            while True:
                block_type_bytes = f.read(4)
                if len(block_type_bytes) < 4:
                    break
                    
                block_type = struct.unpack('>I', block_type_bytes)[0]
                block_len_bytes = f.read(4)
                if len(block_len_bytes) < 4:
                    break
                    
                block_len = struct.unpack('>I', block_len_bytes)[0]
                
                if block_type == 0x06:  # Enhanced Packet Block
                    packet_data = f.read(block_len - 12)
                    frame = self._extract_modbus_from_epb(packet_data)
                    if frame:
                        frames.append(frame)
                else:
                    f.read(block_len - 8)
                
                # Read trailing length
                f.read(4)
        
        return frames

    def _extract_modbus_from_epb(self, data):
        """Extract Modbus frame from Enhanced Packet Block"""
        try:
            if len(data) < 24:
                return None
            
            # Skip interface ID and timestamps
            incl_len = struct.unpack('>I', data[12:16])[0]
            packet_data = data[20:20+incl_len]
            
            # Skip Ethernet (14 bytes)
            if len(packet_data) < 34:
                return None
            
            eth_type = struct.unpack('>H', packet_data[12:14])[0]
            if eth_type != 0x0800:  # IPv4
                return None
            
            # Parse IPv4
            ip_version = (packet_data[14] >> 4) & 0x0F
            if ip_version != 4:
                return None
            
            ihl = (packet_data[14] & 0x0F) * 4
            tcp_start = 14 + ihl
            
            if tcp_start + 20 > len(packet_data):
                return None
            
            # Skip TCP header
            tcp_header_len = ((packet_data[tcp_start + 12] >> 4) & 0x0F) * 4
            modbus_start = tcp_start + tcp_header_len
            
            if modbus_start >= len(packet_data):
                return None
            
            modbus_data = packet_data[modbus_start:]
            
            # Parse Modbus TCP
            if len(modbus_data) < 12:
                return None
            
            transaction_id = struct.unpack('>H', modbus_data[0:2])[0]
            protocol_id = struct.unpack('>H', modbus_data[2:4])[0]
            
            if protocol_id != 0:  # Not Modbus
                return None
            
            frame = {
                'transaction_id': transaction_id,
                'length': struct.unpack('>H', modbus_data[4:6])[0],
                'unit_id': modbus_data[6],
                'function_code': modbus_data[7],
                'raw_hex': modbus_data.hex().upper(),
            }
            
            # Parse function-specific data
            if frame['function_code'] in [3, 4]:  # Read operations
                if len(modbus_data) >= 12:
                    frame['starting_address'] = struct.unpack('>H', modbus_data[8:10])[0]
                    frame['quantity'] = struct.unpack('>H', modbus_data[10:12])[0]
            
            return frame
        except:
            return None

    def analyze_frames(self, frames):
        """Analyze extracted frames and build patterns"""
        address_patterns = defaultdict(lambda: {'count': 0, 'quantities': [], 'units': set(), 'funcs': set()})
        
        for frame in frames:
            if 'starting_address' in frame:
                addr = frame['starting_address']
                qty = frame['quantity']
                unit = frame['unit_id']
                func = frame['function_code']
                
                address_patterns[addr]['count'] += 1
                address_patterns[addr]['quantities'].append(qty)
                address_patterns[addr]['units'].add(unit)
                address_patterns[addr]['funcs'].add(func)
                
                # Track by unit
                if func == 3:
                    self.unit_data[unit]['reads_3'].append({'addr': addr, 'qty': qty})
                elif func == 4:
                    self.unit_data[unit]['reads_4'].append({'addr': addr, 'qty': qty})
        
        return address_patterns

    def infer_data_types(self, address_patterns):
        """Infer data types from read patterns"""
        type_map = {}
        
        for addr, data in address_patterns.items():
            avg_qty = sum(data['quantities']) / len(data['quantities']) if data['quantities'] else 1
            
            if avg_qty >= 4:
                data_type = "FLOAT32 or multiple values"
                count = 4
            elif avg_qty >= 2:
                data_type = "UINT32/INT32"
                count = 2
            else:
                data_type = "UINT16/INT16"
                count = 1
            
            type_map[addr] = {
                'type': data_type,
                'count': count,
                'avg_quantity': avg_qty,
                'frequency': data['count']
            }
        
        return type_map

    def generate_register_mapping(self, output_file):
        """Generate detailed register mapping"""
        mapping = {
            'source': 'Live capture from Sungrow Logger 192.168.1.5',
            'capture_duration': '120 seconds',
            'units': {}
        }
        
        for unit_id, unit_data in self.unit_data.items():
            unit_name = self._get_unit_name(unit_id)
            
            # Analyze Function 3 (Holding Registers)
            func3_addresses = set()
            func3_ranges = []
            for read in unit_data['reads_3']:
                func3_addresses.add(read['addr'])
                func3_ranges.append({'start': read['addr'], 'qty': read['qty']})
            
            # Analyze Function 4 (Input Registers)
            func4_addresses = set()
            func4_ranges = []
            for read in unit_data['reads_4']:
                func4_addresses.add(read['addr'])
                func4_ranges.append({'start': read['addr'], 'qty': read['qty']})
            
            mapping['units'][unit_id] = {
                'name': unit_name,
                'function_3': {
                    'description': 'Holding Registers (Settings/Control)',
                    'addresses_accessed': sorted(list(func3_addresses)),
                    'address_count': len(func3_addresses),
                    'ranges': func3_ranges[:5]  # Show first 5
                },
                'function_4': {
                    'description': 'Input Registers (Measurements)',
                    'addresses_accessed': sorted(list(func4_addresses)),
                    'address_count': len(func4_addresses),
                    'ranges': func4_ranges[:5]  # Show first 5
                }
            }
        
        with open(output_file, 'w') as f:
            json.dump(mapping, f, indent=2, default=str)
        
        return mapping

    def _get_unit_name(self, unit_id):
        """Get friendly name for unit ID"""
        names = {
            1: "Inverter 1",
            2: "Inverter 2",
            3: "Inverter 3",
            4: "Inverter 4",
            5: "Weather Station",
            247: "System Controller"
        }
        return names.get(unit_id, f"Unit {unit_id}")

    def print_summary(self, frames, address_patterns, type_map):
        """Print comprehensive analysis summary"""
        print("\n" + "="*70)
        print("ENHANCED MODBUS FRAME ANALYSIS")
        print("="*70)
        
        print(f"\nTotal Frames Extracted: {len(frames)}")
        print(f"Unique Starting Addresses: {len(address_patterns)}")
        
        print("\nAddress Analysis (Top 10 by frequency):")
        print("-" * 70)
        print(f"{'Address':>8} {'Func':>5} {'Count':>6} {'Avg Qty':>8} {'Type':>20} {'Units':>10}")
        print("-" * 70)
        
        sorted_addrs = sorted(address_patterns.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
        
        for addr, data in sorted_addrs:
            type_info = type_map.get(addr, {})
            data_type = type_info.get('type', 'Unknown')
            units = ','.join(str(u) for u in sorted(data['units']))
            funcs = ','.join(str(f) for f in sorted(data['funcs']))
            avg_qty = sum(data['quantities']) / len(data['quantities']) if data['quantities'] else 0
            
            print(f"{addr:8d} {funcs:>5} {data['count']:6d} {avg_qty:8.1f} {data_type:>20} {units:>10}")
        
        print("\n" + "="*70)
        print("UNIT-SPECIFIC ANALYSIS")
        print("="*70)
        
        for unit_id in sorted(self.unit_data.keys()):
            unit = self.unit_data[unit_id]
            unit_name = self._get_unit_name(unit_id)
            
            print(f"\n{unit_name} (Unit {unit_id}):")
            print(f"  Function 3 (Holding Registers):")
            
            if unit['reads_3']:
                addrs_3 = set(r['addr'] for r in unit['reads_3'])
                print(f"    Addresses: {sorted(addrs_3)[:10]} {'...' if len(addrs_3) > 10 else ''}")
                print(f"    Total accesses: {len(unit['reads_3'])}")
            else:
                print(f"    Not accessed")
            
            print(f"  Function 4 (Input Registers):")
            
            if unit['reads_4']:
                addrs_4 = set(r['addr'] for r in unit['reads_4'])
                print(f"    Addresses: {sorted(addrs_4)[:10]} {'...' if len(addrs_4) > 10 else ''}")
                print(f"    Total accesses: {len(unit['reads_4'])}")
            else:
                print(f"    Not accessed")


def main():
    pcapng_file = "captures/modbus_test_2min.pcapng"
    
    if not Path(pcapng_file).exists():
        print(f"Error: {pcapng_file} not found")
        return
    
    print("Extracting Modbus frames from PCAPNG...")
    extractor = PCAPNGFrameExtractor()
    frames = extractor.extract_from_pcapng(pcapng_file)
    
    print(f"Extracted {len(frames)} Modbus frames")
    
    if not frames:
        print("No frames extracted. Check PCAPNG file format.")
        return
    
    print("\nAnalyzing frame patterns...")
    address_patterns = extractor.analyze_frames(frames)
    
    print("Inferring data types...")
    type_map = extractor.infer_data_types(address_patterns)
    
    print("\nGenerating detailed register mapping...")
    mapping = extractor.generate_register_mapping("enhanced_register_map.json")
    
    print("Generating analysis report...")
    extractor.print_summary(frames, address_patterns, type_map)
    
    print("\n" + "="*70)
    print("OUTPUT FILES")
    print("="*70)
    print("enhanced_register_map.json  - Detailed register mapping by unit")
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
