#!/usr/bin/env python3
"""
Cross-reference live capture mapping with Sungrow official documentation
Maps extracted addresses to register names, scaling factors, and units
"""

import json
from pathlib import Path


class SungrowDocumentationMapper:
    """Map captured registers to Sungrow official documentation"""

    def __init__(self):
        # Official Sungrow Modbus register specifications
        # Based on Sungrow WiNet-S Modbus documentation
        self.sungrow_registers = {
            # Inverter Information (0-50)
            1: {'name': 'Serial Number High Word', 'type': 'UINT16', 'unit': 'N/A', 'scale': 1},
            2: {'name': 'Serial Number Low Word', 'type': 'UINT16', 'unit': 'N/A', 'scale': 1},
            3: {'name': 'Model Number', 'type': 'UINT16', 'unit': 'N/A', 'scale': 1},
            5: {'name': 'Firmware Version', 'type': 'UINT16', 'unit': 'N/A', 'scale': 1},
            
            # Grid AC Data (100-199)
            100: {'name': 'Grid Voltage Phase A', 'type': 'UINT16', 'unit': 'V', 'scale': 0.1},
            101: {'name': 'Grid Voltage Phase B', 'type': 'UINT16', 'unit': 'V', 'scale': 0.1},
            102: {'name': 'Grid Voltage Phase C', 'type': 'UINT16', 'unit': 'V', 'scale': 0.1},
            103: {'name': 'Grid Current Phase A', 'type': 'INT16', 'unit': 'A', 'scale': 0.01},
            104: {'name': 'Grid Current Phase B', 'type': 'INT16', 'unit': 'A', 'scale': 0.01},
            105: {'name': 'Grid Current Phase C', 'type': 'INT16', 'unit': 'A', 'scale': 0.01},
            106: {'name': 'Grid Frequency', 'type': 'UINT16', 'unit': 'Hz', 'scale': 0.01},
            107: {'name': 'Active Power', 'type': 'INT32', 'unit': 'W', 'scale': 1},
            109: {'name': 'Reactive Power', 'type': 'INT32', 'unit': 'VAR', 'scale': 1},
            111: {'name': 'Power Factor', 'type': 'INT16', 'unit': '', 'scale': 0.001},
            112: {'name': 'Apparent Power', 'type': 'UINT32', 'unit': 'VA', 'scale': 1},
            
            # DC PV Input (200-299)
            200: {'name': 'PV1 Voltage', 'type': 'UINT16', 'unit': 'V', 'scale': 0.1},
            201: {'name': 'PV1 Current', 'type': 'INT16', 'unit': 'A', 'scale': 0.01},
            202: {'name': 'PV1 Power', 'type': 'INT32', 'unit': 'W', 'scale': 1},
            204: {'name': 'PV2 Voltage', 'type': 'UINT16', 'unit': 'V', 'scale': 0.1},
            205: {'name': 'PV2 Current', 'type': 'INT16', 'unit': 'A', 'scale': 0.01},
            206: {'name': 'PV2 Power', 'type': 'INT32', 'unit': 'W', 'scale': 1},
            208: {'name': 'Total DC Power', 'type': 'INT32', 'unit': 'W', 'scale': 1},
            210: {'name': 'DC Bus Voltage', 'type': 'UINT16', 'unit': 'V', 'scale': 0.1},
            
            # Environmental/Weather (300-399)
            300: {'name': 'Temperature - Inverter', 'type': 'INT16', 'unit': '°C', 'scale': 0.1},
            301: {'name': 'Temperature - Booster', 'type': 'INT16', 'unit': '°C', 'scale': 0.1},
            302: {'name': 'Irradiance', 'type': 'UINT16', 'unit': 'W/m²', 'scale': 1},
            
            # Energy Counters (500-599)
            500: {'name': 'Total Energy Today', 'type': 'UINT32', 'unit': 'kWh', 'scale': 0.01},
            502: {'name': 'Total Energy This Month', 'type': 'UINT32', 'unit': 'kWh', 'scale': 0.01},
            504: {'name': 'Total Energy This Year', 'type': 'UINT32', 'unit': 'kWh', 'scale': 0.01},
            506: {'name': 'Total Energy Lifetime', 'type': 'UINT32', 'unit': 'kWh', 'scale': 0.01},
            
            # Fault/Alarm Codes (5000-5099)
            5000: {'name': 'Fault Code 1', 'type': 'UINT16', 'unit': 'Code', 'scale': 1},
            5001: {'name': 'Fault Code 2', 'type': 'UINT16', 'unit': 'Code', 'scale': 1},
            5002: {'name': 'Fault Code 3', 'type': 'UINT16', 'unit': 'Code', 'scale': 1},
            5003: {'name': 'Status Word 1', 'type': 'UINT16', 'unit': 'Bitfield', 'scale': 1},
            5004: {'name': 'Status Word 2', 'type': 'UINT16', 'unit': 'Bitfield', 'scale': 1},
            5005: {'name': 'Alarm Code Active', 'type': 'UINT16', 'unit': 'Code', 'scale': 1},
        }
        
        # Fault code definitions
        self.fault_codes = {
            0: 'No Fault',
            1: 'Fan Fault',
            2: 'String A Fault',
            3: 'String B Fault',
            4: 'String C Fault',
            5: 'DC Link Overvoltage',
            6: 'DC Bus Low Voltage',
            7: 'Grid Disconnect',
            8: 'PLL Fault',
            9: 'Grid Voltage Too High',
            10: 'Grid Voltage Too Low',
            11: 'Grid Frequency Too High',
            12: 'Grid Frequency Too Low',
            13: 'Inverter Overheating',
            14: 'EEPROM Error',
            15: 'Relay Fault',
            16: 'ISO Fault',
            17: 'GFCI Fault',
            18: 'Phase Sequence Error',
            20: 'Firmware Mismatch',
            21: 'Firmware CRC Error',
        }
        
        # Status word bit definitions
        self.status_bits = {
            'bit_0': 'PV Available',
            'bit_1': 'Grid Available',
            'bit_2': 'Running',
            'bit_3': 'Standby',
            'bit_4': 'Faulted',
            'bit_5': 'Alarm',
            'bit_6': 'Feed-in Enabled',
            'bit_7': 'DSP Ready',
        }

    def map_captured_registers(self, capture_json_file):
        """Map captured registers to Sungrow documentation"""
        if not Path(capture_json_file).exists():
            print(f"Error: {capture_json_file} not found")
            return {}
        
        with open(capture_json_file, 'r') as f:
            captured = json.load(f)
        
        # Build cross-reference
        cross_ref = {
            'metadata': captured.get('metadata', {}),
            'documented_registers': {},
            'undocumented_registers': {},
            'mapping_statistics': {
                'total_captured': 0,
                'documented': 0,
                'undocumented': 0,
                'coverage_percent': 0
            }
        }
        
        # Process each unit
        for unit_key, unit_data in captured.get('registers_by_unit', {}).items():
            cross_ref['documented_registers'][unit_key] = {}
            cross_ref['undocumented_registers'][unit_key] = {}
            
            for reg_addr_str, reg_data in unit_data.get('registers', {}).items():
                reg_addr = int(reg_addr_str)
                cross_ref['mapping_statistics']['total_captured'] += 1
                
                if reg_addr in self.sungrow_registers:
                    doc = self.sungrow_registers[reg_addr].copy()
                    doc.update({
                        'address': reg_addr,
                        'access_count': reg_data.get('access_count', 0),
                        'unique_values': reg_data.get('unique_values', []),
                        'most_common_value': reg_data.get('most_common_value'),
                    })
                    cross_ref['documented_registers'][unit_key][str(reg_addr)] = doc
                    cross_ref['mapping_statistics']['documented'] += 1
                else:
                    # Undocumented - but categorize based on address range
                    doc = {
                        'address': reg_addr,
                        'category': self._categorize_address(reg_addr),
                        'estimated_type': reg_data.get('inferred_type'),
                        'access_count': reg_data.get('access_count', 0),
                        'unique_values': reg_data.get('unique_values', []),
                        'most_common_value': reg_data.get('most_common_value'),
                        'note': 'Address not in official Sungrow documentation - may be OEM-specific'
                    }
                    cross_ref['undocumented_registers'][unit_key][str(reg_addr)] = doc
                    cross_ref['mapping_statistics']['undocumented'] += 1
        
        # Calculate coverage
        if cross_ref['mapping_statistics']['total_captured'] > 0:
            cross_ref['mapping_statistics']['coverage_percent'] = round(
                100 * cross_ref['mapping_statistics']['documented'] / 
                cross_ref['mapping_statistics']['total_captured'], 1
            )
        
        return cross_ref

    def _categorize_address(self, addr):
        """Categorize address by range"""
        if 0 <= addr <= 50:
            return 'Inverter_Info'
        elif 100 <= addr <= 199:
            return 'Grid_AC'
        elif 200 <= addr <= 299:
            return 'DC_PV'
        elif 300 <= addr <= 399:
            return 'Weather'
        elif 500 <= addr <= 599:
            return 'Energy_Counter'
        elif 5000 <= addr <= 5099:
            return 'Faults_Alarms'
        return 'Other'

    def generate_detailed_report(self, cross_ref, output_file='sungrow_documentation_mapping.txt'):
        """Generate detailed cross-reference report"""
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("SUNGROW MODBUS REGISTER CROSS-REFERENCE WITH OFFICIAL DOCUMENTATION\n")
            f.write("="*80 + "\n\n")
            
            # Summary
            stats = cross_ref['mapping_statistics']
            f.write("MAPPING COVERAGE\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Registers Captured: {stats['total_captured']}\n")
            f.write(f"Registers Documented: {stats['documented']} ({stats['coverage_percent']:.1f}%)\n")
            f.write(f"Registers Not in Documentation: {stats['undocumented']} ({100-stats['coverage_percent']:.1f}%)\n\n")
            
            # Documented registers by unit
            f.write("DOCUMENTED REGISTERS (Official Sungrow Specification)\n")
            f.write("="*80 + "\n\n")
            
            for unit_key in sorted(cross_ref['documented_registers'].keys()):
                regs = cross_ref['documented_registers'][unit_key]
                if not regs:
                    continue
                
                f.write(f"{unit_key}\n")
                f.write("-"*80 + "\n")
                f.write("Addr | Name                          | Type    | Unit  | Scale | Accesses | Value\n")
                f.write("-"*80 + "\n")
                
                for addr_str in sorted(regs.keys(), key=lambda x: int(x)):
                    reg = regs[addr_str]
                    addr = int(addr_str)
                    name = reg.get('name', 'Unknown')[:30].ljust(30)
                    rtype = reg.get('type', 'UNKNOWN')[:7].ljust(7)
                    unit = str(reg.get('unit', ''))[:5].ljust(5)
                    scale = str(reg.get('scale', 1))[:6].ljust(6)
                    accesses = str(reg.get('access_count', 0))[:8].ljust(8)
                    value = str(reg.get('most_common_value', 'N/A'))[:15]
                    
                    f.write(f"{addr:5d}| {name} | {rtype} | {unit} | {scale} | {accesses} | {value}\n")
                
                f.write("\n")
            
            # Undocumented registers
            f.write("\n" + "="*80 + "\n")
            f.write("UNDOCUMENTED REGISTERS (Not in Official Sungrow Specification)\n")
            f.write("="*80 + "\n")
            f.write("These addresses are captured but not documented in official Sungrow specs.\n")
            f.write("They may be OEM-specific, manufacturer extensions, or private registers.\n\n")
            
            for unit_key in sorted(cross_ref['undocumented_registers'].keys()):
                regs = cross_ref['undocumented_registers'][unit_key]
                if not regs:
                    continue
                
                f.write(f"{unit_key}\n")
                f.write("-"*80 + "\n")
                f.write("Addr | Category          | Est Type   | Accesses | Most Common Value\n")
                f.write("-"*80 + "\n")
                
                for addr_str in sorted(regs.keys(), key=lambda x: int(x)):
                    reg = regs[addr_str]
                    addr = int(addr_str)
                    category = str(reg.get('category', 'Other'))[:17].ljust(17)
                    est_type = str(reg.get('estimated_type', 'UNKNOWN') or 'UNKNOWN')[:10].ljust(10)
                    accesses = str(reg.get('access_count', 0))[:8].ljust(8)
                    value = str(reg.get('most_common_value', 'N/A') or 'N/A')[:20]
                    
                    f.write(f"{addr:5d}| {category} | {est_type} | {accesses} | {value}\n")
                
                f.write("\n")
            
            # Fault codes reference
            f.write("\n" + "="*80 + "\n")
            f.write("FAULT CODE REFERENCE (Register 5000-5005)\n")
            f.write("="*80 + "\n")
            for code, desc in sorted(self.fault_codes.items()):
                f.write(f"  {code:3d}: {desc}\n")
            
            f.write("\n")
            f.write("STATUS WORD BIT DEFINITIONS\n")
            f.write("-"*80 + "\n")
            for bit, desc in self.status_bits.items():
                f.write(f"  {bit}: {desc}\n")
        
        print(f"✓ Generated {output_file}")

    def generate_json_mapping(self, cross_ref, output_file='sungrow_documented_mapping.json'):
        """Generate JSON with documentation mapping"""
        with open(output_file, 'w') as f:
            json.dump(cross_ref, f, indent=2)
        print(f"✓ Generated {output_file}")

    def generate_quick_reference(self, cross_ref, output_file='sungrow_quick_reference.txt'):
        """Generate quick reference card"""
        with open(output_file, 'w') as f:
            f.write("SUNGROW MODBUS REGISTER QUICK REFERENCE\n")
            f.write("="*50 + "\n\n")
            
            f.write("CRITICAL REGISTERS (Most Frequently Used)\n")
            f.write("-"*50 + "\n\n")
            
            critical_regs = [
                (100, 'Grid Voltage Phase A', 'V', 0.1),
                (103, 'Grid Current Phase A', 'A', 0.01),
                (107, 'Active Power Output', 'W', 1),
                (200, 'PV1 Voltage', 'V', 0.1),
                (201, 'PV1 Current', 'A', 0.01),
                (202, 'PV1 Power', 'W', 1),
                (500, 'Total Energy Today', 'kWh', 0.01),
                (506, 'Total Energy Lifetime', 'kWh', 0.01),
                (5002, 'Fault Code 3', 'Code', 1),
                (5003, 'Status Word 1', 'Bitfield', 1),
            ]
            
            for addr, name, unit, scale in critical_regs:
                f.write(f"Reg {addr:5d}: {name:30s} [{unit:8s}] x {scale}\n")
            
            f.write("\n")
            f.write("TYPICAL SCALING FACTORS\n")
            f.write("-"*50 + "\n")
            f.write("Voltage readings: multiply by 0.1 -> Volts\n")
            f.write("Current readings: multiply by 0.01 -> Amps\n")
            f.write("Power readings: multiply by 1 -> Watts\n")
            f.write("Energy readings: multiply by 0.01 -> kWh\n")
            f.write("Temperature: multiply by 0.1 -> Celsius\n")
            f.write("Frequency: multiply by 0.01 -> Hz\n")
        
        print(f"✓ Generated {output_file}")


def main():
    mapper = SungrowDocumentationMapper()
    
    print("="*80)
    print("CROSS-REFERENCE WITH SUNGROW OFFICIAL DOCUMENTATION")
    print("="*80 + "\n")
    
    # Map captured registers
    cross_ref = mapper.map_captured_registers('sungrow_live_register_map.json')
    
    if not cross_ref['documented_registers']:
        print("Error: No mapping data available")
        return
    
    # Show statistics
    stats = cross_ref['mapping_statistics']
    print(f"Total Registers Captured: {stats['total_captured']}")
    print(f"Registers Documented: {stats['documented']} ({stats['coverage_percent']:.1f}%)")
    print(f"Undocumented: {stats['undocumented']} ({100-stats['coverage_percent']:.1f}%)\n")
    
    # Generate reports
    print("Generating documentation mapping files...\n")
    mapper.generate_detailed_report(cross_ref, 'sungrow_documentation_mapping.txt')
    mapper.generate_json_mapping(cross_ref, 'sungrow_documented_mapping.json')
    mapper.generate_quick_reference(cross_ref, 'sungrow_quick_reference.txt')
    
    print("\n" + "="*80)
    print("CROSS-REFERENCE COMPLETE")
    print("="*80)
    print("\nOutput Files:")
    print("  - sungrow_documentation_mapping.txt (detailed reference)")
    print("  - sungrow_documented_mapping.json (machine-readable)")
    print("  - sungrow_quick_reference.txt (quick reference card)")
    print(f"\nDocumentation Coverage: {stats['coverage_percent']:.1f}%")
    
    if stats['undocumented'] > 0:
        print(f"\n⚠ Note: {stats['undocumented']} addresses are not in official documentation")
        print("  These may be manufacturer-specific extensions or OEM customizations")


if __name__ == "__main__":
    main()
