#!/usr/bin/env python3
"""
Analyze starting addresses and quantities read from live Modbus capture.
Extracts address patterns, access frequency, and read/write characteristics.
"""

import json
import struct
from collections import defaultdict
from pathlib import Path
from datetime import datetime

class AddressAnalyzer:
    """Analyze Modbus starting addresses and read quantities."""
    
    def __init__(self):
        self.address_stats = defaultdict(lambda: {
            'count': 0,
            'quantities': [],
            'read': False,
            'write': False,
            'functions': [],
            'timestamps': [],
            'devices': set(),
            'data_patterns': []
        })
        self.unit_ids = set()
        self.function_codes = defaultdict(int)
        
    def analyze_from_json(self, json_file):
        """Extract and analyze starting addresses from tshark JSON output."""
        if not Path(json_file).exists():
            print(f"File not found: {json_file}")
            return False
            
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading JSON: {e}")
            return False
        
        packets = data.get('_packets', [])
        print(f"Processing {len(packets)} packets...")
        
        for packet_num, packet in enumerate(packets, 1):
            layers = packet.get('_source', {}).get('layers', {})
            modbus_layer = layers.get('modbus', {})
            
            if not modbus_layer:
                continue
            
            # Extract function code
            func_code = modbus_layer.get('modbus.func_code')
            if not func_code:
                continue
            
            func_code = int(func_code)
            self.function_codes[func_code] += 1
            
            # Extract unit ID
            unit_id = modbus_layer.get('modbus.unit_id')
            if unit_id:
                self.unit_ids.add(int(unit_id))
            
            # Extract starting address
            start_addr = modbus_layer.get('modbus.starting_address')
            if not start_addr:
                continue
            
            start_addr = int(start_addr)
            
            # Extract quantity
            quantity = modbus_layer.get('modbus.quantity_of_registers') or \
                      modbus_layer.get('modbus.quantity_of_coils') or \
                      modbus_layer.get('modbus.quantity_of_inputs')
            
            quantity = int(quantity) if quantity else 1
            
            # Categorize request vs response
            tcp_layer = layers.get('tcp', {})
            src_port = tcp_layer.get('tcp.srcport')
            
            is_request = src_port != '502' if src_port else True
            
            # Record statistics
            stats = self.address_stats[start_addr]
            stats['count'] += 1
            if quantity not in stats['quantities']:
                stats['quantities'].append(quantity)
            if is_request:
                stats['read'] = func_code in [3, 4]  # FC3=holding, FC4=input
                stats['write'] = func_code in [5, 6, 15, 16]
            
            if func_code not in stats['functions']:
                stats['functions'].append(func_code)
            
            # Extract frame time
            frame_time = layers.get('frame', {}).get('frame.time')
            if frame_time:
                stats['timestamps'].append(frame_time)
            
            # Extract device (unit) ID
            if unit_id:
                stats['devices'].add(int(unit_id))
        
        return True
    
    def analyze_patterns(self):
        """Identify access patterns and data characteristics."""
        patterns = {
            'sequential_reads': defaultdict(list),
            'scattered_reads': [],
            'high_frequency': [],
            'single_register': [],
            'bulk_reads': [],
            'mixed_access': []
        }
        
        sorted_addrs = sorted(self.address_stats.keys())
        
        for i, addr in enumerate(sorted_addrs):
            stats = self.address_stats[addr]
            count = stats['count']
            quantities = stats['quantities']
            avg_quantity = sum(quantities) / len(quantities)
            
            # Categorize access patterns
            if count >= 50:
                patterns['high_frequency'].append({
                    'address': addr,
                    'count': count,
                    'avg_quantity': avg_quantity
                })
            
            if 1 in quantities and len(quantities) == 1:
                patterns['single_register'].append({
                    'address': addr,
                    'count': count
                })
            
            if max(quantities) >= 10:
                patterns['bulk_reads'].append({
                    'address': addr,
                    'max_quantity': max(quantities),
                    'count': count
                })
            
            if len(quantities) > 1:
                patterns['mixed_access'].append({
                    'address': addr,
                    'quantities': quantities,
                    'count': count
                })
        
        # Detect sequential reads
        for i in range(len(sorted_addrs) - 1):
            addr = sorted_addrs[i]
            next_addr = sorted_addrs[i + 1]
            
            if next_addr - addr <= 5:  # Within 5 address gap
                patterns['sequential_reads'][addr].append(next_addr)
            else:
                patterns['scattered_reads'].append({
                    'address': addr,
                    'gap_to_next': next_addr - addr
                })
        
        return patterns
    
    def generate_report(self, output_file='address_analysis.txt'):
        """Generate comprehensive analysis report."""
        report = []
        report.append("=" * 80)
        report.append("MODBUS ADDRESS ANALYSIS REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 80)
        
        # Summary statistics
        report.append("\n1. SUMMARY STATISTICS")
        report.append("-" * 80)
        report.append(f"Total unique starting addresses: {len(self.address_stats)}")
        report.append(f"Total unit IDs found: {sorted(self.unit_ids)}")
        report.append(f"Function codes used: {dict(sorted(self.function_codes.items()))}")
        report.append(f"Address range: {min(self.address_stats.keys())} - {max(self.address_stats.keys())}")
        
        # Function code breakdown
        report.append("\n2. FUNCTION CODE BREAKDOWN")
        report.append("-" * 80)
        fc_names = {
            1: "Read Coils",
            2: "Read Discrete Inputs",
            3: "Read Holding Registers",
            4: "Read Input Registers",
            5: "Write Single Coil",
            6: "Write Single Register",
            15: "Write Multiple Coils",
            16: "Write Multiple Registers"
        }
        for fc, count in sorted(self.function_codes.items()):
            name = fc_names.get(fc, "Unknown")
            report.append(f"  FC{fc:2d} ({name:30s}): {count:6d} times")
        
        # Top accessed addresses
        report.append("\n3. TOP 20 MOST FREQUENTLY ACCESSED ADDRESSES")
        report.append("-" * 80)
        sorted_by_count = sorted(
            self.address_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:20]
        
        for addr, stats in sorted_by_count:
            quantities_str = ', '.join(map(str, sorted(set(stats['quantities']))))
            devices = ', '.join(map(str, sorted(stats['devices'])))
            report.append(f"  Address 0x{addr:04X} ({addr:5d}): {stats['count']:4d} accesses, "
                        f"Qty: [{quantities_str}], Units: [{devices}]")
        
        # Address ranges analysis
        report.append("\n4. ADDRESS RANGE ANALYSIS")
        report.append("-" * 80)
        
        # Group into ranges
        ranges = defaultdict(list)
        for addr in sorted(self.address_stats.keys()):
            range_key = (addr // 100) * 100
            ranges[range_key].append(addr)
        
        for start in sorted(ranges.keys()):
            addrs = ranges[start]
            count = sum(self.address_stats[a]['count'] for a in addrs)
            report.append(f"  Range 0x{start:04X}-0x{start+99:04X}: {len(addrs):3d} addresses, "
                        f"{count:5d} total accesses")
        
        # Read/Write patterns
        report.append("\n5. READ/WRITE PATTERNS")
        report.append("-" * 80)
        read_addrs = [a for a, s in self.address_stats.items() if s['read']]
        write_addrs = [a for a, s in self.address_stats.items() if s['write']]
        both_addrs = [a for a in read_addrs if a in write_addrs]
        
        report.append(f"  Read-only addresses: {len(read_addrs)}")
        report.append(f"  Write-only addresses: {len(write_addrs)}")
        report.append(f"  Read+Write addresses: {len(both_addrs)}")
        
        if both_addrs:
            report.append(f"\n  Addresses with both read and write:")
            for addr in sorted(both_addrs)[:10]:
                report.append(f"    0x{addr:04X} ({addr})")
        
        # Quantity distribution
        report.append("\n6. QUANTITY (LENGTH) DISTRIBUTION")
        report.append("-" * 80)
        qty_distribution = defaultdict(int)
        for stats in self.address_stats.values():
            for qty in stats['quantities']:
                qty_distribution[qty] += 1
        
        for qty in sorted(qty_distribution.keys()):
            count = qty_distribution[qty]
            pct = (count / len(self.address_stats)) * 100
            report.append(f"  Quantity {qty:3d}: {count:4d} addresses ({pct:5.1f}%)")
        
        # Data access patterns
        patterns = self.analyze_patterns()
        
        report.append("\n7. DATA ACCESS PATTERNS")
        report.append("-" * 80)
        report.append(f"  High-frequency addresses (>=50 accesses): {len(patterns['high_frequency'])}")
        if patterns['high_frequency']:
            for item in patterns['high_frequency'][:5]:
                report.append(f"    0x{item['address']:04X}: {item['count']} accesses, "
                            f"avg qty {item['avg_quantity']:.1f}")
        
        report.append(f"\n  Single-register reads: {len(patterns['single_register'])}")
        report.append(f"  Bulk reads (qty>=10): {len(patterns['bulk_reads'])}")
        report.append(f"  Mixed-quantity addresses: {len(patterns['mixed_access'])}")
        
        # Device-specific analysis
        report.append("\n8. DEVICE-SPECIFIC ACCESS PATTERNS")
        report.append("-" * 80)
        for unit_id in sorted(self.unit_ids):
            unit_addrs = [a for a, s in self.address_stats.items() if unit_id in s['devices']]
            if unit_addrs:
                total_accesses = sum(self.address_stats[a]['count'] for a in unit_addrs)
                report.append(f"  Unit {unit_id}: {len(unit_addrs)} addresses, {total_accesses} total accesses")
        
        # Save report
        report_text = '\n'.join(report)
        with open(output_file, 'w') as f:
            f.write(report_text)
        
        print(f"\nReport saved to: {output_file}")
        return report_text
    
    def generate_json_output(self, output_file='address_analysis.json'):
        """Generate machine-readable JSON output."""
        output = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'total_unique_addresses': len(self.address_stats),
                'unit_ids': sorted(self.unit_ids),
                'function_codes': dict(self.function_codes)
            },
            'addresses': {}
        }
        
        for addr, stats in sorted(self.address_stats.items()):
            output['addresses'][f"0x{addr:04X}"] = {
                'decimal': addr,
                'access_count': stats['count'],
                'quantities_read': sorted(set(stats['quantities'])),
                'is_read': stats['read'],
                'is_write': stats['write'],
                'function_codes': sorted(set(stats['functions'])),
                'devices': sorted(stats['devices']),
                'timestamp_first': stats['timestamps'][0] if stats['timestamps'] else None,
                'timestamp_last': stats['timestamps'][-1] if stats['timestamps'] else None
            }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"JSON output saved to: {output_file}")
        return output

def main():
    """Run analysis."""
    analyzer = AddressAnalyzer()
    
    # Try to find JSON output from previous tshark capture
    json_file = 'modbus_capture.json'
    
    # If not found, try to extract from PCAPNG
    if not Path(json_file).exists():
        print("Note: To use this script, first generate JSON output from tshark:")
        print('  tshark -r captures/modbus_test_2min.pcapng -T json > modbus_capture.json')
        print("\nFor demonstration, using sample data...\n")
        
        # Create sample analysis with known addresses
        sample_addresses = {
            0x0000: {'count': 156, 'quantities': [10], 'read': True, 'functions': [3]},
            0x000A: {'count': 149, 'quantities': [8], 'read': True, 'functions': [3]},
            0x0012: {'count': 151, 'quantities': [6], 'read': True, 'functions': [3]},
            0x0018: {'count': 95, 'quantities': [2], 'read': True, 'functions': [3]},
            0x001A: {'count': 89, 'quantities': [4], 'read': True, 'functions': [3]},
            0x001E: {'count': 12, 'quantities': [1], 'read': True, 'functions': [3]},
            0x001F: {'count': 12, 'quantities': [1], 'read': True, 'functions': [3]},
            0x0020: {'count': 147, 'quantities': [8], 'read': True, 'functions': [3]},
            0x0028: {'count': 150, 'quantities': [6], 'read': True, 'functions': [3]},
            0x002E: {'count': 12, 'quantities': [1], 'read': True, 'functions': [3]},
        }
        
        analyzer.function_codes[3] = 1173
        analyzer.unit_ids = {1, 2, 3, 4, 5, 6, 247}
        
        for addr, stats in sample_addresses.items():
            analyzer.address_stats[addr] = {
                'count': stats['count'],
                'quantities': stats['quantities'],
                'read': stats['read'],
                'write': False,
                'functions': stats['functions'],
                'timestamps': [],
                'devices': {1, 2, 3}
            }
    else:
        analyzer.analyze_from_json(json_file)
    
    # Generate outputs
    print("\n" + "="*80)
    print("GENERATING ANALYSIS REPORTS...")
    print("="*80)
    
    report = analyzer.generate_report('address_analysis.txt')
    analyzer.generate_json_output('address_analysis.json')
    
    print("\n" + report[:500] + "\n...")

if __name__ == '__main__':
    main()
