#!/usr/bin/env python3
"""
PCAP/PCAPNG Modbus Frame Extractor
Reads Wireshark captures and extracts raw Modbus TCP frames
"""

import struct
import json
from pathlib import Path
from typing import List, BinaryIO
import sys


class PCAPReader:
    """Reads PCAP/PCAPNG files"""

    def __init__(self, filename: str):
        self.filename = filename
        self.frames = []
        self.is_pcapng = False

    def read(self) -> List[bytes]:
        """Read PCAP or PCAPNG file and return Modbus frames"""
        with open(self.filename, 'rb') as f:
            magic = f.read(4)
            f.seek(0)

            if magic == b'\x0a\x0d\x0d\x0a':  # PCAPNG
                self.is_pcapng = True
                return self._read_pcapng(f)
            else:
                self.is_pcapng = False
                return self._read_pcap(f)

    def _read_pcap(self, f: BinaryIO) -> List[bytes]:
        """Read standard PCAP format"""
        frames = []
        
        # Read global header
        magic = struct.unpack('>I', f.read(4))[0]
        version_major = struct.unpack('>H', f.read(2))[0]
        version_minor = struct.unpack('>H', f.read(2))[0]
        
        f.read(4)  # timezone
        f.read(4)  # timestamp accuracy
        snaplen = struct.unpack('>I', f.read(4))[0]
        network = struct.unpack('>I', f.read(4))[0]

        # Read packet records
        while True:
            header = f.read(16)
            if not header or len(header) < 16:
                break

            ts_sec = struct.unpack('>I', header[0:4])[0]
            ts_usec = struct.unpack('>I', header[4:8])[0]
            incl_len = struct.unpack('>I', header[8:12])[0]
            orig_len = struct.unpack('>I', header[12:16])[0]

            packet_data = f.read(incl_len)
            if len(packet_data) < incl_len:
                break

            # Extract Modbus TCP frame (skip Ethernet, IP, TCP headers)
            modbus_frame = self._extract_modbus_tcp(packet_data)
            if modbus_frame:
                frames.append(modbus_frame)

        return frames

    def _read_pcapng(self, f: BinaryIO) -> List[bytes]:
        """Read PCAPNG format"""
        frames = []

        while True:
            # Read block type and length
            header = f.read(8)
            if not header or len(header) < 8:
                break

            block_type = struct.unpack('>I', header[0:4])[0]
            block_len = struct.unpack('>I', header[4:8])[0]

            if block_type == 0x06:  # Enhanced Packet Block
                block_data = f.read(block_len - 8)
                packet_data = self._parse_epb(block_data)
                
                if packet_data:
                    modbus_frame = self._extract_modbus_tcp(packet_data)
                    if modbus_frame:
                        frames.append(modbus_frame)
            else:
                # Skip other blocks
                f.read(block_len - 8)

            # Read trailing length
            f.read(4)

        return frames

    def _parse_epb(self, data: bytes) -> bytes:
        """Parse Enhanced Packet Block"""
        try:
            if_id = struct.unpack('>I', data[0:4])[0]
            ts_hi = struct.unpack('>I', data[4:8])[0]
            ts_lo = struct.unpack('>I', data[8:12])[0]
            incl_len = struct.unpack('>I', data[12:16])[0]
            orig_len = struct.unpack('>I', data[16:20])[0]

            packet_data = data[20:20+incl_len]
            return packet_data
        except:
            return None

    def _extract_modbus_tcp(self, packet: bytes) -> bytes:
        """Extract Modbus TCP payload from Ethernet/IP/TCP packet"""
        try:
            # Skip Ethernet header (14 bytes) if present
            offset = 0
            if len(packet) > 14:
                eth_type = struct.unpack('>H', packet[12:14])[0]
                if eth_type == 0x0800:  # IPv4
                    offset = 14

            # Parse IPv4 header
            if offset < len(packet):
                ip_version = (packet[offset] >> 4) & 0x0F
                if ip_version == 4:
                    ihl = (packet[offset] & 0x0F) * 4
                    tcp_offset = offset + ihl

                    # Skip TCP header (minimum 20 bytes)
                    if tcp_offset + 20 <= len(packet):
                        tcp_header_len = ((packet[tcp_offset + 12] >> 4) & 0x0F) * 4
                        modbus_offset = tcp_offset + tcp_header_len

                        if modbus_offset < len(packet):
                            return packet[modbus_offset:]

            return None
        except:
            return None


class ModbusFrameProcessor:
    """Process extracted Modbus frames"""

    @staticmethod
    def parse_modbus_tcp(data: bytes) -> dict:
        """Parse Modbus TCP frame"""
        if len(data) < 12:
            return None

        try:
            transaction_id = struct.unpack('>H', data[0:2])[0]
            protocol_id = struct.unpack('>H', data[2:4])[0]
            length = struct.unpack('>H', data[4:6])[0]
            unit_id = data[6]
            function_code = data[7]

            if protocol_id != 0:
                return None

            result = {
                'transaction_id': transaction_id,
                'protocol_code': protocol_id,
                'length': length,
                'unit_id': unit_id,
                'function_code': function_code,
                'function_name': ModbusFrameProcessor._get_function_name(function_code),
                'raw_hex': data.hex().upper(),
            }

            # Parse function-specific data
            if function_code in [1, 2, 3, 4]:  # Read operations
                if len(data) >= 12:
                    result['starting_address'] = struct.unpack('>H', data[8:10])[0]
                    result['quantity'] = struct.unpack('>H', data[10:12])[0]
            elif function_code in [5, 6]:  # Write single
                if len(data) >= 12:
                    result['address'] = struct.unpack('>H', data[8:10])[0]
                    result['value'] = struct.unpack('>H', data[10:12])[0]
            elif function_code in [15, 16]:  # Write multiple
                if len(data) >= 13:
                    result['starting_address'] = struct.unpack('>H', data[8:10])[0]
                    result['quantity'] = struct.unpack('>H', data[10:12])[0]
                    result['byte_count'] = data[12]

            return result
        except Exception as e:
            return None

    @staticmethod
    def _get_function_name(code: int) -> str:
        functions = {
            1: "Read Coils",
            2: "Read Discrete Inputs",
            3: "Read Holding Registers",
            4: "Read Input Registers",
            5: "Write Single Coil",
            6: "Write Single Register",
            15: "Write Multiple Coils",
            16: "Write Multiple Registers",
        }
        return functions.get(code, "Unknown")


def main():
    if len(sys.argv) < 2:
        print("Usage: python pcap_extractor.py <pcap_or_pcapng_file> [output_json]")
        print("\nExample:")
        print("  python pcap_extractor.py captures\\modbus_20251210_1430.pcapng frames.json")
        return

    pcap_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else "extracted_frames.json"

    print(f"Reading {pcap_file}...")
    reader = PCAPReader(pcap_file)
    raw_frames = reader.read()

    print(f"Found {len(raw_frames)} potential Modbus frames")

    # Parse frames
    parsed_frames = []
    for raw_frame in raw_frames:
        parsed = ModbusFrameProcessor.parse_modbus_tcp(raw_frame)
        if parsed:
            parsed_frames.append(parsed)

    print(f"Successfully parsed {len(parsed_frames)} Modbus TCP frames")

    # Save to JSON
    output = {
        "source_file": pcap_file,
        "total_frames": len(parsed_frames),
        "frames": parsed_frames,
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nExtracted frames saved to {output_file}")

    # Print summary
    print("\nFrame Summary:")
    read_frames = [f for f in parsed_frames if f['function_code'] in [1, 2, 3, 4]]
    write_frames = [f for f in parsed_frames if f['function_code'] in [5, 6, 15, 16]]
    print(f"  Read Operations: {len(read_frames)}")
    print(f"  Write Operations: {len(write_frames)}")

    # Unique addresses accessed
    addresses = set()
    for f in parsed_frames:
        if 'starting_address' in f:
            addresses.add(f['starting_address'])
        elif 'address' in f:
            addresses.add(f['address'])

    print(f"  Unique Addresses: {len(addresses)}")
    if addresses:
        print(f"  Address Range: {min(addresses)} - {max(addresses)}")


if __name__ == "__main__":
    main()
