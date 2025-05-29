# Parsing 'fosexec -fid all -cmd "switchshow"' Output in Python

To parse the output of the Brocade Fibre Channel switch command `fosexec -fid all -cmd "switchshow"`, you'll need to handle the structured output that shows switch information and port statuses. Here's a Python approach to parse this data:

## Sample Python Code

```python
import re
from collections import defaultdict

def parse_switchshow(output):
    """Parse the output of 'fosexec -fid all -cmd "switchshow"'"""
    
    switches = defaultdict(dict)
    current_switch = None
    
    for line in output.splitlines():
        # Detect switch header line (e.g., "FID:128; Switch Name:switch_name; ...")
        switch_header = re.match(r'FID:(\d+);\s+Switch Name:([^;]+);', line)
        if switch_header:
            fid = switch_header.group(1)
            switch_name = switch_header.group(2)
            current_switch = f"FID{fid}_{switch_name}"
            switches[current_switch]['info'] = line.strip()
            switches[current_switch]['ports'] = []
            continue
            
        # Parse port information (e.g., " 0   0   id   N4   No_Light    ...")
        port_line = re.match(r'\s*(\d+)\s+(\d+)\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)', line)
        if port_line and current_switch:
            port_data = {
                'port': port_line.group(1),
                'slot': port_line.group(2),
                'port_type': port_line.group(3),
                'state': port_line.group(4),
                'phys_state': port_line.group(5),
                'speed': port_line.group(7),
                'remote_switch': port_line.group(8)
            }
            switches[current_switch]['ports'].append(port_data)
            
    return switches

# Example usage:
if __name__ == "__main__":
    # This would be the output from your command
    sample_output = """
FID:128; Switch Name:switch1; ...
 0   0   id   N4   No_Light    fc   auto    switch2[10]
 1   0   id   N4   Online      fc   16G     switch3[5]
FID:129; Switch Name:switch2; ...
 0   0   id   N4   No_Light    fc   auto    -
    """
    
    parsed = parse_switchshow(sample_output)
    
    # Print parsed data
    for switch, data in parsed.items():
        print(f"\nSwitch: {switch}")
        print(f"Info: {data['info']}")
        print("Ports:")
        for port in data['ports']:
            print(f"  Port {port['port']}: {port['state']} ({port['speed']}) to {port['remote_switch']}")
```

## Key Components

1. **Switch Detection**: Identifies each switch section by the FID and switch name
2. **Port Parsing**: Extracts port information including:
   - Port number
   - Slot number
   - Port type
   - Operational state
   - Physical state
   - Speed
   - Connected device

## Enhancement Options

1. **Add more fields**: Extract additional information from the port lines as needed
2. **Error handling**: Add validation for malformed lines
3. **Output formatting**: Convert to JSON, CSV, or other formats
4. **Filtering**: Add functions to filter by port state or other criteria

## Running with Actual Command Output

To use this with real command output:

```python
import subprocess

# Run the command and capture output
output = subprocess.check_output(['fosexec', '-fid', 'all', '-cmd', 'switchshow'], 
                               universal_newlines=True)

# Parse the output
parsed_data = parse_switchshow(output)
```

Would you like me to modify any part of this parser to better match your specific switchshow output format?
