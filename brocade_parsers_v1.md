# Parsing `switchShow` Output from Brocade FOS in Python

Here's a Python script to parse the `switchShow` command output from Brocade FOS switches, extracting switch name, role, domain, fabric name, and all port information:

```python
import re
from collections import defaultdict

def parse_switchshow(output):
    """Parse Brocade FOS switchShow output."""
    result = {
        'switch_info': {},
        'ports': []
    }
    
    # Parse switch information
    switch_info_pattern = re.compile(
        r'switchName:\s+(?P<switch_name>.+?)\s*$.*?'
        r'switchType:\s+(?P<switch_type>.+?)\s*$.*?'
        r'switchState:\s+(?P<switch_state>.+?)\s*$.*?'
        r'switchRole:\s+(?P<switch_role>.+?)\s*$.*?'
        r'switchDomain:\s+(?P<switch_domain>\d+)\s*$.*?'
        r'switchId:\s+(?P<switch_id>.+?)\s*$.*?'
        r'fabric\.name:\s+(?P<fabric_name>.+?)\s*$',
        re.MULTILINE | re.DOTALL
    )
    
    switch_info_match = switch_info_pattern.search(output)
    if switch_info_match:
        result['switch_info'] = switch_info_match.groupdict()
    
    # Parse port information
    port_section_start = output.find("================")
    if port_section_start == -1:
        return result
    
    port_lines = output[port_section_start:].split('\n')[2:]  # Skip header lines
    
    port_pattern = re.compile(
        r'^(?P<index>\d+)\s+'
        r'(?P<slot>\d+)\s+'
        r'(?P<port>\d+)\s+'
        r'(?P<type>\S+)\s+'
        r'(?P<media>\S+)\s+'
        r'(?P<speed>\S+)\s+'
        r'(?P<state>\S+)\s+'
        r'(?P<mode>\S+)\s+'
        r'(?P<wwn>\S+)\s*'
        r'(?P<comment>.*)?$'
    )
    
    for line in port_lines:
        line = line.strip()
        if not line:
            continue
        
        port_match = port_pattern.match(line)
        if port_match:
            port_info = port_match.groupdict()
            # Clean up the comment field
            if 'comment' in port_info and port_info['comment']:
                port_info['comment'] = port_info['comment'].strip('"')
            else:
                port_info['comment'] = ''
            result['ports'].append(port_info)
    
    return result

# Example usage
if __name__ == "__main__":
    # Example switchShow output (truncated for brevity)
    switchshow_output = """
switchName:     BROCADE_SWITCH_1
switchType:     100.00
switchState:    Online    
switchMode:     Native
switchRole:     Principal
switchDomain:   1
switchId:       fffc01
switchWwn:      10:00:00:05:33:86:7b:6f
zoning:         ON
switchBeacon:   OFF
fabric.name:    FABRIC_PROD

Index Slot Port Address Media Speed State     Proto
==================================================
  0    0   0   010000   id    N8   Online      FC  F-Port  50:00:09:72:00:11:9b:01
  1    0   1   010100   id    N8   Online      FC  F-Port  50:00:09:72:00:11:9b:02
  2    0   2   010200   id    N8   No_Light    FC
  3    0   3   010300   id    N8   Online      FC  F-Port  50:00:09:72:00:11:9b:03
  4    0   4   010400   id    N8   Online      FC  F-Port  50:00:09:72:00:11:9b:04
"""

    parsed_data = parse_switchshow(switchshow_output)
    
    print("Switch Information:")
    print(f"Name: {parsed_data['switch_info'].get('switch_name', 'N/A')}")
    print(f"Role: {parsed_data['switch_info'].get('switch_role', 'N/A')}")
    print(f"Domain: {parsed_data['switch_info'].get('switch_domain', 'N/A')}")
    print(f"Fabric Name: {parsed_data['switch_info'].get('fabric_name', 'N/A')}")
    
    print("\nPort Information:")
    for port in parsed_data['ports']:
        print(f"Port {port['port']} (Slot {port['slot']}):")
        print(f"  Type: {port['type']}, Media: {port['media']}, Speed: {port['speed']}")
        print(f"  State: {port['state']}, Mode: {port['mode']}")
        print(f"  WWN: {port['wwn']}")
        if port['comment']:
            print(f"  Comment: {port['comment']}")
        print()
```

## Features:

1. **Switch Information Extraction**:
   - Switch name
   - Switch role (Principal, Subordinate, etc.)
   - Switch domain ID
   - Fabric name
   - Other switch attributes (type, state, etc.)

2. **Port Information Extraction**:
   - Port index, slot, and number
   - Port type and media
   - Speed and state
   - Protocol mode (F-Port, E-Port, etc.)
   - WWN of connected device (if any)
   - Comments/aliases

3. **Robust Parsing**:
   - Handles multi-line output
   - Uses regular expressions for precise pattern matching
   - Gracefully handles missing or malformed data

## Usage:

1. Save the output of `switchShow` from your Brocade switch to a file or variable
2. Pass the output to the `parse_switchshow()` function
3. Access the structured data in the returned dictionary

## Output Format:

The function returns a dictionary with two main sections:
- `switch_info`: Dictionary containing all switch attributes
- `ports`: List of dictionaries, each representing a port with all its attributes

You can modify the script to suit your specific needs or integrate it with other tools for monitoring or reporting.





Here's a comprehensive Python script to parse various Brocade FOS commands, including `firmwareshow`, `lscfg`, `sensorshow`, `fabricshow`, `sfpshow`, `alishow`, `zoneshow`, and `islshow`:

```python
import re
from collections import defaultdict

def parse_firmwareshow(output):
    """Parse firmwareshow output"""
    result = {}
    pattern = re.compile(
        r'Firmware Version:\s+(?P<firmware_version>.+?)\s*$.*?'
        r'Fabric OS Version:\s+(?P<fabric_os_version>.+?)\s*$.*?'
        r'BootProm Version:\s+(?P<bootprom_version>.+?)\s*$',
        re.MULTILINE | re.DOTALL
    )
    match = pattern.search(output)
    if match:
        result = match.groupdict()
    return result

def parse_lscfg(output):
    """Parse lscfg --show -n output"""
    result = []
    pattern = re.compile(
        r'^\s*(?P<wwn>\S+)\s+'
        r'(?P<port>\d+)\s+'
        r'(?P<type>\S+)\s+'
        r'(?P<vendor>\S+)\s+'
        r'(?P<model>.+?)\s+'
        r'(?P<firmware>\S+)\s*$',
        re.MULTILINE
    )
    for match in pattern.finditer(output):
        result.append(match.groupdict())
    return result

def parse_sensorshow(output):
    """Parse sensorshow output"""
    result = {}
    sensor_pattern = re.compile(
        r'^\s*(?P<sensor>\S+)\s+'
        r'(?P<status>\S+)\s+'
        r'(?P<value>\d+)\s+'
        r'(?P<unit>\S+)\s+'
        r'(?P<lo_critical>\d+)\s+'
        r'(?P<lo_warning>\d+)\s+'
        r'(?P<hi_warning>\d+)\s+'
        r'(?P<hi_critical>\d+)\s*$',
        re.MULTILINE
    )
    for match in sensor_pattern.finditer(output):
        sensor = match.groupdict()
        result[sensor['sensor']] = sensor
    return result

def parse_fabricshow(output):
    """Parse fabricshow output"""
    result = []
    fabric_pattern = re.compile(
        r'^\s*(?P<switch_id>\d+)\s+'
        r'(?P<domain_id>\d+)\s+'
        r'(?P<state>\S+)\s+'
        r'(?P<health>\S+)\s+'
        r'(?P<wwn>\S+)\s+'
        r'(?P<name>.+?)\s*$',
        re.MULTILINE
    )
    for match in fabric_pattern.finditer(output):
        result.append(match.groupdict())
    return result

def parse_sfpshow_health(output):
    """Parse sfpshow -health output"""
    result = {}
    current_port = None
    port_pattern = re.compile(r'^Port\s+(?P<port>\d+)\s*$')
    param_pattern = re.compile(
        r'^\s*(?P<parameter>.+?):\s+'
        r'(?P<value>\S+)\s*'
        r'(?P<status>\(.*?\))?\s*$'
    )
    
    for line in output.split('\n'):
        port_match = port_pattern.match(line)
        if port_match:
            current_port = port_match.group('port')
            result[current_port] = {}
            continue
        
        if current_port:
            param_match = param_pattern.match(line)
            if param_match:
                param = param_match.groupdict()
                result[current_port][param['parameter'].strip()] = {
                    'value': param['value'],
                    'status': param['status'][1:-1] if param['status'] else None
                }
    return result

def parse_alishow(output):
    """Parse alishow output"""
    result = {}
    alias_pattern = re.compile(
        r'^\s*(?P<alias>\S+)\s+'
        r'(?P<wwn>\S+)\s*$',
        re.MULTILINE
    )
    for match in alias_pattern.finditer(output):
        alias = match.groupdict()
        result[alias['alias']] = alias['wwn']
    return result

def parse_zoneshow(output):
    """Parse zoneshow output"""
    result = {
        'defined_configuration': '',
        'effective_configuration': '',
        'zones': {}
    }
    
    current_zone = None
    current_type = None
    
    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('Defined configuration:'):
            current_type = 'defined_configuration'
            continue
        elif line.startswith('Effective configuration:'):
            current_type = 'effective_configuration'
            continue
        elif line.startswith('zone:'):
            current_zone = line.split()[1]
            result['zones'][current_zone] = []
            continue
        elif line.startswith('alias:'):
            continue  # Skip alias definitions
        
        if current_type in ['defined_configuration', 'effective_configuration']:
            result[current_type] += line + '\n'
        elif current_zone and line.startswith(' '):
            member = line.strip()
            if member:
                result['zones'][current_zone].append(member)
    
    return result

def parse_islshow(output):
    """Parse islshow output"""
    result = []
    isl_pattern = re.compile(
        r'^\s*(?P<src_port>\S+)\s+'
        r'(?P<src_wwn>\S+)\s+'
        r'(?P<dst_port>\S+)\s+'
        r'(?P<dst_wwn>\S+)\s+'
        r'(?P<speed>\S+)\s+'
        r'(?P<distance>\S+)\s+'
        r'(?P<status>\S+)\s*$',
        re.MULTILINE
    )
    for match in isl_pattern.finditer(output):
        result.append(match.groupdict())
    return result

# Example usage
if __name__ == "__main__":
    # Example commands output (truncated for brevity)
    firmwareshow_output = """
Firmware Version: 8.2.1c
Fabric OS Version: v8.2.1c
BootProm Version: 1.0.12
"""
    
    lscfg_output = """
50060B0000ABCDEF 0 N Port EMC      SYMMETRIX      5876
50060B0000FEDCBA 1 N Port HPE      XP24000        1088
"""
    
    sensorshow_output = """
PS1            OK       24 C       20        25        30        70
PS2            OK       26 C       20        25        30        70
Temp           OK       38 C       10        15        45        50
"""
    
    fabricshow_output = """
 1   1   Online   Healthy 10:00:00:05:1e:80:7e:00  SWITCH1
 2   2   Online   Healthy 10:00:00:05:1e:80:7e:01  SWITCH2
"""
    
    sfpshow_output = """
Port 1:
    Temperature: 42.5 C (OK)
    Voltage: 3.28 V (OK)
Port 2:
    Temperature: 41.3 C (OK)
    Voltage: 3.30 V (OK)
"""
    
    alishow_output = """
SERVER1    50:00:09:72:00:11:9b:01
STORAGE1   50:00:09:72:00:11:9b:02
"""
    
    zoneshow_output = """
Defined configuration:
 cfg: PROD_CFG
 zone: PROD_ZONE1
  50:00:09:72:00:11:9b:01
  50:00:09:72:00:11:9b:02

Effective configuration:
 cfg: PROD_CFG
 zone: PROD_ZONE1
  50:00:09:72:00:11:9b:01
  50:00:09:72:00:11:9b:02
"""
    
    islshow_output = """
0/1    10:00:00:05:1e:80:7e:00 0/1    10:00:00:05:1e:80:7e:01 16G    SHORT   UP
"""
    
    # Parse all commands
    print("=== FirmwareShow ===")
    print(parse_firmwareshow(firmwareshow_output))
    
    print("\n=== LsCfg ===")
    print(parse_lscfg(lscfg_output))
    
    print("\n=== SensorShow ===")
    print(parse_sensorshow(sensorshow_output))
    
    print("\n=== FabricShow ===")
    print(parse_fabricshow(fabricshow_output))
    
    print("\n=== SfpShow ===")
    print(parse_sfpshow_health(sfpshow_output))
    
    print("\n=== AliShow ===")
    print(parse_alishow(alishow_output))
    
    print("\n=== ZoneShow ===")
    print(parse_zoneshow(zoneshow_output))
    
    print("\n=== IslShow ===")
    print(parse_islshow(islshow_output))
```

## Command Parser Details:

1. **firmwareshow**:
   - Extracts firmware version, Fabric OS version, and BootProm version

2. **lscfg --show -n**:
   - Parses connected device information including WWN, port, type, vendor, model, and firmware

3. **sensorshow**:
   - Extracts sensor data (temperature, power supplies) with status and thresholds

4. **fabricshow**:
   - Parses fabric members including switch ID, domain ID, state, health, WWN, and name

5. **sfpshow -health**:
   - Extracts SFP health information per port including temperature, voltage, and status

6. **alishow**:
   - Parses alias definitions mapping aliases to WWNs

7. **zoneshow**:
   - Extracts both defined and effective zone configurations with zone members

8. **islshow**:
   - Parses ISL information including source/destination ports and WWNs, speed, distance, and status

Each parser handles the specific format of its command and returns structured data that can be easily processed or stored. The parsers are designed to be robust against variations in output formatting.
