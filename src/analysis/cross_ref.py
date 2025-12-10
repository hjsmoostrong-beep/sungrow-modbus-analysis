#!/usr/bin/env python3
"""
Cross-reference captured Modbus addresses with Sungrow official documentation.
Maps response data to specific registers and validates against known patterns.
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

class SungrowCrossReference:
    """Cross-reference Modbus addresses with official Sungrow documentation."""
    
    # Official Sungrow Modbus register documentation (from SG5k-20k range)
    OFFICIAL_REGISTERS = {
        # Input Registers (FC4) - Read-only
        0x0000: {'name': 'Status Code', 'type': 'uint16', 'unit': '', 'access': 'R', 'scale': 1},
        0x0001: {'name': 'Fault Code', 'type': 'uint16', 'unit': '', 'access': 'R', 'scale': 1},
        0x0002: {'name': 'PV1 Voltage', 'type': 'uint16', 'unit': 'V', 'access': 'R', 'scale': 0.1},
        0x0003: {'name': 'PV1 Current', 'type': 'uint16', 'unit': 'A', 'access': 'R', 'scale': 0.01},
        0x0004: {'name': 'PV1 Power', 'type': 'uint32', 'unit': 'W', 'access': 'R', 'scale': 1},
        0x0006: {'name': 'PV2 Voltage', 'type': 'uint16', 'unit': 'V', 'access': 'R', 'scale': 0.1},
        0x0007: {'name': 'PV2 Current', 'type': 'uint16', 'unit': 'A', 'access': 'R', 'scale': 0.01},
        0x0008: {'name': 'PV2 Power', 'type': 'uint32', 'unit': 'W', 'access': 'R', 'scale': 1},
        0x000A: {'name': 'Grid Voltage', 'type': 'uint16', 'unit': 'V', 'access': 'R', 'scale': 0.1},
        0x000B: {'name': 'Grid Current', 'type': 'int16', 'unit': 'A', 'access': 'R', 'scale': 0.01},
        0x000C: {'name': 'Total Power', 'type': 'int32', 'unit': 'W', 'access': 'R', 'scale': 1},
        0x000E: {'name': 'Frequency', 'type': 'uint16', 'unit': 'Hz', 'access': 'R', 'scale': 0.01},
        0x000F: {'name': 'Efficiency', 'type': 'uint16', 'unit': '%', 'access': 'R', 'scale': 0.1},
        0x0010: {'name': 'Temperature', 'type': 'int16', 'unit': '°C', 'access': 'R', 'scale': 0.1},
        0x0011: {'name': 'Today Energy', 'type': 'uint32', 'unit': 'kWh', 'access': 'R', 'scale': 0.01},
        0x0013: {'name': 'Total Energy', 'type': 'uint32', 'unit': 'kWh', 'access': 'R', 'scale': 0.01},
        0x0015: {'name': 'Total Runtime', 'type': 'uint32', 'unit': 'hours', 'access': 'R', 'scale': 1},
        
        # Holding Registers (FC3) - Read/Write
        0x1000: {'name': 'Device Type', 'type': 'uint16', 'unit': '', 'access': 'RW', 'scale': 1},
        0x1001: {'name': 'Device ID', 'type': 'uint16', 'unit': '', 'access': 'R', 'scale': 1},
        0x1002: {'name': 'Firmware Version', 'type': 'uint16', 'unit': '', 'access': 'R', 'scale': 0.01},
        0x1003: {'name': 'System Time', 'type': 'uint32', 'unit': 'Unix', 'access': 'RW', 'scale': 1},
    }
    
    # Data type sizes (in registers)
    DATA_TYPES = {
        'uint16': 1,
        'int16': 1,
        'uint32': 2,
        'int32': 2,
        'float': 2,
        'string': None  # Variable
    }
    
    # Sungrow fault codes
    FAULT_CODES = {
        1: 'Hardware failure',
        2: 'Grid disconnection',
        3: 'Over-voltage protection',
        4: 'Under-voltage protection',
        5: 'Over-frequency protection',
        6: 'Under-frequency protection',
        7: 'Over-temperature protection',
        8: 'Communication error',
        9: 'Firmware error',
        10: 'DCI fault',
    }
    
    # Status codes
    STATUS_CODES = {
        0x0000: 'Standby',
        0x0001: 'Startup',
        0x0002: 'Running',
        0x0003: 'Shutdown',
        0x0004: 'Fault',
        0x0005: 'Maintenance',
    }
    
    def __init__(self):
        self.captured_addresses = {}
        self.cross_reference = {}
        self.pattern_matches = defaultdict(list)
        
    def load_captured_addresses(self, json_file):
        """Load captured addresses from analysis output."""
        if not Path(json_file).exists():
            print(f"File not found: {json_file}")
            return False
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                self.captured_addresses = data.get('addresses', {})
            print(f"Loaded {len(self.captured_addresses)} captured addresses")
            return True
        except json.JSONDecodeError as e:
            print(f"Error loading JSON: {e}")
            return False
    
    def cross_reference_addresses(self):
        """Map captured addresses to official documentation."""
        documented = 0
        undocumented = 0
        
        for addr_hex, captured_data in sorted(self.captured_addresses.items()):
            try:
                addr_int = int(addr_hex, 16) if isinstance(addr_hex, str) else addr_hex
            except ValueError:
                continue
            
            if addr_int in self.OFFICIAL_REGISTERS:
                doc = self.OFFICIAL_REGISTERS[addr_int]
                self.cross_reference[addr_int] = {
                    'address': addr_int,
                    'hex': f'0x{addr_int:04X}',
                    'name': doc['name'],
                    'documented': True,
                    'type': doc['type'],
                    'unit': doc['unit'],
                    'access': doc['access'],
                    'scale': doc['scale'],
                    'captured': captured_data,
                    'register_size': self.DATA_TYPES.get(doc['type'], 1)
                }
                documented += 1
            else:
                self.cross_reference[addr_int] = {
                    'address': addr_int,
                    'hex': f'0x{addr_int:04X}',
                    'name': 'Undocumented (OEM Extension)',
                    'documented': False,
                    'type': 'unknown',
                    'unit': '',
                    'access': 'R',
                    'scale': 1,
                    'captured': captured_data,
                    'register_size': 1
                }
                undocumented += 1
        
        print(f"Documented: {documented}, Undocumented: {undocumented}")
        return documented, undocumented
    
    def detect_data_patterns(self):
        """Identify data types from response patterns."""
        pattern_analysis = {}
        
        for addr, ref in self.cross_reference.items():
            captured = ref['captured']
            access_count = captured.get('access_count', 0)
            quantities = captured.get('quantities_read', [])
            
            # Infer data type from access patterns
            if quantities and quantities[0] == 1:
                inferred_type = 'uint16'
            elif quantities and quantities[0] == 2:
                inferred_type = 'uint32'
            else:
                inferred_type = 'unknown'
            
            # Determine if read-only or read-write
            is_read = captured.get('is_read', True)
            is_write = captured.get('is_write', False)
            access_mode = 'RW' if (is_read and is_write) else ('W' if is_write else 'R')
            
            pattern_analysis[addr] = {
                'address': f'0x{addr:04X}',
                'access_count': access_count,
                'inferred_type': inferred_type,
                'access_mode': access_mode,
                'quantities': quantities,
                'devices': captured.get('devices', []),
                'function_codes': captured.get('function_codes', [])
            }
            
            # Validate against documented type if known
            if ref['documented']:
                documented_type = ref['type']
                if inferred_type != 'unknown' and inferred_type != documented_type:
                    pattern_analysis[addr]['type_mismatch'] = True
        
        self.pattern_matches = pattern_analysis
        return pattern_analysis
    
    def validate_response_data(self, address, raw_data, expected_type=None):
        """Validate response data matches expected patterns."""
        validation = {
            'address': f'0x{address:04X}',
            'valid': True,
            'issues': []
        }
        
        if address not in self.cross_reference:
            validation['issues'].append('Address not in cross-reference')
            validation['valid'] = False
            return validation
        
        ref = self.cross_reference[address]
        data_type = expected_type or ref['type']
        
        # Validate data length
        if data_type == 'uint16':
            if len(raw_data) != 2:
                validation['issues'].append(f'Expected 2 bytes for uint16, got {len(raw_data)}')
                validation['valid'] = False
        elif data_type == 'uint32':
            if len(raw_data) != 4:
                validation['issues'].append(f'Expected 4 bytes for uint32, got {len(raw_data)}')
                validation['valid'] = False
        
        # Validate value range
        try:
            if data_type == 'uint16':
                value = struct.unpack('>H', raw_data[:2])[0]
                scaled = value * ref['scale']
            elif data_type == 'uint32':
                value = struct.unpack('>I', raw_data[:4])[0]
                scaled = value * ref['scale']
            elif data_type == 'int16':
                value = struct.unpack('>h', raw_data[:2])[0]
                scaled = value * ref['scale']
            elif data_type == 'int32':
                value = struct.unpack('>i', raw_data[:4])[0]
                scaled = value * ref['scale']
            
            validation['raw_value'] = value
            validation['scaled_value'] = scaled
            validation['unit'] = ref['unit']
            
        except struct.error as e:
            validation['issues'].append(f'Struct unpack error: {e}')
            validation['valid'] = False
        
        return validation
    
    def generate_cross_reference_report(self, output_file='cross_reference_report.txt'):
        """Generate detailed cross-reference report."""
        report = []
        report.append("=" * 100)
        report.append("MODBUS ADDRESS CROSS-REFERENCE REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 100)
        
        # Summary
        documented = sum(1 for r in self.cross_reference.values() if r['documented'])
        undocumented = len(self.cross_reference) - documented
        
        report.append("\nSUMMARY")
        report.append("-" * 100)
        report.append(f"Total Addresses: {len(self.cross_reference)}")
        report.append(f"Officially Documented: {documented} ({documented*100/len(self.cross_reference):.1f}%)")
        report.append(f"Undocumented (OEM Extensions): {undocumented} ({undocumented*100/len(self.cross_reference):.1f}%)")
        
        # Documented registers
        report.append("\n" + "=" * 100)
        report.append("DOCUMENTED REGISTERS (From Official Sungrow Specification)")
        report.append("=" * 100)
        
        documented_list = [r for r in self.cross_reference.values() if r['documented']]
        documented_list.sort(key=lambda x: x['address'])
        
        for reg in documented_list:
            report.append(f"\n{reg['hex']} - {reg['name']}")
            report.append(f"  Type: {reg['type']}, Unit: {reg['unit']}, Scale: {reg['scale']}")
            report.append(f"  Access: {reg['access']}, Register Size: {reg['register_size']}")
            captured = reg['captured']
            report.append(f"  Captured: {captured['access_count']} accesses, Quantities: {captured['quantities_read']}")
            if captured['devices']:
                report.append(f"  Accessed by units: {captured['devices']}")
        
        # Undocumented addresses
        report.append("\n" + "=" * 100)
        report.append("UNDOCUMENTED ADDRESSES (OEM EXTENSIONS)")
        report.append("=" * 100)
        
        undocumented_list = [r for r in self.cross_reference.values() if not r['documented']]
        undocumented_list.sort(key=lambda x: x['address'])
        
        for reg in undocumented_list[:20]:  # Show top 20
            report.append(f"\n{reg['hex']}")
            captured = reg['captured']
            report.append(f"  Accesses: {captured['access_count']}, Quantities: {captured['quantities_read']}")
            report.append(f"  Units: {captured['devices']}")
        
        if len(undocumented_list) > 20:
            report.append(f"\n... and {len(undocumented_list) - 20} more undocumented addresses")
        
        # Data type validation
        report.append("\n" + "=" * 100)
        report.append("DATA TYPE VALIDATION")
        report.append("=" * 100)
        
        for addr, pattern in sorted(self.pattern_matches.items()):
            report.append(f"\n{pattern['address']}")
            report.append(f"  Access Count: {pattern['access_count']}")
            report.append(f"  Inferred Type: {pattern['inferred_type']}")
            report.append(f"  Access Mode: {pattern['access_mode']}")
            report.append(f"  Quantities: {pattern['quantities']}")
            if 'type_mismatch' in pattern and pattern['type_mismatch']:
                report.append(f"  WARNING: Type mismatch detected!")
        
        report_text = '\n'.join(report)
        with open(output_file, 'w') as f:
            f.write(report_text)
        
        print(f"Report saved to: {output_file}")
        return report_text
    
    def generate_json_output(self, output_file='cross_reference.json'):
        """Generate machine-readable JSON output."""
        output = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_addresses': len(self.cross_reference),
                'documented_count': sum(1 for r in self.cross_reference.values() if r['documented']),
                'undocumented_count': sum(1 for r in self.cross_reference.values() if not r['documented']),
            },
            'documented': {},
            'undocumented': {}
        }
        
        for addr, ref in sorted(self.cross_reference.items()):
            entry = {
                'address': f'0x{addr:04X}',
                'name': ref['name'],
                'type': ref['type'],
                'unit': ref['unit'],
                'access': ref['access'],
                'scale': ref['scale'],
                'captured_access_count': ref['captured']['access_count'],
                'captured_quantities': ref['captured']['quantities_read'],
                'captured_devices': ref['captured']['devices'],
            }
            
            if ref['documented']:
                output['documented'][f'0x{addr:04X}'] = entry
            else:
                output['undocumented'][f'0x{addr:04X}'] = entry
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"JSON output saved to: {output_file}")
        return output

import struct

def main():
    """Run cross-reference analysis."""
    xref = SungrowCrossReference()
    
    # Try to load captured addresses
    analysis_file = 'address_analysis.json'
    if not Path(analysis_file).exists():
        print(f"Note: Run analyze_starting_addresses.py first to generate {analysis_file}")
        print("For demonstration, using built-in test data...\n")
        
        # Use built-in test data
        xref.captured_addresses = {
            '0x0000': {'access_count': 156, 'quantities_read': [10], 'devices': [1, 2, 3]},
            '0x000A': {'access_count': 149, 'quantities_read': [8], 'devices': [1, 2, 3]},
            '0x0010': {'access_count': 95, 'quantities_read': [6], 'devices': [1, 2, 3]},
            '0x1000': {'access_count': 50, 'quantities_read': [1], 'devices': [247]},
            '0x1002': {'access_count': 45, 'quantities_read': [1], 'devices': [247]},
            '0x2000': {'access_count': 200, 'quantities_read': [4], 'devices': [1, 2, 3, 4, 5]},
        }
    else:
        xref.load_captured_addresses(analysis_file)
    
    print("\n" + "="*80)
    print("CROSS-REFERENCING WITH OFFICIAL DOCUMENTATION...")
    print("="*80)
    
    documented, undocumented = xref.cross_reference_addresses()
    
    print("\n" + "="*80)
    print("DETECTING DATA PATTERNS...")
    print("="*80)
    
    xref.detect_data_patterns()
    
    print("\n" + "="*80)
    print("GENERATING REPORTS...")
    print("="*80)
    
    report = xref.generate_cross_reference_report('cross_reference_report.txt')
    xref.generate_json_output('cross_reference.json')
    
    print("\n" + report[:500] + "\n...")

if __name__ == '__main__':
    main()
