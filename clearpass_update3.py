import csv
import re
from netmiko import ConnectHandler

# Define device connection settings
device_type = "cisco_ios"
username = "cisco"
password = "cisco"

# Define RADIUS servers and IP radius source interface
radius_servers = [
    {"name": "LAG_RadiusVIP", "address": "146.42.253.49"},
    {"name": "GBA_RadiusVIP", "address": "146.42.250.28"},
    {"name": "WAR_RadiusVIP", "address": "146.42.159.20"}
]
ip_radius_source_interface = "Vlan50"

# Define device_type pattern to extract device model
device_type_pattern = re.compile(r'^\S+\s+\S+\s+(\S+)\s')

# Define function to apply commands to device
def apply_commands_to_device(device):
    try:
        # Connect to device
        with ConnectHandler(
            device_type=device_type,
            host=device["ip"],
            username=username,
            password=password,
            secret=secret,
        ) as conn:
            # Determine device model
            output = conn.send_command("show version")
            device_model = device_type_pattern.search(output).group(1)

            # Determine management interface or VLAN
            if device_model.startswith("WS-C"):
                # For Catalyst switches
                output = conn.send_command("show ip interface brief | include up")
                management_interface = output.split()[0]
            elif device_model.startswith("ISR"):
                # For ISR routers
                output = conn.send_command("show ip interface brief | include up")
                management_interface = output.split()[0]
            else:
                # For other devices, assume VLAN 1
                management_interface = "Vlan1"

            # Configure RADIUS servers and IP radius source interface
            commands = [
                "radius-server dead-criteria time 5 tries 3",
                "radius-server timeout 60",
                "radius-server deadtime 15",
                "aaa group server radius AAA",
            ]
            for server in radius_servers:
                commands.append(f"server name {server['name']}\naddress ipv4 {server['address']} auth-port 1812 acct-port 1813 key")
            commands.append(f"ip radius source-interface {management_interface}")

            # Apply commands to device
            output = conn.send_config_set(commands)

            # Print output
            print(f"Successfully applied commands to {device['hostname']}")
            print(output)
            
            # Authentication test
            output = conn.send_command("show aaa servers radius")
            if "dead" in output:
                print("One or more RADIUS servers are dead or unresponsive.")
            else:
                print("RADIUS servers are all alive and responsive.")
                
    except Exception as e:
        # Print error message if unable to connect or apply commands
        print(f"Unable to apply commands to {device['hostname']}: {str(e)}")

# Read devices from CSV file
with open("devices.csv") as f:
    devices = list(csv.DictReader(f))

# Apply commands to each device
for device in devices:
    if device["device_type"] == "switch":
        apply_commands_to_device(device)
