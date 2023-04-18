import concurrent.futures
import csv
from netmiko import ConnectHandler

#Sites config
caba_config = {
    'radius_servers': [
        {
            'name': 'angola_publisher_virtual',
            'ip': '146.42.34.73',
            'auth_port': '1812',
            'acct_port': '1813',
            'key': '10631A3B2B37003E0E247372'
        },
        {
            'name': 'angola_subscriber_virtual',
            'ip': '146.42.69.72',
            'auth_port': '1812',
            'acct_port': '1813',
            'key': '0526152D0F6C5C3C1B254E4B'
        }
    ]
}

lua_config = {
    'radius_servers': [
        {
            'name': 'angola_publisher_virtual',
            'ip': '146.42.34.73',
            'auth_port': '1812',
            'acct_port': '1813',
            'key': '09615D2B37250527092C5D73'
        },
        {
            'name': 'angola_subscriber_virtual',
            'ip': '146.42.69.72',
            'auth_port': '1812',
            'acct_port': '1813',
            'key': '0722326E60290B3015325255'
        }
    ]
}

sites_config = {
    'CABA': caba_config,
    'LUA': lua_config
}

def configure_device(device):
    # Connect to device
    net_connect = ConnectHandler(
        device_type='cisco_ios',
        ip=device['IP Address'],
        username='cisco',
        password='cisco'
    )

    # Check if AAA servers are up
    output = net_connect.send_command('show aaa servers')
    #if 'Total dead time: 0 sec' not in output:
    if 'Dead: total time 0s' not in output:
        print(f"WARNING: AAA servers on {device['Device Name']} ({device['IP Address']}) are not up")

    # Apply site-specific configuration
    site_config = sites_config.get(device['site'])
    if site_config:
        for server in site_config['radius_servers']:
            commands = [
                'aaa new',
                f"radius server {server['name']}",
                f"address ipv4 {server['ip']} auth-port {server['auth_port']} acct-port {server['acct_port']}",
                f"key 7 {server['key']}"
            ]
            output = net_connect.send_config_set(commands)
            print(output)
        
        commands = [
            'aaa group server radius AAA',
            f"no server name {site_config['radius_servers'][0]['name']}",
            f"no server name {site_config['radius_servers'][1]['name']}",
            f"server name {site_config['radius_servers'][0]['name']}",
            f"server name {site_config['radius_servers'][1]['name']}"
        ]
        output = net_connect.send_config_set(commands)
        print(output)

    # Disconnect from device
    net_connect.disconnect()

# Read devices from CSV file
with open('devices.csv') as file:
    reader = csv.DictReader(file)
    devices = [row for row in reader]

# Execute configure_device function for each device in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    results = [executor.submit(configure_device, device) for device in devices]
    concurrent.futures.wait(results)
