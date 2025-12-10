#!/usr/bin/env python3
"""
Parse Modbus register data from live PCAPNG capture using JSON output
"""

import subprocess
import json
from collections import defaultdict
from pathlib import Path
import re


class ModbusJSONAnalyzer:
    """Extract and analyze Modbus frames from JSON output"""

    def __init__(self):
        self.frames = []
        self.unit_data = defaultdict(lambda: {
            'registers': defaultdict(lambda: {'values': [], 'count': 0}),
            'function_codes': set()
        })
        self.address_patterns = defaultdict(int)

    def extract_from_json(self, pcapng_file):
        """Extract frames from tshark JSON output"""
        try:
            tshark = r"C:\Program Files\Wireshark\tshark.exe"
            
            # Get JSON output with Modbus data
            cmd = [
                tshark,
                '-r', pcapng_file,
                '-Y', 'modbus',
                '-T', 'jsonraw'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            
            if result.returncode != 0:
                print(f"tshark error: {result.stderr[:200]}")
                return []
            
            # Parse JSON
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                return []
            
            if not isinstance(data, list):
                print("Unexpected JSON format")
                return []
            
            frame_count = 0
            register_count = 0
            
            for packet in data:
                try:
                    if '_source' not in packet:
                        continue
                    
                    layers = packet['_source'].get('layers', {})
                    
                    # Get frame info
                    frame_info = {
                        'number': None,
                        'src_ip': None,
                        'dst_ip': None,
                        'func_code': None,
                        'unit_id': None,
                        'registers': {}
                    }
                    
                    # Extract IP addresses
                    if 'ip' in layers:
                        ip_data = layers['ip']
                        frame_info['src_ip'] = ip_data.get('ip.src_raw', [None])[0]
                        frame_info['dst_ip'] = ip_data.get('ip.dst_raw', [None])[0]
                    
                    # Extract Modbus info
                    if 'mbtcp' in layers:
                        mbtcp = layers['mbtcp']
                        unit_id_raw = mbtcp.get('mbtcp.unit_id_raw', [None])[0]
                        frame_info['unit_id'] = int(unit_id_raw, 16) if unit_id_raw else 1
                    
                    if 'modbus' in layers:
                        modbus = layers['modbus']
                        func_raw = modbus.get('modbus.func_code_raw', [None])[0]
                        frame_info['func_code'] = int(func_raw) if func_raw else None
                        
                        # Extract register data
                        for key, value in modbus.items():
                            match = re.match(r'Register\s+(\d+)\s+\((\w+)\):\s+(.+)', key)
                            if match:
                                reg_num = int(match.group(1))
                                reg_type = match.group(2)
                                reg_val = match.group(3)
                                
                                frame_info['registers'][reg_num] = {
                                    'type': reg_type,
                                    'value': reg_val
                                }
                                register_count += 1
                    
                    if frame_info['unit_id'] is not None and frame_info['func_code'] is not None:
                        self.frames.append(frame_info)
                        frame_count += 1
                        
                        # Track register accesses
                        unit = frame_info['unit_id']
                        self.unit_data[unit]['function_codes'].add(frame_info['func_code'])
                        
                        for reg_num, reg_info in frame_info['registers'].items():
                            self.unit_data[unit]['registers'][reg_num]['values'].append(reg_info['value'])
                            self.unit_data[unit]['registers'][reg_num]['count'] += 1
                
                except Exception as e:
                    pass
            
            print(f"✓ Extracted {frame_count} frames with {register_count} register values")
            return self.frames
            
        except subprocess.TimeoutExpired:
            print("tshark timeout (JSON extraction took too long)")
            return []
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def generate_mapping(self, output_file="sungrow_live_register_map.json"):
        """Generate detailed register mapping"""
        mapping = {
            'metadata': {
                'total_frames': len(self.frames),
                'units': sorted(list(self.unit_data.keys())),
                'total_register_accesses': sum(
                    sum(r['count'] for r in unit['registers'].values())
                    for unit in self.unit_data.values()
                )
            },
            'registers_by_unit': {},
            'register_summary': {}
        }
        
        # Build mapping per unit
        for unit_id in sorted(self.unit_data.keys()):
            unit_info = self.unit_data[unit_id]
            unit_regs = {}
            
            for reg_addr in sorted(unit_info['registers'].keys()):
                reg_data = unit_info['registers'][reg_addr]
                values = reg_data['values']
                
                # Get unique values
                unique_values = list(set(values))
                
                unit_regs[str(reg_addr)] = {
                    'address': reg_addr,
                    'access_count': reg_data['count'],
                    'unique_values': unique_values,
                    'most_common_value': max(set(values), key=values.count) if values else None,
                    'category': self._categorize_address(reg_addr),
                    'data_type': self._infer_type(reg_addr)
                }
            
            mapping['registers_by_unit'][f'Unit_{unit_id}'] = {
                'function_codes': sorted(list(unit_info['function_codes'])),
                'registers': unit_regs,
                'register_count': len(unit_regs)
            }
        
        # Summary of all registers
        all_registers = defaultdict(lambda: {'units': set(), 'accesses': 0, 'values': set()})
        
        for unit_id, unit_info in self.unit_data.items():
            for reg_addr, reg_data in unit_info['registers'].items():
                all_registers[reg_addr]['units'].add(unit_id)
                all_registers[reg_addr]['accesses'] += reg_data['count']
                all_registers[reg_addr]['values'].update(set(reg_data['values']))
        
        for addr in sorted(all_registers.keys()):
            reg = all_registers[addr]
            mapping['register_summary'][str(addr)] = {
                'address': addr,
                'accessed_by_units': sorted(list(reg['units'])),
                'total_accesses': reg['accesses'],
                'unique_values_observed': sorted(list(reg['values'])[:100]),  # Limit to first 100
                'category': self._categorize_address(addr)
            }
        
        with open(output_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"✓ Generated {output_file}")
        return mapping

    def generate_report(self, output_file="sungrow_live_analysis_report.txt"):
        """Generate human-readable report"""
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MODBUS REGISTER MAPPING ANALYSIS\n")
            f.write("From: modbus_test_2min.pcapng (Live 2-minute capture)\n")
            f.write("="*70 + "\n\n")
            
            # Summary
            total_accesses = sum(
                sum(r['count'] for r in unit['registers'].values())
                for unit in self.unit_data.values()
            )
            
            f.write("CAPTURE SUMMARY\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Frames: {len(self.frames)}\n")
            f.write(f"Units Found: {sorted(list(self.unit_data.keys()))}\n")
            f.write(f"Total Register Accesses: {total_accesses}\n")
            f.write(f"Unique Registers Accessed: {sum(len(u['registers']) for u in self.unit_data.values())}\n\n")
            
            # Per-unit details
            f.write("REGISTER MAPPING BY UNIT\n")
            f.write("-"*70 + "\n\n")
            
            for unit_id in sorted(self.unit_data.keys()):
                unit_info = self.unit_data[unit_id]
                f.write(f"UNIT {unit_id}\n")
                f.write(f"  Function Codes: {sorted(list(unit_info['function_codes']))}\n")
                f.write(f"  Registers Accessed: {len(unit_info['registers'])}\n")
                f.write(f"  Register Accesses: {sum(r['count'] for r in unit_info['registers'].values())}\n\n")
                
                f.write("  Address  | Category        | Accesses | Data Type | Most Common Value\n")
                f.write("  " + "-"*65 + "\n")
                
                for reg_addr in sorted(unit_info['registers'].keys()):
                    reg = unit_info['registers'][reg_addr]
                    accesses = reg['count']
                    category = self._categorize_address(reg_addr)
                    dtype = self._infer_type(reg_addr)
                    
                    # Get most common value from list
                    if reg['values']:
                        most_common = max(set(reg['values']), key=reg['values'].count)
                        value = str(most_common)[:20]
                    else:
                        value = "N/A"
                    
                    f.write(f"  {reg_addr:5d}   | {category:15s} | {accesses:8d} | {dtype:9s} | {value}\n")
                
                f.write("\n")
            
            # Category summary
            f.write("\nREGISTER CATEGORY SUMMARY\n")
            f.write("-"*70 + "\n\n")
            
            categories = {
                'Inverter_Info': (0, 50),
                'Grid_AC': (100, 199),
                'DC_PV': (200, 299),
                'Weather': (300, 399),
                'Energy_Counter': (500, 599),
                'Faults_Alarms': (1000, 9999),
            }
            
            for cat_name, (min_addr, max_addr) in categories.items():
                addrs_in_cat = []
                total_cat_accesses = 0
                
                for unit_info in self.unit_data.values():
                    for addr, reg_data in unit_info['registers'].items():
                        if min_addr <= addr <= max_addr:
                            if addr not in addrs_in_cat:
                                addrs_in_cat.append(addr)
                            total_cat_accesses += reg_data['count']
                
                if addrs_in_cat:
                    f.write(f"{cat_name} ({min_addr}-{max_addr})\n")
                    f.write(f"  Addresses: {sorted(addrs_in_cat)}\n")
                    f.write(f"  Total Accesses: {total_cat_accesses}\n\n")
        
        print(f"✓ Generated {output_file}")

    def _categorize_address(self, addr):
        """Categorize register address"""
        if 0 <= addr <= 50:
            return "Inverter_Info"
        elif 100 <= addr <= 199:
            return "Grid_AC"
        elif 200 <= addr <= 299:
            return "DC_PV"
        elif 300 <= addr <= 399:
            return "Weather"
        elif 500 <= addr <= 599:
            return "Energy_Counter"
        elif addr >= 1000:
            return "Faults_Alarms"
        return "Other"

    def _infer_type(self, addr):
        """Infer data type from address"""
        # Heuristics based on Sungrow logger ranges
        if 0 <= addr <= 50:
            return "UINT16"
        elif 100 <= addr <= 199:
            return "UINT32"  # Usually AC data
        elif 200 <= addr <= 299:
            return "UINT32"  # Usually DC data
        elif 300 <= addr <= 399:
            return "INT16"   # Usually sensor data
        elif 500 <= addr <= 599:
            return "UINT32"  # Energy counters
        elif addr >= 1000:
            return "UINT16"  # Fault codes
        return "UNKNOWN"


def main():
    pcapng_file = "captures/modbus_test_2min.pcapng"
    
    if not Path(pcapng_file).exists():
        print(f"Error: {pcapng_file} not found")
        return
    
    print("="*70)
    print("MODBUS LIVE CAPTURE ANALYZER (JSON)")
    print("="*70 + "\n")
    
    analyzer = ModbusJSONAnalyzer()
    
    print(f"Processing: {pcapng_file}")
    print("Extracting frames with tshark JSON output...\n")
    
    frames = analyzer.extract_from_json(pcapng_file)
    
    if not frames:
        print("No frames extracted!")
        return
    
    units = sorted(list(analyzer.unit_data.keys()))
    print(f"✓ Units: {units}")
    print(f"✓ Registers per unit: {[len(analyzer.unit_data[u]['registers']) for u in units]}\n")
    
    print("Generating outputs...")
    analyzer.generate_mapping("sungrow_live_register_map.json")
    analyzer.generate_report("sungrow_live_analysis_report.txt")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nOutput files:")
    print("  - sungrow_live_register_map.json (machine readable)")
    print("  - sungrow_live_analysis_report.txt (human readable)")


if __name__ == "__main__":
    main()
