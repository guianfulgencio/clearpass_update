import csv
from netmiko import ConnectHandler

# Open CSV file containing list of devices
with open('devices.csv', 'r') as file:
    reader = csv.DictReader(file)
    # Loop through each row in the CSV file
    for row in reader:
        # Check if the device type is supported
        if row['device_type'] == 'cisco_ios' or row['device_type'] == 'cisco_xe':
            # Define the device parameters
            device_params = {
                'device_type': row['device_type'],
                'ip': row['ip'],
                'username': 'cisco',
                'password': 'cisco'
            }
            # Connect to the device
            with ConnectHandler(**device_params) as device:
                # Determine the source-interface
                intf_output = device.send_command('show ip interface brief | include up.*up|Vlan|Gig|Eth')
                intf_lines = intf_output.splitlines()
                for line in intf_lines:
                    if 'Vlan' in line or 'Gig' in line or 'Eth' in line:
                        intf_name = line.split()[0]
                        break
                # Configure the radius settings and source-interface
                radius_commands = [
                    'radius-server dead-criteria time 5 tries 3',
                    'radius-server timeout 60',
                    'radius-server deadtime 15',
                    'aaa group server radius AAA',
                    'server name LAG_RadiusVIP',
                    'server name GBA_RadiusVIP',
                    'server name WAR_RadiusVIP',
                    f'ip radius source-interface {intf_name}',
                ]
                device.send_config_set(radius_commands)
                print(f"Configuration applied to {device_params['ip']}")
        else:
            print(f"{row['device_type']} not supported for {row['ip']}")
