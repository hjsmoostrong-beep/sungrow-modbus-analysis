#!/usr/bin/env python3
"""
Simple Modbus Frame Analyzer using tshark output
Analyzes captured PCAPNG files and generates register mapping
"""

import subprocess
import json
import re
from collections import defaultdict
from pathlib import Path


class ModbusFrameAnalyzer:
    """Extract and analyze Modbus frames from PCAPNG using tshark"""

    def __init__(self):
        self.frames = []
        self.unit_data = defaultdict(lambda: {'reads_3': [], 'reads_4': [], 'responses': []})
        self.address_map = defaultdict(list)
        self.unit_ids = set()

    def extract_from_pcapng(self, pcapng_file):
        """Extract Modbus frames using tshark"""
        try:
            tshark_path = r"C:\Program Files\Wireshark\tshark.exe"
            
            # Get all Modbus frames with detailed output
            cmd = [
                tshark_path,
                '-r', pcapng_file,
                '-Y', 'modbus',
                '-T', 'fields',
                '-e', 'ip.src',
                '-e', 'ip.dst',
                '-e', 'tcp.srcport',
                '-e', 'tcp.dstport',
                '-e', 'modbus.hdr.transaction_id',
                '-e', 'modbus.hdr.unit_id',
                '-e', 'modbus.func_code',
                '-e', 'modbus.read.quantity',
                '-e', 'modbus.read.addr',
                '-e', 'frame.number',
                '-e', 'frame.time_relative',
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"tshark error: {result.stderr}")
                return []
            
            lines = result.stdout.strip().split('\n')
            frames = []
            
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                    
                parts = line.split('\t')
                if len(parts) < 10:
                    continue
                
                try:
                    frame = {
                        'src_ip': parts[0],
                        'dst_ip': parts[1],
                        'src_port': parts[2],
                        'dst_port': parts[3],
                        'transaction_id': parts[4] if parts[4] else None,
                        'unit_id': int(parts[5]) if parts[5] else None,
                        'function_code': int(parts[6]) if parts[6] else None,
                        'quantity': int(parts[7]) if parts[7] else None,
                        'start_addr': int(parts[8]) if parts[8] else None,
                        'frame_number': int(parts[9]) if parts[9] else None,
                        'time': float(parts[10]) if parts[10] else 0,
                    }
                    
                    if frame['unit_id'] is not None:
                        self.unit_ids.add(frame['unit_id'])
                        frames.append(frame)
                except (ValueError, IndexError):
                    continue
            
            self.frames = frames
            return frames
            
        except subprocess.TimeoutExpired:
            print("tshark command timed out")
            return []
        except Exception as e:
            print(f"Error extracting frames: {e}")
            return []

    def analyze_frames(self):
        """Analyze frame patterns to identify register access"""
        analysis = {
            'total_frames': len(self.frames),
            'unit_ids': sorted(list(self.unit_ids)),
            'function_codes': {},
            'address_ranges': defaultdict(list),
            'common_queries': defaultdict(int),
        }
        
        for frame in self.frames:
            fc = frame['function_code']
            unit = frame['unit_id']
            
            if fc not in analysis['function_codes']:
                analysis['function_codes'][fc] = {'count': 0, 'by_unit': {}}
            
            analysis['function_codes'][fc]['count'] += 1
            if unit not in analysis['function_codes'][fc]['by_unit']:
                analysis['function_codes'][fc]['by_unit'][unit] = 0
            analysis['function_codes'][fc]['by_unit'][unit] += 1
            
            # Track address ranges by function code
            if frame['start_addr'] is not None and frame['quantity'] is not None:
                key = f"FC{fc}_Unit{unit}_{frame['start_addr']}"
                analysis['address_ranges'][key].append({
                    'address': frame['start_addr'],
                    'quantity': frame['quantity'],
                    'time': frame['time'],
                    'frame_num': frame['frame_number']
                })
                
                # Track common query patterns
                pattern = f"FC{fc}_Addr{frame['start_addr']}_Qty{frame['quantity']}"
                analysis['common_queries'][pattern] += 1
        
        return analysis

    def generate_register_mapping(self, output_file="sungrow_live_mapping.json"):
        """Generate detailed register mapping"""
        analysis = self.analyze_frames()
        
        mapping = {
            'capture_summary': {
                'total_frames': analysis['total_frames'],
                'unit_ids_found': analysis['unit_ids'],
                'function_codes': analysis['function_codes'],
            },
            'registers_by_unit': {},
            'register_groups': {
                'inverter_info': {'range': '0-50', 'category': 'Device info, serial, model'},
                'grid_ac_data': {'range': '100-199', 'category': 'Grid voltage, current, frequency, power'},
                'dc_pv_input': {'range': '200-299', 'category': 'PV voltage, current, power'},
                'weather_station': {'range': '300-399', 'category': 'Temperature, irradiance'},
                'energy_counters': {'range': '500-599', 'category': 'Daily/monthly/yearly energy'},
                'faults_alarms': {'range': '1000+', 'category': 'Fault codes and alarms'},
            },
            'address_patterns': {},
        }
        
        # Build per-unit register maps
        for frame in self.frames:
            unit = frame['unit_id']
            fc = frame['function_code']
            addr = frame['start_addr']
            qty = frame['quantity']
            
            if unit not in mapping['registers_by_unit']:
                mapping['registers_by_unit'][unit] = {
                    'function_3_reads': {},  # Holding registers
                    'function_4_reads': {},  # Input registers
                }
            
            if addr is not None:
                addr_key = f"{addr}+{qty}"
                
                if fc == 3:
                    mapping['registers_by_unit'][unit]['function_3_reads'][addr_key] = {
                        'start_address': addr,
                        'quantity': qty,
                        'inferred_type': self._infer_type(qty),
                        'access_count': 1 + mapping['registers_by_unit'][unit]['function_3_reads'].get(addr_key, {}).get('access_count', 0),
                        'category': self._infer_category(addr),
                    }
                elif fc == 4:
                    mapping['registers_by_unit'][unit]['function_4_reads'][addr_key] = {
                        'start_address': addr,
                        'quantity': qty,
                        'inferred_type': self._infer_type(qty),
                        'access_count': 1 + mapping['registers_by_unit'][unit]['function_4_reads'].get(addr_key, {}).get('access_count', 0),
                        'category': self._infer_category(addr),
                    }
        
        # Add address patterns
        for pattern, count in sorted(analysis['common_queries'].items(), key=lambda x: -x[1])[:50]:
            mapping['address_patterns'][pattern] = {'frequency': count}
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        return mapping

    def _infer_type(self, quantity):
        """Infer data type based on register quantity"""
        if quantity == 1:
            return 'UINT16'
        elif quantity == 2:
            return 'UINT32 or FLOAT32'
        elif quantity >= 3:
            return 'STRING or ARRAY'
        return 'UNKNOWN'

    def _infer_category(self, address):
        """Infer register category from address"""
        if 0 <= address <= 50:
            return 'Inverter_Info'
        elif 100 <= address <= 199:
            return 'Grid_AC_Data'
        elif 200 <= address <= 299:
            return 'DC_PV_Input'
        elif 300 <= address <= 399:
            return 'Weather_Station'
        elif 500 <= address <= 599:
            return 'Energy_Counters'
        elif address >= 1000:
            return 'Faults_Alarms'
        else:
            return 'Other'

    def print_summary(self, output_file="sungrow_live_report.txt"):
        """Print human-readable summary"""
        analysis = self.analyze_frames()
        
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MODBUS FRAME ANALYSIS SUMMARY\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total Frames Captured: {analysis['total_frames']}\n")
            f.write(f"Unit IDs Found: {analysis['unit_ids']}\n\n")
            
            f.write("Function Code Distribution:\n")
            f.write("-" * 70 + "\n")
            for fc, data in sorted(analysis['function_codes'].items()):
                f.write(f"  FC {fc}: {data['count']} frames\n")
                for unit, count in sorted(data['by_unit'].items()):
                    f.write(f"    Unit {unit}: {count} frames\n")
            f.write("\n")
            
            f.write("Most Common Query Patterns (top 20):\n")
            f.write("-" * 70 + "\n")
            for pattern, count in sorted(analysis['common_queries'].items(), key=lambda x: -x[1])[:20]:
                f.write(f"  {pattern}: {count} times\n")
            f.write("\n")
            
            f.write("Address Ranges Accessed:\n")
            f.write("-" * 70 + "\n")
            addr_ranges = {}
            for frame in self.frames:
                if frame['start_addr'] is not None:
                    addr = frame['start_addr']
                    unit = frame['unit_id']
                    key = f"Unit {unit}"
                    if key not in addr_ranges:
                        addr_ranges[key] = set()
                    addr_ranges[key].add(addr)
            
            for unit_key in sorted(addr_ranges.keys()):
                addrs = sorted(addr_ranges[unit_key])
                f.write(f"  {unit_key}: {min(addrs)}-{max(addrs)} (accessed: {len(addrs)} addresses)\n")
            f.write("\n")

        print(f"Report written to {output_file}")


def main():
    import sys
    
    pcapng_file = "captures/modbus_test_2min.pcapng"
    if not Path(pcapng_file).exists():
        print(f"Error: {pcapng_file} not found")
        return
    
    print("="*70)
    print("SIMPLE MODBUS FRAME ANALYZER")
    print("="*70)
    print(f"\nAnalyzing: {pcapng_file}")
    
    analyzer = ModbusFrameAnalyzer()
    print("\nExtracting frames with tshark...")
    frames = analyzer.extract_from_pcapng(pcapng_file)
    
    if not frames:
        print("No frames extracted!")
        return
    
    print(f"✓ Extracted {len(frames)} Modbus frames")
    print(f"✓ Found {len(analyzer.unit_ids)} unique Unit IDs: {sorted(analyzer.unit_ids)}")
    
    print("\nAnalyzing patterns...")
    analysis = analyzer.analyze_frames()
    
    print("\nGenerating mapping file...")
    mapping = analyzer.generate_register_mapping("sungrow_live_mapping.json")
    print("✓ Generated sungrow_live_mapping.json")
    
    print("\nGenerating report...")
    analyzer.print_summary("sungrow_live_report.txt")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nOutput Files:")
    print("  - sungrow_live_mapping.json   (Detailed register mapping)")
    print("  - sungrow_live_report.txt     (Human-readable summary)")


if __name__ == "__main__":
    main()
