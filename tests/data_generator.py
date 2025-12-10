#!/usr/bin/env python3
"""
Test data generator - Creates sample Modbus frames for demonstration
"""

import json
import struct


def generate_sample_modbus_frames():
    """Generate sample Modbus TCP frames for testing"""
    
    frames = []
    
    # Sample 1: Read Inverter Info (registers 0-10)
    frames.append({
        "transaction_id": 1,
        "protocol_id": 0,
        "length": 6,
        "unit_id": 1,
        "function_code": 3,
        "function_name": "Read Holding Registers",
        "starting_address": 0,
        "quantity": 10,
        "raw_hex": "000100000006010300000000000A"
    })

    # Sample 2: Read Grid Data (registers 100-120)
    frames.append({
        "transaction_id": 2,
        "protocol_id": 0,
        "length": 6,
        "unit_id": 1,
        "function_code": 3,
        "function_name": "Read Holding Registers",
        "starting_address": 100,
        "quantity": 20,
        "raw_hex": "000200000006010300640000014"
    })

    # Sample 3: Read PV Input (registers 200-230)
    frames.append({
        "transaction_id": 3,
        "protocol_id": 0,
        "length": 6,
        "unit_id": 1,
        "function_code": 3,
        "function_name": "Read Holding Registers",
        "starting_address": 200,
        "quantity": 30,
        "raw_hex": "000300000006010300C8000001E"
    })

    # Sample 4: Read Weather Station (registers 300-320)
    frames.append({
        "transaction_id": 4,
        "protocol_id": 0,
        "length": 6,
        "unit_id": 1,
        "function_code": 3,
        "function_name": "Read Holding Registers",
        "starting_address": 300,
        "quantity": 20,
        "raw_hex": "000400000006010300012C000014"
    })

    # Sample 5: Read Energy Counters (registers 500-550)
    frames.append({
        "transaction_id": 5,
        "protocol_id": 0,
        "length": 6,
        "unit_id": 1,
        "function_code": 3,
        "function_name": "Read Holding Registers",
        "starting_address": 500,
        "quantity": 50,
        "raw_hex": "000500000006010301F4000032"
    })

    # Sample 6: Read Faults (registers 1000-1020)
    frames.append({
        "transaction_id": 6,
        "protocol_id": 0,
        "length": 6,
        "unit_id": 1,
        "function_code": 3,
        "function_name": "Read Holding Registers",
        "starting_address": 1000,
        "quantity": 20,
        "raw_hex": "000600000006010303E8000014"
    })

    # Multiple repeated accesses to show patterns
    for i in range(7, 50):
        # Repeat inverter info reads
        frames.append({
            "transaction_id": i,
            "protocol_id": 0,
            "length": 6,
            "unit_id": 1,
            "function_code": 3,
            "function_name": "Read Holding Registers",
            "starting_address": 0,
            "quantity": 10,
            "raw_hex": "000100000006010300000000000A"
        })

    return frames


def save_test_frames(filename="test_extracted_frames.json"):
    """Save test frames to JSON file"""
    frames = generate_sample_modbus_frames()
    
    data = {
        "source_file": "test_capture.pcapng",
        "total_frames": len(frames),
        "frames": frames
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated {len(frames)} test frames in {filename}")
    return filename


if __name__ == "__main__":
    save_test_frames()
