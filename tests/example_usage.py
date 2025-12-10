#!/usr/bin/env python3
"""
Practical Example: Using the generated register map in your application
"""

import json


def load_register_map(filename="test_register_map.json"):
    """Load the generated register mapping"""
    with open(filename, 'r') as f:
        return json.load(f)


def example_1_access_by_group():
    """Example 1: Get all registers in a specific group"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Access Registers by Group")
    print("="*70)
    
    register_map = load_register_map()
    
    print(f"\nDevice: {register_map['device']}")
    print(f"IP: {register_map['device_ip']}")
    print(f"Total Frames: {register_map['total_frames_captured']}")
    print(f"\nAvailable Groups:")
    
    for group_name, registers in register_map['groups'].items():
        print(f"\n  {group_name}:")
        for reg in registers:
            print(f"    Address {reg['address']:4d}: {reg['name']:40s} "
                  f"Type: {reg['type']:8s} Unit: {reg['unit']}")


def example_2_find_register_by_address():
    """Example 2: Find register by address"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Look Up Register by Address")
    print("="*70)
    
    register_map = load_register_map()
    
    # Build address index
    address_map = {}
    for group_name, registers in register_map['groups'].items():
        for reg in registers:
            address_map[reg['address']] = {**reg, 'group': group_name}
    
    # Look up specific addresses
    test_addresses = [0, 500, 1000]
    
    for addr in test_addresses:
        if addr in address_map:
            reg = address_map[addr]
            print(f"\nAddress {addr}:")
            print(f"  Name: {reg['name']}")
            print(f"  Group: {reg['group']}")
            print(f"  Type: {reg['type']} ({reg['count']} register(s))")
            print(f"  Access: {reg['access']}")
            print(f"  Description: {reg['description']}")
        else:
            print(f"\nAddress {addr}: Not found in mapping")


def example_3_build_modbus_query():
    """Example 3: Generate Modbus read command from mapping"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Build Modbus Read Commands")
    print("="*70)
    
    register_map = load_register_map()
    
    print("\nBuilding Modbus Function 3 (Read Holding Registers) commands:")
    print("Format: Function | Start Address | Quantity | Register Names")
    print("-" * 70)
    
    for group_name, registers in sorted(register_map['groups'].items()):
        if not registers:
            continue
        
        addresses = sorted([reg['address'] for reg in registers])
        start = addresses[0]
        end = addresses[-1]
        quantity = end - start + 1
        
        names = [registers[i]['name'] for i in range(min(2, len(registers)))]
        
        print(f"Function 3 | Start: {start:4d} | Qty: {quantity:2d} | "
              f"Group: {group_name}")
        print(f"            Registers: {', '.join(names)}")
        if len(registers) > 2:
            print(f"                      ... and {len(registers)-2} more")


def example_4_monitoring_script():
    """Example 4: Template for monitoring script using the mapping"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Monitoring Script Template")
    print("="*70)
    
    print("""
# Python script using the register mapping
import json
import pymodbus  # Example Modbus library

register_map = json.load(open('sungrow_logger_map.json'))

def read_all_registers(client):
    '''Read all mapped registers from device'''
    
    results = {}
    
    # Read by group for organization
    for group_name, registers in register_map['groups'].items():
        print(f"Reading {group_name}...")
        results[group_name] = {}
        
        for reg in registers:
            address = reg['address']
            name = reg['name']
            reg_type = reg['type']
            
            # Read from Modbus
            response = client.read_holding_registers(
                address=address,
                count=reg['count'],
                unit=1
            )
            
            if response.isError():
                print(f"  ERROR reading {name} at {address}")
            else:
                results[group_name][name] = {
                    'address': address,
                    'value': response.registers[0],
                    'type': reg_type,
                    'unit': reg['unit']
                }
                print(f"  ✓ {name}: {response.registers[0]}")
    
    return results

# Usage
from pymodbus.client.sync import ModbusTcpClient

client = ModbusTcpClient('192.168.1.5', port=502)
client.connect()

data = read_all_registers(client)

client.close()

# Process results
for group, registers in data.items():
    print(f"\\n{group}:")
    for name, value in registers.items():
        print(f"  {name}: {value['value']} {value['unit']}")
    """)


def example_5_csv_export():
    """Example 5: Export mapping to CSV"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Export Mapping to CSV")
    print("="*70)
    
    register_map = load_register_map()
    
    # CSV header
    csv_lines = ["Address,Name,Type,Count,Group,Access,Description"]
    
    for group_name, registers in sorted(register_map['groups'].items()):
        for reg in sorted(registers, key=lambda r: r['address']):
            csv_lines.append(
                f"{reg['address']},"
                f"{reg['name']},"
                f"{reg['type']},"
                f"{reg['count']},"
                f"{group_name},"
                f"{reg['access']},"
                f"\"{reg['description']}\""
            )
    
    # Save CSV
    csv_content = "\n".join(csv_lines)
    with open("register_map.csv", "w") as f:
        f.write(csv_content)
    
    print("\nExported to register_map.csv:")
    print(csv_content[:500] + "...\n")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("PRACTICAL USAGE EXAMPLES - SUNGROW REGISTER MAP")
    print("="*70)
    
    try:
        example_1_access_by_group()
        example_2_find_register_by_address()
        example_3_build_modbus_query()
        example_4_monitoring_script()
        example_5_csv_export()
        
        print("\n" + "="*70)
        print("EXAMPLES COMPLETE")
        print("="*70)
        print("\nKey Takeaways:")
        print("  ✓ Load register map from JSON")
        print("  ✓ Access by group, address, or type")
        print("  ✓ Build Modbus queries from mapping")
        print("  ✓ Integrate into monitoring applications")
        print("  ✓ Export to other formats (CSV, etc.)")
        print("\nNext Step: Use with real Wireshark captures!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
