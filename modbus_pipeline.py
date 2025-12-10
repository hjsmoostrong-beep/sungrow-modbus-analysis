#!/usr/bin/env python3
"""
Integrated Modbus Capture -> Register Map Pipeline
Combines frame extraction, analysis, and mapping in one workflow
"""

import json
import sys
from pathlib import Path
from modbus_decoder import ModbusDecoder, RegisterType
from pcap_extractor import PCAPReader, ModbusFrameProcessor


class ModbusAnalysisPipeline:
    """End-to-end pipeline: PCAP -> Frames -> Register Map"""

    def __init__(self):
        self.raw_frames = []
        self.parsed_frames = []
        self.decoder = ModbusDecoder()

    def process_pcap(self, pcap_file: str):
        """Step 1: Extract frames from PCAP"""
        print(f"\n[STEP 1] Extracting Modbus frames from {pcap_file}...")
        
        reader = PCAPReader(pcap_file)
        self.raw_frames = reader.read()
        
        print(f"  Found {len(self.raw_frames)} frames")

    def parse_frames(self):
        """Step 2: Parse into structured data"""
        print(f"\n[STEP 2] Parsing Modbus TCP frames...")
        
        for i, raw_frame in enumerate(self.raw_frames):
            parsed = ModbusFrameProcessor.parse_modbus_tcp(raw_frame)
            if parsed:
                self.parsed_frames.append(parsed)
                self.decoder.parse_frame(raw_frame, direction="capture")

        print(f"  Parsed {len(self.parsed_frames)} valid frames")

    def analyze_patterns(self):
        """Step 3: Analyze traffic patterns"""
        print(f"\n[STEP 3] Analyzing access patterns...")
        
        patterns = self.decoder.analyze_traffic_patterns()
        
        print(f"  Unique read addresses: {len(patterns['reads'])}")
        print(f"  Unique write addresses: {len(patterns['writes'])}")
        print(f"  Most accessed: {patterns['most_accessed'][:5]}")
        
        return patterns

    def generate_mapping(self, output_json: str):
        """Step 4: Generate register mapping"""
        print(f"\n[STEP 4] Generating register mapping...")
        
        self.decoder.generate_register_map_json(output_json)
        
        print(f"  Saved to {output_json}")

    def generate_summary_report(self, output_txt: str):
        """Generate human-readable report"""
        print(f"\n[STEP 5] Generating analysis report...")
        
        with open(output_txt, 'w') as f:
            f.write("="*70 + "\n")
            f.write("SUNGROW MODBUS ANALYSIS REPORT\n")
            f.write("="*70 + "\n\n")

            f.write(f"Input File: PCAP Capture\n")
            f.write(f"Total Frames: {len(self.raw_frames)}\n")
            f.write(f"Valid Modbus Frames: {len(self.parsed_frames)}\n\n")

            # Frame statistics
            read_frames = [f for f in self.parsed_frames if f['function_code'] in [1, 2, 3, 4]]
            write_frames = [f for f in self.parsed_frames if f['function_code'] in [5, 6, 15, 16]]

            f.write("TRAFFIC BREAKDOWN:\n")
            f.write(f"  Read Operations: {len(read_frames)}\n")
            f.write(f"  Write Operations: {len(write_frames)}\n\n")

            # Function breakdown
            f.write("FUNCTION CODE BREAKDOWN:\n")
            func_codes = {}
            for frame in self.parsed_frames:
                func = frame.get('function_name', 'Unknown')
                func_codes[func] = func_codes.get(func, 0) + 1

            for func, count in sorted(func_codes.items()):
                f.write(f"  {func}: {count}\n")

            f.write("\n")

            # Address ranges
            addresses = set()
            for f_data in self.parsed_frames:
                if 'starting_address' in f_data:
                    addresses.add(f_data['starting_address'])
                elif 'address' in f_data:
                    addresses.add(f_data['address'])

            if addresses:
                f.write("ADDRESS RANGES:\n")
                f.write(f"  Min Address: {min(addresses)}\n")
                f.write(f"  Max Address: {max(addresses)}\n")
                f.write(f"  Unique Addresses: {len(addresses)}\n\n")

                # Categorize by known groups
                f.write("EXPECTED REGISTER GROUPS:\n")
                groups = {
                    "Inverter Info": (0, 50),
                    "Grid/AC Data": (100, 199),
                    "DC/PV Input": (200, 299),
                    "Weather Station": (300, 399),
                    "Energy Counters": (500, 599),
                    "Faults/Alarms": (1000, 1100),
                }

                for group_name, (start, end) in groups.items():
                    matching = [a for a in addresses if start <= a <= end]
                    if matching:
                        f.write(f"  {group_name} ({start}-{end}): {len(matching)} addresses\n")
                        f.write(f"    Addresses: {sorted(matching)}\n")

            f.write("\n" + "="*70 + "\n")
            f.write("RECOMMENDATIONS:\n")
            f.write("="*70 + "\n\n")

            f.write("1. Register Mapping:\n")
            f.write("   - See register_map_*.json for detailed mapping suggestions\n")
            f.write("   - Registers are grouped by function (Inverter, Grid, Weather, etc.)\n\n")

            f.write("2. Next Steps:\n")
            f.write("   - Validate mapping against Sungrow documentation\n")
            f.write("   - Adjust scale/offset factors based on physical readings\n")
            f.write("   - Update unit strings for engineering values\n\n")

            f.write("3. Data Types:\n")
            f.write("   - Most registers are UINT16 (16-bit unsigned)\n")
            f.write("   - Temperature/Power typically UINT32 or INT32\n")
            f.write("   - Voltages/Currents may need scaling (÷10, ÷100)\n\n")

        print(f"  Report saved to {output_txt}")

    def run(self, pcap_file: str, output_prefix: str = "modbus_analysis"):
        """Run complete pipeline"""
        print("\n" + "="*70)
        print("SUNGROW MODBUS CAPTURE ANALYSIS PIPELINE")
        print("="*70)

        try:
            self.process_pcap(pcap_file)
            self.parse_frames()
            self.analyze_patterns()
            
            json_output = f"{output_prefix}_map.json"
            txt_output = f"{output_prefix}_report.txt"
            
            self.generate_mapping(json_output)
            self.generate_summary_report(txt_output)

            print("\n" + "="*70)
            print("PIPELINE COMPLETE")
            print("="*70)
            print(f"\nOutputs:")
            print(f"  - Register Map: {json_output}")
            print(f"  - Summary Report: {txt_output}")
            print(f"\nNext steps:")
            print(f"  1. Review the register mapping JSON")
            print(f"  2. Cross-reference with Sungrow documentation")
            print(f"  3. Update scale factors and units as needed")

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python modbus_pipeline.py <pcap_file> [output_prefix]")
        print("\nExample:")
        print("  python modbus_pipeline.py captures\\modbus_20251210_1430.pcapng sungrow_logger")
        print("\nThis will generate:")
        print("  - sungrow_logger_map.json (register mapping)")
        print("  - sungrow_logger_report.txt (analysis report)")
        return

    pcap_file = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) >= 3 else Path(pcap_file).stem

    if not Path(pcap_file).exists():
        print(f"Error: File not found: {pcap_file}")
        return

    pipeline = ModbusAnalysisPipeline()
    pipeline.run(pcap_file, output_prefix)


if __name__ == "__main__":
    main()
