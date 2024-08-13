# Backend

This project is designed to connect to network devices using SSHv2, gather information about Spanning Tree Protocol (STP) and Cisco Discovery Protocol (CDP), and process the gathered data. The implementation is done using Python and the Netmiko library for handling SSH connections.

## Implementation

### 0. Preconfiguration
Ensure the following preconfigurations are completed:

* Each device should be configured with SSHv2 and CDP enabled.
* The file device_credentials.json must be filled with the appropriate parameters for each device. This file is a list of dictionaries and the structure of this file should be as follows:

    ```python
    [
        
        {
            "host": "device_ip_or_hostname",
            "port": 22,
            "username": "your_username",
            "password": "your_password",
            "secret": "enable_password"
            "device_type": "cisco_ios",
            "spanning_tree_command": "show spanning-tree",
            "cdp_neighbors_command": "show cdp neighbors"
        },
        ...
    ]
    ```
    > port: refers to the SSH port number used to connect to the device

    > secret: refers to the password needed, in some vendors like *Cisco*, to enter privileged EXEC mode
    
    > device_type: refers to the platform of the device

### 1. Load credentials

Load each device's credentials from the device_credentials.json file and store them in a variable called *devices*. 
After that, this variable will be modified by eliminating 2 specific keys (spanning_tree_command and cdp_neighbors_command) with their respectives values for each device. This new variable will be called *netmiko_device* and that is the one that will be used by Netmiko to connect to each device via SSHv2.

### 2. Establish connection to each device

The script connects to each device concurrently using Python's ThreadPoolExecutor and Netmiko. It gathers STP and CDP data. The gathered data is then parsed for easier consumption by using TextFSM.

### 3. Count and Display Connection Results
After attempting to connect to all devices, the script counts and displays the number of successful and failed connections, along with detailed failure reasons.

## Running the Script

Ensure all devices are preconfigured and the *device_credentials.json* file is correctly filled.

Run the script using Python 3:
```python
py main.py
```

## Requirements

* Spanning Tree Protocol (STP) and Cisco Discovery Protocol (CDP) are needed for getting all the data needed to finally represent a spanning tree dynamically in this project
* Dependencies:
    - Netmiko
    - Python 3 (Python 3.12.2)
    
Install dependencies by using:
```python
pip install -r requirements.txt
```

## Current limitations of the project

Currently, this project includes only Cisco devices. That is why CDP is being used right now: It is planned to support Link-Layer Discovery Protocol (LLDP) as well in the future in order to include more vendors and not only Cisco

## Notes

* Make sure to handle your credentials securely.
* Adjust the *max_workers* parameter in the *ThreadPoolExecutor* to match the number of devices you are connecting to and the capabilities of your system.
* The script currently handles common exceptions such as authentication failure and timeout. 
* Modify the exception handling as needed for your specific use case.

This README should help anyone understand the purpose, configuration, and usage of the app

## Output folder

Folder containing output files for executions of *./backend/main.py* file 

### PowerShell

```python
py .\main.py > ".\output\output_$(Get-Date -Format 'ddMMMyyyy_HHmmss').txt"
```

### NTC Templates folder

D:\Program Files\Python312\Lib\site-packages\ntc_templates\templates
D:\Program Files\Python312\Lib\site-packages\ntc_templates\templates\index

## About the level value for each device

We assign a value of 9999 to each device in the results dictionary.
It will be updated in the process_nodes function later
It indicates that the key level has not been determined yet
How it works:
1. All devices start having a value of 9999
2. When root bridge is found, device gets an updated value of 0 for key level
3. When root bridge neighbor(s) is/are found, that/those device(s) will updated to a value of 1 for key level
4. Finally, every device is going to be updated to a value of 2, 3, 4,...etc