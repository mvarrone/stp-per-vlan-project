import json
import time
import telnetlib3
import asyncio

template = """
enable
configure terminal
hostname {hostname}
enable secret {enable_password}
username {username} secret {normal_password}
interface vlan 1
ip address {SVI_ip_address} {SVI_mask}
no shutdown
exit
ip default-gateway {default_gateway_ip}
line console 0
login local
exit
ip domain name {domain_name}
crypto key generate rsa modulus 2048
line vty 0 4
login local
transport input ssh
end
wr
exit
"""


def print_execution_time(end_total) -> None:
    if end_total > 1:
        print(f"Total script execution time: {end_total:.2f} s")
    else:
        end_total *= 1000
        print(f"Total script execution time: {end_total:.2f} ms")


def print_stats(devices, counters) -> None:
    total_devices = len(devices)

    good_connections = counters.get("good_connections")
    bad_connections = counters.get("bad_connections")

    good_connections_percentaje = round(100 * good_connections / total_devices, 2)
    bad_connections_percentaje = round(100 * bad_connections / total_devices, 2)
    print(
        f"\nGood connections: {good_connections}/{total_devices} - {good_connections_percentaje} %"
    )
    print(
        f"Bad connections: {bad_connections}/{total_devices} - {bad_connections_percentaje} %"
    )


async def configure_switch(host, port, commands, counters):
    writer = None
    try:
        print(f"Connecting to {host}:{port}...")
        _, writer = await telnetlib3.open_connection(host, port)
        print(f"Connected to {host}:{port}")

        # Send each command to the switch
        for line in commands.strip().splitlines():
            if line.strip():  # Ensure non-empty lines only
                command = line.strip() + "\n"
                # print(f"Sending command: {command}")
                writer.write(command)  # Encode command properly

        # Close the telnet connection
        await writer.drain()
        print(f"Closed connection to {host}:{port}")
        counters["good_connections"] += 1
    except Exception as e:
        print(f"Error configuring {host}:{port} - {e}")
        counters["bad_connections"] += 1
    finally:
        if writer is not None:
            writer.close()


async def main():
    # Define the JSON file with credentials
    CREDENTIALS_FILE = "./credentials.json"

    # Define server ip address
    SERVER_IP_ADDRESS = "192.168.150.129"

    # Define counters for connection results
    counters = {"good_connections": 0, "bad_connections": 0}

    # Read credentials
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            devices = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {CREDENTIALS_FILE} was not found")
        return

    tasks = []

    # Iterate over each device in the list
    for device in devices:
        # Create the command string from the template and parameters
        commands = template.format(
            hostname=device.get("hostname"),
            enable_password=device.get("enable_password"),
            username=device.get("username"),
            normal_password=device.get("normal_password"),
            SVI_ip_address=device.get("SVI_ip_address"),
            SVI_mask=device.get("SVI_mask"),
            default_gateway_ip=device.get("default_gateway_ip"),
            domain_name=device.get("domain_name"),
        )

        # Configure the switch
        port = device.get("port")
        tasks.append(configure_switch(SERVER_IP_ADDRESS, port, commands, counters))

        print(
            f"Started task for {device.get('hostname')} - SVI: {device.get('SVI_ip_address')}"
        )

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

    print_stats(devices, counters)


if __name__ == "__main__":
    start_total = time.time()
    asyncio.run(main())
    end_total = time.time() - start_total

    print_execution_time(end_total)
