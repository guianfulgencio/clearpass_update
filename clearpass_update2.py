import csv
from netmiko import ConnectHandler

# Define the credentials and device types
username = "admin"
password = "secret"
access_switches = ["WS-C2960X", "WS-C3560X", "WS-C3650", "WS-C3850"]

# Read the list of devices from the CSV file
with open("devices.csv") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Check if the device is an access switch
        device_type = row["device_type"]
        if device_type not in access_switches:
            continue

        # Connect to the device using Netmiko
        device = {
            "device_type": "cisco_ios",
            "ip": row["ip_address"],
            "username": username,
            "password": password,
        }
        connection = ConnectHandler(**device)

        # Determine the source interface of the switch
        output = connection.send_command("show ip interface brief")
        for line in output.splitlines():
            fields = line.split()
            if fields[0] == "Vlan50":
                source_interface = "Vlan50"
                break
            elif "mgmt" in fields[0]:
                source_interface = fields[0]
                break

        # Configure the RADIUS servers and source interface
        commands = [
            "radius-server dead-criteria time 5 tries 3",
            "radius-server timeout 60",
            "radius-server deadtime 15",
            "aaa group server radius AAA",
            "server name LAG_RadiusVIP",
            "server name GBA_RadiusVIP",
            "server name WAR_RadiusVIP",
            f"ip radius source-interface {source_interface}",
        ]
        output = connection.send_config_set(commands)
        print(output)

        # Disconnect from the device
        connection.disconnect()
