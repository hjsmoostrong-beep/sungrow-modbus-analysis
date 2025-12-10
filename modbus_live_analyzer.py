#!/usr/bin/env python3
"""
Modbus Frame Analyzer using binary parsing of PCAPNG output
"""

import subprocess
import json
from collections import defaultdict
from pathlib import Path
import struct


class ModbusLiveAnalyzer:
    """Analyze live Modbus capture data"""

    def __init__(self):
        self.frames = []
        self.unit_ids = set()
        self.address_patterns = defaultdict(int)
        self.unit_registers = defaultdict(lambda: defaultdict(set))

    def extract_from_pcapng(self, pcapng_file):
        """Extract frames by parsing hex output"""
        try:
            tshark_path = r"C:\Program Files\Wireshark\tshark.exe"
            
            # Get hex dump of Modbus packets
            cmd = [
                tshark_path,
                '-r', pcapng_file,
                '-Y', 'modbus',
                '-x',  # Hex dump
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return []
            
            lines = result.stdout.split('\n')
            frame_data = []
            current_frame = {'hex': '', 'data': []}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Frame'):
                    if current_frame['hex']:
                        frame_data.append(current_frame)
                    current_frame = {'hex': line, 'data': []}
                elif line.startswith('Modbus'):
                    current_frame['data'].append(line)
                elif len(line) > 0 and not any(line.startswith(x) for x in ['Transmission', 'Internet', 'Ethernet', '---']):
                    if current_frame['hex']:
                        current_frame['data'].append(line)
            
            if current_frame['hex']:
                frame_data.append(current_frame)
            
            print(f"Found {len(frame_data)} frames with Modbus data")
            
            # Now parse the Modbus TCP format
            # Modbus TCP: Transaction ID (2), Protocol ID (2), Length (2), Unit ID (1), Function Code (1), Data
            frames = self._parse_modbus_frames(pcapng_file)
            self.frames = frames
            return frames
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_modbus_frames(self, pcapng_file):
        """Parse PCAPNG file directly to extract Modbus frames"""
        frames = []
        frame_count = 0
        
        try:
            # Use tshark to extract raw bytes
            tshark_path = r"C:\Program Files\Wireshark\tshark.exe"
            cmd = [
                tshark_path,
                '-r', pcapng_file,
                '-Y', 'modbus',
                '-x',
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Parse hex dump output
            hex_lines = []
            for line in result.stdout.split('\n'):
                # Look for hex dump pattern: offset   hex bytes
                if ':' in line and any(c in line for c in '0123456789abcdef '):
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        hex_part = parts[1].strip()
                        # Extract just the hex digits
                        hex_bytes = hex_part.split('  ')[0].replace(' ', '')
                        if hex_bytes:
                            hex_lines.append(hex_bytes)
            
            # Reconstruct frames from hex lines
            if hex_lines:
                full_hex = ''.join(hex_lines)
                
                # Look for Modbus TCP packets (starting with reasonable transaction IDs)
                # Try to identify Modbus boundaries
                try:
                    # Convert to bytes
                    data = bytes.fromhex(full_hex)
                    
                    # Find Modbus frames: Protocol ID should be 0x0000
                    i = 0
                    while i < len(data) - 7:
                        # Check if this looks like a Modbus TCP header
                        if i + 6 < len(data):
                            protocol_id = struct.unpack('>H', data[i+2:i+4])[0]
                            
                            if protocol_id == 0:  # Modbus protocol ID
                                trans_id = struct.unpack('>H', data[i:i+2])[0]
                                msg_len = struct.unpack('>H', data[i+4:i+6])[0]
                                unit_id = data[i+6]
                                
                                if 0 < msg_len < 250:  # Reasonable length
                                    func_code = data[i+7] if i+7 < len(data) else 0
                                    
                                    if func_code in [1, 2, 3, 4, 5, 6, 15, 16]:  # Valid Modbus function codes
                                        # Extract frame data
                                        frame_end = i + 6 + msg_len
                                        if frame_end <= len(data):
                                            frame_bytes = data[i:frame_end]
                                            
                                            # Parse the frame
                                            parsed = self._parse_modbus_frame_bytes(frame_bytes)
                                            if parsed:
                                                frames.append(parsed)
                                                self.unit_ids.add(unit_id)
                                                frame_count += 1
                                            
                                            i = frame_end - 1
                        i += 1
                except Exception as e:
                    print(f"Error parsing hex data: {e}")
            
            print(f"Parsed {frame_count} Modbus frames from hex data")
            return frames
            
        except Exception as e:
            print(f"Error in frame parsing: {e}")
            return []

    def _parse_modbus_frame_bytes(self, frame_bytes):
        """Parse a single Modbus TCP frame"""
        try:
            if len(frame_bytes) < 8:
                return None
            
            trans_id = struct.unpack('>H', frame_bytes[0:2])[0]
            protocol_id = struct.unpack('>H', frame_bytes[2:4])[0]
            msg_len = struct.unpack('>H', frame_bytes[4:6])[0]
            unit_id = frame_bytes[6]
            func_code = frame_bytes[7]
            
            frame = {
                'transaction_id': trans_id,
                'protocol_id': protocol_id,
                'length': msg_len,
                'unit_id': unit_id,
                'function_code': func_code,
                'data': frame_bytes[8:].hex() if len(frame_bytes) > 8 else ''
            }
            
            # Parse function-specific data
            if func_code in [3, 4]:  # Read registers
                if len(frame_bytes) >= 12:
                    start_addr = struct.unpack('>H', frame_bytes[8:10])[0]
                    quantity = struct.unpack('>H', frame_bytes[10:12])[0]
                    frame['start_address'] = start_addr
                    frame['quantity'] = quantity
                    
                    # Infer category
                    frame['category'] = self._infer_category(start_addr)
                    
                    # Track pattern
                    pattern = f"FC{func_code}_Unit{unit_id}_Addr{start_addr}_Qty{quantity}"
                    self.address_patterns[pattern] += 1
                    self.unit_registers[unit_id][start_addr].add(quantity)
            
            elif func_code in [1, 2]:  # Read coils/inputs
                if len(frame_bytes) >= 12:
                    start_addr = struct.unpack('>H', frame_bytes[8:10])[0]
                    quantity = struct.unpack('>H', frame_bytes[10:12])[0]
                    frame['start_address'] = start_addr
                    frame['quantity'] = quantity
            
            return frame
            
        except Exception as e:
            return None

    def _infer_category(self, address):
        """Infer register category"""
        if 0 <= address <= 50:
            return 'Inverter_Info'
        elif 100 <= address <= 199:
            return 'Grid_AC'
        elif 200 <= address <= 299:
            return 'DC_PV'
        elif 300 <= address <= 399:
            return 'Weather'
        elif 500 <= address <= 599:
            return 'Energy_Counter'
        elif address >= 1000:
            return 'Faults_Alarms'
        else:
            return 'Other'

    def generate_report(self, output_file="modbus_live_report.txt"):
        """Generate analysis report"""
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("LIVE MODBUS CAPTURE ANALYSIS\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Total Frames Parsed: {len(self.frames)}\n")
            f.write(f"Unit IDs Found: {sorted(self.unit_ids)}\n\n")
            
            f.write("REGISTER ACCESS PATTERNS\n")
            f.write("-"*70 + "\n\n")
            
            for unit in sorted(self.unit_registers.keys()):
                f.write(f"Unit {unit}:\n")
                for addr in sorted(self.unit_registers[unit].keys()):
                    quantities = self.unit_registers[unit][addr]
                    category = self._infer_category(addr)
                    f.write(f"  Address {addr} ({category}): Quantities read = {quantities}\n")
                f.write("\n")
            
            f.write("\nMOST COMMON PATTERNS (top 30):\n")
            f.write("-"*70 + "\n")
            for pattern, count in sorted(self.address_patterns.items(), key=lambda x: -x[1])[:30]:
                f.write(f"  {pattern}: {count} times\n")
        
        print(f"Report written to {output_file}")

    def generate_mapping(self, output_file="modbus_live_mapping.json"):
        """Generate JSON mapping"""
        mapping = {
            'summary': {
                'total_frames': len(self.frames),
                'units': sorted(list(self.unit_ids)),
                'address_patterns': len(self.address_patterns),
            },
            'registers_by_unit': {},
            'patterns': {}
        }
        
        # Build register map per unit
        for unit in sorted(self.unit_registers.keys()):
            unit_map = {}
            for addr in sorted(self.unit_registers[unit].keys()):
                quantities = list(self.unit_registers[unit][addr])
                unit_map[str(addr)] = {
                    'address': addr,
                    'quantities_read': quantities,
                    'common_quantity': max(set(quantities), key=quantities.count) if quantities else 1,
                    'category': self._infer_category(addr),
                    'inferred_type': 'UINT32' if max(quantities) > 1 else 'UINT16' if max(quantities) == 1 else 'STRING'
                }
            mapping['registers_by_unit'][f'Unit_{unit}'] = unit_map
        
        # Top patterns
        for pattern, count in sorted(self.address_patterns.items(), key=lambda x: -x[1])[:50]:
            mapping['patterns'][pattern] = count
        
        with open(output_file, 'w') as f:
            json.dump(mapping, f, indent=2)
        
        print(f"Mapping written to {output_file}")


def main():
    pcapng_file = "captures/modbus_test_2min.pcapng"
    
    if not Path(pcapng_file).exists():
        print(f"Error: {pcapng_file} not found")
        return
    
    print("="*70)
    print("MODBUS LIVE CAPTURE ANALYZER")
    print("="*70 + "\n")
    
    analyzer = ModbusLiveAnalyzer()
    print(f"Analyzing: {pcapng_file}\n")
    
    frames = analyzer.extract_from_pcapng(pcapng_file)
    
    if not frames:
        print("No frames extracted - trying alternative approach...")
        return
    
    print(f"✓ Extracted {len(frames)} frames")
    print(f"✓ Units: {sorted(analyzer.unit_ids)}")
    print(f"✓ Patterns: {len(analyzer.address_patterns)}")
    
    print("\nGenerating outputs...")
    analyzer.generate_report("modbus_live_report.txt")
    analyzer.generate_mapping("modbus_live_mapping.json")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
