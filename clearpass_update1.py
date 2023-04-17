from netmiko import ConnectHandler
import re

# Define the device types that are considered access switches
access_switch_types = ['cisco_ios']

# Define the regex pattern to match the device type
device_type_pattern = re.compile(r'^\S+\s+\S+\s+(\S+)\s')

# Define the regex pattern to match the source interface
source_interface_pattern = re.compile(r'^ip\s+radius\s+source-interface\s+(\S+)')

# Define the commands to be applied to the access switches
commands = [
    'show run | inc radius'
]

# Define the function to apply the commands to the switches
def configure_switch(switch_ip):
    # Define the device parameters
    device = {
        'device_type': 'cisco_ios',
        'ip': switch_ip,
        'username': 'cisco',
        'password': 'cisco'
    }

    # Create a new SSH connection
    with ConnectHandler(**device) as net_connect:
        # Send the command to show the device type
        device_type_output = net_connect.send_command('show version | include \^Cisco')

        # Check if the device is an access switch
        device_type_match = device_type_pattern.match(device_type_output)
        if device_type_match and device_type_match.group(1) in access_switch_types:
            # Send the commands to the switch
            for command in commands:
                net_connect.send_command(command)

            # Send the command to show the source interface
            source_interface_output = net_connect.send_command('show run | include ^ip radius source-interface')

            # Extract the source interface from the output
            source_interface_match = source_interface_pattern.match(source_interface_output)
            if source_interface_match:
                source_interface = source_interface_match.group(1)
                print(f'Successfully configured {switch_ip} with source interface {source_interface}')
            else:
                print(f'Error: Failed to extract source interface from {switch_ip}')
        else:
            print(f'Skipping {switch_ip} as it is not an access switch')

# Define the IP addresses of the switches to be configured
switch_ips = ['172.20.10.12']

# Apply the commands to each switch in the list
for switch_ip in switch_ips:
    configure_switch(switch_ip)
