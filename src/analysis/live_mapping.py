#!/usr/bin/env python3
"""
Extract Modbus register mapping from live PCAPNG capture
Uses tshark to parse PCAPNG and extract frame details
"""

import subprocess
import json
from collections import defaultdict
from pathlib import Path


class LiveMappingExtractor:
    """Extract detailed register mapping from live capture"""

    def __init__(self):
        self.frames = []
        self.units = set()
        self.registers = defaultdict(lambda: defaultdict(lambda: {
            'addresses': set(),
            'quantities': set(),
            'function_codes': set(),
            'access_count': 0
        }))

    def extract_frames(self, pcapng_file):
        """Extract all Modbus frames from PCAPNG"""
        try:
            tshark = r"C:\Program Files\Wireshark\tshark.exe"
            
            # Get detailed info about each Modbus frame
            cmd = [
                tshark,
                '-r', pcapng_file,
                '-Y', 'modbus',
                '-T', 'fields',
                '-e', 'frame.number',
                '-e', 'ip.src',
                '-e', 'ip.dst',
                '-e', 'tcp.srcport',
                '-e', 'tcp.dstport',
                '-e', 'modbus.func_code',
                '-e', 'modbus.read.addr',
                '-e', 'modbus.read.quantity',
                '-E', 'separator=|'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                # Try basic extraction
                return self._extract_basic(pcapng_file)
            
            lines = result.stdout.strip().split('\n')
            frame_count = 0
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split('|')
                if len(parts) < 6:
                    continue
                
                try:
                    frame = {
                        'number': int(parts[0]) if parts[0] else None,
                        'src_ip': parts[1],
                        'dst_ip': parts[2],
                        'src_port': int(parts[3]) if parts[3] else None,
                        'dst_port': int(parts[4]) if parts[4] else None,
                        'func_code': int(parts[5]) if parts[5] else None,
                        'read_addr': int(parts[6]) if len(parts) > 6 and parts[6] else None,
                        'read_qty': int(parts[7]) if len(parts) > 7 and parts[7] else None,
                    }
                    
                    if frame['func_code'] in [3, 4]:
                        self.frames.append(frame)
                        frame_count += 1
                        
                        # Determine unit ID from address pattern or IP
                        # For now, extract from captured traffic
                        unit_id = self._infer_unit_id(frame)
                        self.units.add(unit_id)
                        
                        # Track register access
                        if frame['read_addr'] is not None:
                            reg_info = self.registers[unit_id][frame['read_addr']]
                            reg_info['addresses'].add(frame['read_addr'])
                            reg_info['quantities'].add(frame['read_qty'] if frame['read_qty'] else 1)
                            reg_info['function_codes'].add(frame['func_code'])
                            reg_info['access_count'] += 1
                
                except (ValueError, IndexError):
                    continue
            
            print(f"✓ Extracted {frame_count} Modbus frames")
            return self.frames
        
        except subprocess.TimeoutExpired:
            print("tshark timeout - trying alternative method")
            return self._extract_basic(pcapng_file)
        except Exception as e:
            print(f"Error: {e}")
            return []

    def _infer_unit_id(self, frame):
        """Infer Unit ID from IP pattern"""
        # In Modbus, unit ID is typically embedded in traffic or we can use device IP last octet
        # For Sungrow: 192.168.1.5 is the main logger
        # Multiple devices may be accessed via different unit IDs
        # Use a simple heuristic: Unit 1-5 for now
        ip = frame['dst_ip']
        if '192.168.1.5' in ip:
            # This is the logger - check if we can infer unit from ports/addresses
            return 1
        return 1  # Default

    def _extract_basic(self, pcapng_file):
        """Fallback: extract just basic frame info"""
        print("Attempting basic extraction...")
        tshark = r"C:\Program Files\Wireshark\tshark.exe"
        
        cmd = [tshark, '-r', pcapng_file, '-Y', 'modbus', '-T', 'fields', 
               '-e', 'modbus.func_code', '-E', 'separator=|']
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            print(f"✓ Found {len(lines)} Modbus frames")
            self.units.add(1)
            return lines
        
        return []

    def generate_mapping(self, output_file="sungrow_live_register_map.json"):
        """Generate detailed register mapping"""
        mapping = {
            'metadata': {
                'total_frames': len(self.frames),
                'units_found': sorted(list(self.units)),
                'unique_addresses': sum(len(regs) for regs in self.registers.values()),
            },
            'registers_by_unit': {},
            'register_categories': {
                'inverter_info': (0, 50),
                'grid_ac_data': (100, 199),
                'dc_pv_input': (200, 299),
                'weather_station': (300, 399),
                'energy_counters': (500, 599),
                'faults_alarms': (1000, 9999),
            },
            'address_usage': {}
        }
        
        # Build per-unit mappings
        for unit in sorted(self.units):
            unit_regs = {}
            
            for addr in sorted(self.registers[unit].keys()):
                reg_info = self.registers[unit][addr]
                
                qty_list = sorted(list(reg_info['quantities']))
                most_common_qty = max(set(qty_list), key=qty_list.count) if qty_list else 1
                
                unit_regs[str(addr)] = {
                    'address': addr,
                    'quantities_read': qty_list,
                    'most_common_quantity': most_common_qty,
                    'function_codes': sorted(list(reg_info['function_codes'])),
                    'access_count': reg_info['access_count'],
                    'category': self._get_category(addr),
                    'inferred_type': self._infer_type(most_common_qty),
                }
            
            mapping['registers_by_unit'][f'Unit_{unit}'] = unit_regs
        
        # Build address usage summary
        all_addresses = set()
        for unit_regs in self.registers.values():
            for addr in unit_regs.keys():
                all_addresses.add(addr)
        
        for addr in sorted(all_addresses):
            access_count = sum(
                self.registers[unit][addr]['access_count'] 
                for unit in self.units 
                if addr in self.registers[unit]
            )
            mapping['address_usage'][str(addr)] = {
                'address': addr,
                'total_accesses': access_count,
                'category': self._get_category(addr)
            }
        
        # Write JSON
        with open(output_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"✓ Generated {output_file}")
        return mapping

    def generate_report(self, output_file="sungrow_live_analysis_report.txt"):
        """Generate human-readable report"""
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MODBUS REGISTER MAPPING ANALYSIS\n")
            f.write("From: sungrow_test_2min.pcapng\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"CAPTURE SUMMARY\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Frames: {len(self.frames)}\n")
            f.write(f"Units Found: {sorted(list(self.units))}\n")
            f.write(f"Total Unique Addresses: {sum(len(regs) for regs in self.registers.values())}\n\n")
            
            f.write("REGISTER MAPPING BY UNIT\n")
            f.write("-"*70 + "\n\n")
            
            for unit in sorted(self.units):
                f.write(f"UNIT {unit}\n")
                f.write("-"*70 + "\n")
                
                for addr in sorted(self.registers[unit].keys()):
                    reg_info = self.registers[unit][addr]
                    category = self._get_category(addr)
                    qty = sorted(list(reg_info['quantities']))
                    
                    f.write(f"  Address {addr:4d} ({category:20s})\n")
                    f.write(f"    Quantities:  {qty}\n")
                    f.write(f"    Functions:   {sorted(list(reg_info['function_codes']))}\n")
                    f.write(f"    Access Count: {reg_info['access_count']}\n")
                    f.write(f"    Type:        {self._infer_type(max(qty))}\n\n")
                
                f.write("\n")
            
            f.write("\nREGISTER CATEGORY SUMMARY\n")
            f.write("-"*70 + "\n")
            
            categories = {
                'inverter_info': (0, 50),
                'grid_ac_data': (100, 199),
                'dc_pv_input': (200, 299),
                'weather_station': (300, 399),
                'energy_counters': (500, 599),
                'faults_alarms': (1000, 9999),
            }
            
            for cat_name, (min_addr, max_addr) in categories.items():
                addrs_in_cat = []
                for unit_regs in self.registers.values():
                    for addr in unit_regs.keys():
                        if min_addr <= addr <= max_addr:
                            addrs_in_cat.append(addr)
                
                if addrs_in_cat:
                    f.write(f"\n{cat_name.upper()} ({min_addr}-{max_addr})\n")
                    f.write(f"  Addresses found: {sorted(set(addrs_in_cat))}\n")
        
        print(f"✓ Generated {output_file}")

    def _get_category(self, addr):
        """Get category for address"""
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

    def _infer_type(self, quantity):
        """Infer data type from quantity"""
        if quantity == 1:
            return "UINT16"
        elif quantity == 2:
            return "UINT32/FLOAT32"
        elif quantity == 4:
            return "64-bit/INT64"
        else:
            return f"ARRAY[{quantity}]"


def main():
    pcapng_file = "captures/modbus_test_2min.pcapng"
    
    if not Path(pcapng_file).exists():
        print(f"Error: {pcapng_file} not found")
        return
    
    print("="*70)
    print("MODBUS LIVE CAPTURE ANALYSIS")
    print("="*70 + "\n")
    
    extractor = LiveMappingExtractor()
    
    print(f"Processing: {pcapng_file}\n")
    frames = extractor.extract_frames(pcapng_file)
    
    if not frames:
        print("No Modbus frames found!")
        return
    
    print(f"✓ Units: {sorted(extractor.units)}")
    print(f"✓ Registers tracked: {sum(len(r) for r in extractor.registers.values())}\n")
    
    print("Generating outputs...")
    extractor.generate_mapping("sungrow_live_register_map.json")
    extractor.generate_report("sungrow_live_analysis_report.txt")
    
    print("\n" + "="*70)
    print("COMPLETE - Register mapping extracted from live capture")
    print("="*70)
    print("\nOutput files:")
    print("  - sungrow_live_register_map.json (machine readable)")
    print("  - sungrow_live_analysis_report.txt (human readable)")


if __name__ == "__main__":
    main()
