#!/usr/bin/env python3
"""
Enhanced Modbus Decoder for Sungrow Logger
Parses raw Modbus TCP frames with grouping, heuristics, and mapping suggestions
"""

import struct
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from enum import Enum
from pathlib import Path


class ModbusFunction(Enum):
    """Modbus function codes"""
    READ_COILS = 1
    READ_DISCRETE_INPUTS = 2
    READ_HOLDING_REGISTERS = 3
    READ_INPUT_REGISTERS = 4
    WRITE_SINGLE_COIL = 5
    WRITE_SINGLE_REGISTER = 6
    WRITE_MULTIPLE_COILS = 15
    WRITE_MULTIPLE_REGISTERS = 16


class RegisterType(Enum):
    """Register data types"""
    UINT16 = "uint16"
    INT16 = "int16"
    UINT32 = "uint32"
    INT32 = "int32"
    FLOAT32 = "float32"
    STRING = "string"
    BITS = "bits"


@dataclass
class ModbusFrame:
    """Parsed Modbus TCP frame"""
    transaction_id: int
    protocol_id: int
    length: int
    unit_id: int
    function_code: int
    starting_address: int
    quantity: int
    raw_data: bytes
    direction: str  # "request" or "response"
    timestamp: float = 0.0


@dataclass
class Register:
    """Modbus register mapping"""
    address: int
    name: str
    type: RegisterType
    count: int  # number of registers (1 for 16-bit, 2 for 32-bit, etc.)
    scale: float = 1.0
    offset: float = 0.0
    unit: str = ""
    description: str = ""
    group: str = "Uncategorized"
    access: str = "read"  # read, write, read/write


class ModbusDecoder:
    """Decodes Modbus TCP frames and suggests register mapping"""

    def __init__(self):
        self.frames: List[ModbusFrame] = []
        self.register_map: Dict[int, Register] = {}
        self.register_access_patterns: Dict[int, Dict] = {}
        
        # Known Sungrow register patterns
        self.sungrow_hints = self._load_sungrow_hints()

    def _load_sungrow_hints(self) -> Dict:
        """Load known Sungrow register hints based on industry knowledge"""
        return {
            # Inverter Info (typical range 0-100)
            (0, 50): {
                "group": "Inverter_Info",
                "hints": ["serial_number", "model", "firmware", "status"],
            },
            # Grid/AC Data (typical range 100-200)
            (100, 199): {
                "group": "Grid_AC_Data",
                "hints": ["voltage_phase_a", "voltage_phase_b", "voltage_phase_c",
                         "current_phase_a", "current_phase_b", "current_phase_c",
                         "frequency", "power_output"],
            },
            # DC/PV Input (typical range 200-300)
            (200, 299): {
                "group": "DC_PV_Input",
                "hints": ["pv1_voltage", "pv1_current", "pv2_voltage", "pv2_current",
                         "pv1_power", "pv2_power", "total_pv_power"],
            },
            # Weather/Environmental (typical range 300-400)
            (300, 399): {
                "group": "Weather_Station",
                "hints": ["temperature", "humidity", "irradiance", "wind_speed"],
            },
            # Energy Counters (typical range 500-600)
            (500, 599): {
                "group": "Energy_Counters",
                "hints": ["total_energy_produced", "daily_energy", "total_import",
                         "total_export"],
            },
            # Faults/Alarms (typical range 1000+)
            (1000, 1100): {
                "group": "Faults_Alarms",
                "hints": ["fault_code", "alarm_code", "warning_code"],
            },
        }

    def parse_frame(self, data: bytes, direction: str = "request", timestamp: float = 0.0) -> Optional[ModbusFrame]:
        """Parse a raw Modbus TCP frame"""
        if len(data) < 12:
            return None

        try:
            transaction_id = struct.unpack(">H", data[0:2])[0]
            protocol_id = struct.unpack(">H", data[2:4])[0]
            length = struct.unpack(">H", data[4:6])[0]
            unit_id = data[6]
            function_code = data[7]

            if protocol_id != 0:  # Not Modbus
                return None

            frame = ModbusFrame(
                transaction_id=transaction_id,
                protocol_id=protocol_id,
                length=length,
                unit_id=unit_id,
                function_code=function_code,
                starting_address=0,
                quantity=0,
                raw_data=data[8:],
                direction=direction,
                timestamp=timestamp,
            )

            # Parse function-specific fields
            if function_code in [1, 2, 3, 4]:  # Read operations
                if len(data) >= 12:
                    frame.starting_address = struct.unpack(">H", data[8:10])[0]
                    frame.quantity = struct.unpack(">H", data[10:12])[0]
            elif function_code in [5, 6]:  # Write single
                if len(data) >= 12:
                    frame.starting_address = struct.unpack(">H", data[8:10])[0]
            elif function_code in [15, 16]:  # Write multiple
                if len(data) >= 13:
                    frame.starting_address = struct.unpack(">H", data[8:10])[0]
                    frame.quantity = struct.unpack(">H", data[10:12])[0]

            self.frames.append(frame)
            return frame
        except Exception as e:
            print(f"Error parsing frame: {e}")
            return None

    def analyze_traffic_patterns(self) -> Dict:
        """Analyze patterns in captured traffic"""
        patterns = {
            "reads": {},
            "writes": {},
            "most_accessed": [],
            "access_sequences": [],
        }

        # Track access patterns
        for frame in self.frames:
            func = ModbusFunction(frame.function_code).name if frame.function_code in [f.value for f in ModbusFunction] else "UNKNOWN"
            
            if frame.function_code in [1, 2, 3, 4]:  # Read operations
                if frame.starting_address not in patterns["reads"]:
                    patterns["reads"][frame.starting_address] = {
                        "count": 0,
                        "quantities": [],
                        "function": func,
                    }
                patterns["reads"][frame.starting_address]["count"] += 1
                patterns["reads"][frame.starting_address]["quantities"].append(frame.quantity)

            elif frame.function_code in [5, 6, 15, 16]:  # Write operations
                if frame.starting_address not in patterns["writes"]:
                    patterns["writes"][frame.starting_address] = {
                        "count": 0,
                        "function": func,
                    }
                patterns["writes"][frame.starting_address]["count"] += 1

        # Find most accessed registers
        all_accesses = {
            addr: data["count"] for addr, data in patterns["reads"].items()
        }
        patterns["most_accessed"] = sorted(
            all_accesses.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return patterns

    def suggest_register_mapping(self) -> List[Register]:
        """Suggest register mapping based on analysis"""
        suggestions = []
        patterns = self.analyze_traffic_patterns()

        for address, access_info in patterns["reads"].items():
            # Try to infer group from address range
            group = "Uncategorized"
            for range_start, range_end in self.sungrow_hints.keys():
                if range_start <= address <= range_end:
                    group = self.sungrow_hints[(range_start, range_end)]["group"]
                    break

            # Infer data type from access patterns
            quantities = access_info.get("quantities", [1])
            avg_quantity = sum(quantities) / len(quantities) if quantities else 1
            
            if avg_quantity >= 2:
                reg_type = RegisterType.UINT32
                count = 2
            else:
                reg_type = RegisterType.UINT16
                count = 1

            # Generate hints for name
            hints = []
            for range_key, range_hints in self.sungrow_hints.items():
                if range_key[0] <= address <= range_key[1]:
                    hints = range_hints.get("hints", [])
                    break

            # Create register suggestion
            reg = Register(
                address=address,
                name=f"{group.lower()}_reg_{address:04d}",
                type=reg_type,
                count=count,
                unit="",
                description=f"Accessed {access_info['count']} times via {access_info['function']}",
                group=group,
                access="read",
            )
            suggestions.append(reg)

        return sorted(suggestions, key=lambda r: r.address)

    def generate_register_map_json(self, output_file: str):
        """Generate register map in JSON format"""
        suggestions = self.suggest_register_mapping()
        
        register_map = {
            "decoder_version": "1.0",
            "device": "Sungrow_Logger",
            "device_ip": "192.168.1.5",
            "total_frames_captured": len(self.frames),
            "groups": {},
        }

        # Group registers
        for reg in suggestions:
            if reg.group not in register_map["groups"]:
                register_map["groups"][reg.group] = []
            
            register_map["groups"][reg.group].append({
                "address": reg.address,
                "name": reg.name,
                "type": reg.type.value,
                "count": reg.count,
                "scale": reg.scale,
                "offset": reg.offset,
                "unit": reg.unit,
                "description": reg.description,
                "access": reg.access,
            })

        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(register_map, f, indent=2)

        return register_map

    def print_analysis_report(self):
        """Print human-readable analysis report"""
        print("\n" + "="*70)
        print("MODBUS CAPTURE ANALYSIS REPORT")
        print("="*70)

        print(f"\nTotal Frames Captured: {len(self.frames)}")

        if not self.frames:
            print("No frames parsed.")
            return

        # Frame statistics
        read_frames = [f for f in self.frames if f.function_code in [1, 2, 3, 4]]
        write_frames = [f for f in self.frames if f.function_code in [5, 6, 15, 16]]

        print(f"\nFrame Types:")
        print(f"  - Read Operations: {len(read_frames)}")
        print(f"  - Write Operations: {len(write_frames)}")

        # Traffic patterns
        patterns = self.analyze_traffic_patterns()

        print(f"\nRegister Access Patterns:")
        print(f"  - Unique Read Addresses: {len(patterns['reads'])}")
        print(f"  - Unique Write Addresses: {len(patterns['writes'])}")

        print(f"\nMost Accessed Registers (Top 10):")
        for addr, count in patterns["most_accessed"]:
            print(f"  - Address {addr:4d}: {count:3d} accesses")

        # Suggestions
        suggestions = self.suggest_register_mapping()
        print(f"\nRegister Mapping Suggestions: {len(suggestions)} registers")

        # Group by category
        groups = {}
        for reg in suggestions:
            if reg.group not in groups:
                groups[reg.group] = []
            groups[reg.group].append(reg)

        for group_name in sorted(groups.keys()):
            regs = groups[group_name]
            print(f"\n  {group_name} ({len(regs)} registers):")
            for reg in regs[:5]:  # Show first 5 of each group
                print(f"    {reg.address:4d}: {reg.name:40s} ({reg.type.value})")
            if len(regs) > 5:
                print(f"    ... and {len(regs) - 5} more")


def main():
    """Example usage"""
    decoder = ModbusDecoder()

    print("Sungrow Modbus Decoder Ready")
    print("Usage: python modbus_decoder.py [pcapng_file] [output_json]")
    print("\nExample:")
    print("  python modbus_decoder.py captures\\modbus_20251210_1430.pcapng register_map.json")

    # If arguments provided, process them
    import sys
    if len(sys.argv) >= 2:
        pcapng_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) >= 3 else "register_map.json"

        print(f"\nProcessing {pcapng_file}...")
        print(f"Output will be saved to {output_file}")
        print("\nNote: To parse PCAPNG, install tshark or pyshark:")
        print("  pip install pyshark")
        print("\nThen add code to extract Modbus frames from PCAPNG.")


if __name__ == "__main__":
    main()
