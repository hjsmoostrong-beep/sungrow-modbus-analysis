#!/usr/bin/env python3
"""
Test harness - Demonstrates the decoder with sample Modbus data
"""

import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from modbus_decoder import ModbusDecoder, RegisterType


def test_decoder_with_sample_data():
    """Test the decoder with generated sample frames"""
    
    print("\n" + "="*70)
    print("SUNGROW MODBUS DECODER - TEST EXECUTION")
    print("="*70)
    
    # Generate test data
    print("\n[1] Generating sample Modbus frames...")
    from test_data_generator import generate_sample_modbus_frames
    
    frames = generate_sample_modbus_frames()
    print(f"    [OK] Generated {len(frames)} sample frames")
    
    # Initialize decoder
    print("\n[2] Initializing ModbusDecoder...")
    decoder = ModbusDecoder()
    print("    [OK] Decoder ready")
    
    # Parse frames
    print("\n[3] Parsing frames...")
    parsed_count = 0
    for i, frame in enumerate(frames):
        # Simulate raw bytes from hex string
        try:
            raw_bytes = bytes.fromhex(frame['raw_hex'])
            if decoder.parse_frame(raw_bytes, direction="request"):
                parsed_count += 1
        except:
            pass
    
    print(f"    [OK] Parsed {parsed_count}/{len(frames)} frames")
    
    # Analyze patterns
    print("\n[4] Analyzing traffic patterns...")
    patterns = decoder.analyze_traffic_patterns()
    print(f"    [OK] Found {len(patterns['reads'])} unique read addresses")
    print(f"    [OK] Found {len(patterns['writes'])} unique write addresses")
    print(f"    [OK] Top accessed addresses: {patterns['most_accessed'][:5]}")
    
    # Generate suggestions
    print("\n[5] Generating register mapping suggestions...")
    suggestions = decoder.suggest_register_mapping()
    print(f"    [OK] Generated {len(suggestions)} register suggestions")
    
    # Group by category
    groups = {}
    for reg in suggestions:
        if reg.group not in groups:
            groups[reg.group] = []
        groups[reg.group].append(reg)
    
    print("\n[6] Registers by Category:")
    for group_name in sorted(groups.keys()):
        regs = groups[group_name]
        print(f"    {group_name}: {len(regs)} registers")
        for reg in regs[:3]:
            print(f"      - Addr {reg.address:4d}: {reg.name:40s} ({reg.type.value})")
        if len(regs) > 3:
            print(f"      ... and {len(regs)-3} more")
    
    # Generate JSON mapping
    print("\n[7] Generating JSON register map...")
    output_file = "test_register_map.json"
    decoder.generate_register_map_json(output_file)
    print(f"    [OK] Saved to {output_file}")
    
    # Load and display
    with open(output_file, 'r') as f:
        register_map = json.load(f)
    
    print("\n[8] Register Map Summary:")
    print(f"    Device: {register_map['device']}")
    print(f"    IP Address: {register_map['device_ip']}")
    print(f"    Total Frames: {register_map['total_frames_captured']}")
    print(f"    Groups: {len(register_map['groups'])}")
    
    # Generate report
    print("\n[9] Generating analysis report...")
    decoder.print_analysis_report()
    
    print("\n" + "="*70)
    print("TEST COMPLETE - EXECUTION SUCCESSFUL")
    print("="*70)
    print("\nOutput files generated:")
    print(f"  - {output_file}")
    print("\nNext steps:")
    print("  1. Review the generated register_map.json")
    print("  2. Run with actual Wireshark captures:")
    print("     python modbus_pipeline.py captures/modbus_*.pcapng output_name")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_decoder_with_sample_data()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
