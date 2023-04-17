import csv
from netmiko import ConnectHandler
from getpass import getpass

# Prompt user for credentials
username = input("Enter your SSH username: ")
password = getpass("Enter your SSH password: ")

# Open the CSV file containing the devices
with open('devices.csv', 'r') as file:
    reader = csv.DictReader(file)

    # Iterate over each device in the CSV file
    for device in reader:
        print(f"Configuring device {device['hostname']}...")

        # Connect to the device using Netmiko
        net_connect = ConnectHandler(
            device_type=device['device_type'],
            ip=device['ip_address'],
            username=username,
            password=password,
        )

        # Determine the management interface
        output = net_connect.send_command('show ip interface brief')
        for line in output.split('\n'):
            if 'mgmt' in line.lower() or 'management' in line.lower():
                management_interface = line.split()[0]
                break
        else:
            management_interface = 'Vlan1'
        print(f"Using {management_interface} as the management interface")

        # Apply the command
        config_commands = [
            'aaa group server radius AAA',
            'server name LAG_RadiusVIP',
            'server name GBA_RadiusVIP',
            'server name WAR_RadiusVIP',
            f'ip radius source-interface {management_interface}',
            f'radius-server host {LAG_RadiusVIP} auth-port 1812 acct-port 1813 key',
            f'radius-server host {GBA_RadiusVIP} auth-port 1812 acct-port 1813 key',
            f'radius-server host {WAR_RadiusVIP} auth-port 1812 acct-port 1813 key',
            'radius-server dead-criteria time 5 tries 3',
            'radius-server timeout 60',
            'radius-server deadtime 15',
        ]
        output = net_connect.send_config_set(config_commands)
        print(output)

        # Test the authentication
        output = net_connect.send_command('test aaa group radius AAA test-user password radius123')
        if 'successful' in output.lower():
            print('Authentication test successful')
        else:
            print('Authentication test failed')

        # Disconnect from the device
        net_connect.disconnect()

print("Configuration complete")
