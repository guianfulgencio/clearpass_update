import csv
from netmiko import ConnectHandler

# Define the list of keywords to search for in the "show version" output
# to identify if a device is a Cisco access switch
switch_keywords = ["WS-C2960X", "WS-C3560X", "WS-C3650", "WS-C3850", "WS-C3950", "IOSv"]

# Open the CSV file containing device names and IP addresses
with open('devices.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Create a new CSV file to write the report
    with open('report.csv', 'w', newline='') as reportfile:
        writer = csv.writer(reportfile)
        writer.writerow(['Device Name', 'IP Address', 'Management Interface'])
        
        # Iterate over each device in the CSV file
        for row in reader:
            device_name = row['Device Name']
            ip_address = row['IP Address']
            
            # Create a Netmiko connection to the device
            device = {
                'device_type': 'cisco_ios',
                'ip': ip_address,
                'username': 'cisco',
                'password': 'cisco'
            }
            try:
                net_connect = ConnectHandler(**device)
            except Exception as e:
                print(f"Error connecting to {device_name} ({ip_address}): {e}")
                continue
            
            # Run the "show version" command to check if the device is a Cisco access switch
            output = net_connect.send_command("show version")
            is_switch = False
            for keyword in switch_keywords:
                if keyword in output:
                    is_switch = True
                    break
            
            if is_switch:
                # If the device is a Cisco access switch, identify the management interface
                #output = net_connect.send_command("show ip interface brief | include ^Vlan|^Mgmt|^Loop")
                output = net_connect.send_command("show ip int brief | ex down|unassigned | inc Vlan")
                lines = output.splitlines()
                if len(lines) >= 2:
                    management_interface = lines[1].split()[0]
                else:
                    management_interface = 'unknown'
                    
                # Write the device name, IP address, and management interface to the report CSV file
                writer.writerow([device_name, ip_address, management_interface])
                
            net_connect.disconnect()
