import os
import re
import json

from datetime import datetime
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pprint import pprint
from typing import List, Dict, Any, Tuple, Union

from netmiko import (
    ConnectHandler,
    NetMikoAuthenticationException,
    NetMikoTimeoutException,
)
from netmiko.utilities import get_structured_data

def save_data_per_vlan(data_per_vlan) -> None:
    # Read and update the counter
    COUNTER_FILE = './graph/counter.txt'
    counter = read_counter(COUNTER_FILE)
    new_counter = counter + 1
    write_counter(new_counter, COUNTER_FILE)
    
    # Get the current date and time
    now = datetime.now()

    # Format the date and time as a string
    formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the directory path with the counter
    base_dir_path = f'./graph/saved_data/{counter:01d}-{formatted_now}/'

    # Ensure the base directory exists
    os.makedirs(base_dir_path, exist_ok=True)

    # Iterate through each item in the data_per_vlan list
    for vlan_data in data_per_vlan:
        vlan_id = vlan_data.get('vlan_id', 'unknown')
        
        # Create a subdirectory for each VLAN
        vlan_dir_path = os.path.join(base_dir_path, f'vlan_{vlan_id}')
        os.makedirs(vlan_dir_path, exist_ok=True)

        # Define the paths and corresponding data for each VLAN
        paths_and_data = {
            'nodes.json': vlan_data.get("nodes"),
            'edges.json': vlan_data.get("edges"),
            'edges_with_blocked_links.json': vlan_data.get("edges_with_blocked_links"),
            'blocked_interfaces.json': vlan_data.get("blocked_interfaces"),
            'results.json': vlan_data.get("results")
        }

        # Save data to the files for each VLAN
        for file_name, content in paths_and_data.items():
            if content is not None:
                file_path = os.path.join(vlan_dir_path, file_name)
                with open(file_path, 'w') as outfile:
                    json.dump(content, outfile, indent=2)

        # Save the entire VLAN data
        full_data_path = os.path.join(vlan_dir_path, 'full_vlan_data.json')
        with open(full_data_path, 'w') as outfile:
            json.dump(vlan_data, outfile, indent=2)

    # Save the entire data_per_vlan variable to data_per_vlan.json in base_dir_path
    data_per_vlan_path = os.path.join(base_dir_path, 'data_per_vlan.json')
    with open(data_per_vlan_path, 'w') as outfile:
        json.dump(data_per_vlan, outfile, indent=2)

    print(f"Data saved successfully in {base_dir_path}")

def read_counter(COUNTER_FILE) -> int:
    if not os.path.exists(COUNTER_FILE):
        return 1
    with open(COUNTER_FILE, 'r') as file:
        return int(file.read().strip())

def write_counter(counter, COUNTER_FILE) -> None:
    with open(COUNTER_FILE, 'w') as file:
        file.write(str(counter))

def save_data(data) -> None:
    # Read and update the counter
    COUNTER_FILE = './graph/counter.txt'
    counter = read_counter(COUNTER_FILE)
    new_counter = counter + 1
    write_counter(new_counter, COUNTER_FILE)
    
    # Get the current date and time
    now = datetime.now()

    # Format the date and time as a string
    formatted_now = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the directory path with the counter
    dir_path = f'./graph/saved_data/{counter:01d}-{formatted_now}/'

    # Ensure the directory exists
    os.makedirs(dir_path, exist_ok=True)

    # Define the paths and corresponding data
    paths_and_data = {
        'nodes.json': data.get("nodes"),
        'edges.json': data.get("edges"),
        'edges_with_blocked_links.json': data.get("edges_with_blocked_links"),
        'blocked_interfaces.json': data.get("blocked_interfaces")
    }

    # Save data to the files
    for file_name, content in paths_and_data.items():
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, 'w') as outfile:
            json.dump(content, outfile)

def set_options_to_blocked_edges(edges_finally_deleted, edges_without_duplicated_with_blocked_links):
    # Properties to add
    color_property = { 'color': 'red' }
    dashes_property = True
    smooth_property = { 'type': 'curvedCW', 'roundness': 0.55 }
    #label_property = 'X'

    # Convert the edges_finally_deleted to a set of tuples for easy lookup
    deleted_edges_set = {(edge['from'], edge['to']) for edge in edges_finally_deleted}

    # Update the edges in edges_without_duplicated_with_blocked_links if they are in edges_finally_deleted
    for edge in edges_without_duplicated_with_blocked_links:
        if (edge['from'], edge['to']) in deleted_edges_set:
            edge['color'] = color_property
            edge['dashes'] = dashes_property
            edge['smooth'] = smooth_property
            #edge['label'] = label_property

    edges_with_options = edges_without_duplicated_with_blocked_links

    return edges_with_options

def select_specific_data(results) -> List[Dict[str, Any]]:
    filtered_results = []

    for result in results:
        device = result.get('device')
        device_type = result.get('device_type')
        id = result.get('id')
        label = result.get('label')
        level = result.get('level')
        priority = result.get('priority')
        mac_address = result.get('mac_address')
        cost_to_root_bridge = result.get('cost_to_root_bridge')
        version = result.get('version')
        serial = result.get('serial')
        uptime = result.get('uptime')

        filtered_results.append({
            'device': device,
            'device_type': device_type,
            'id': id,
            'label': label,
            'level': level,
            'priority': priority,
            'mac_address': mac_address,
            'cost_to_root_bridge': cost_to_root_bridge,
            'version': version,
            'serial': serial,
            'uptime': uptime
        })

    return filtered_results

def print_updated_edge_information(edges_without_duplicated) -> None:
    #print(edges_without_duplicated)
    print("\nBetter way to show edges_without_duplicated:")
    for edge in edges_without_duplicated:
        print(edge)

def print_edges_with_options(edges_with_options) -> None:
    #print(edges_with_options)
    print("\nBetter way to show edges_with_options:")
    for edge in edges_with_options:
        print(edge)

def find_blocked_interfaces(results) -> List[Dict[str, Dict[str, List[str]]]]:
    # Here, we are implementing a list of blocked interfaces (blocked by STP protocol) for each device
    # In other words, each device has their own list of blocked interfaces
    # Of course, that list can contain one or more than one interface name
    # Note: That list can not contain 0 elements (can not be empty) because we are adding elements to the list
    # only for the cases where the role of that interface is equal to Alternate

    ## Output return example:
    ## List[Dict[str, Dict[str, List[str]]]]
    """" 
    [
        {
            "SW3": {
                "interfaces": [
                    "G 0/0",
                    "G 1/2"
                ]
            }
        },
        {
            "SW2": {
                "interfaces": [
                    "G 0/1"
                ]
            }
        },
        {
            "SW1": {
                "interfaces": [
                    "G 0/3"
                ]
            }
        }
    ]
    """

    blocked_interfaces = defaultdict(lambda: {"interfaces": []})
    
    for result in results:
        device_prompt = result.get('prompt')
        stp_output_parsed = result.get("stp_output_parsed", [])
        
        for stp_entry in stp_output_parsed:
            interfaces = stp_entry.get("interfaces", [])
            for interface in interfaces:
                role = interface.get("interface_role")
                if role == "Alternate":
                    interface_name = interface.get('interface_name')
                    blocked_interfaces[device_prompt]["interfaces"].append(interface_name)
    
    return [{k: v} for k, v in blocked_interfaces.items()]

def remove_blocked_links(edges_to_be_deleted: List[Dict[str, int]], edges_without_duplicated: List[Dict[str, int]]) -> List[Dict[str, int]]:
    m = len(edges_to_be_deleted)
    if m == 1:
        print("We found that 1 edge must be deleted and it is the following one:")
    else:
        print(f"We found that {m} edges must be deleted and those are:")
    
    print("edges_to_be_deleted: ", edges_to_be_deleted)

    print("\nBefore eliminating edge(s)")
    print(f"edges_without_duplicated: {len(edges_without_duplicated)} element(s)")
    print(edges_without_duplicated)

    def normalize_edge(edge: Dict[str, int]) -> Dict[str, int]:
        return {'from': edge['from'], 'to': edge['to']}

    counter_number_of_removed_edges = 0
    edges_finally_deleted = []
    for edge in edges_to_be_deleted:
        # Create the opposite edge dictionary
        opposite_edge = normalize_edge({'from': edge.get("to"), 'to': edge.get("from")})

        # Normalize and try to remove the original edge if it exists
        normalized_edges = [normalize_edge(e) for e in edges_without_duplicated]
        if normalize_edge(edge) in normalized_edges:
            to_delete = next(e for e in edges_without_duplicated if normalize_edge(e) == normalize_edge(edge))
            edges_without_duplicated.remove(to_delete)
            edges_finally_deleted.append(to_delete)
            counter_number_of_removed_edges = counter_number_of_removed_edges + 1

        # Normalize and try to remove the opposite edge if it exists
        if opposite_edge in normalized_edges:
            to_delete = next(e for e in edges_without_duplicated if normalize_edge(e) == opposite_edge)
            edges_without_duplicated.remove(to_delete)
            edges_finally_deleted.append(to_delete)
            counter_number_of_removed_edges = counter_number_of_removed_edges + 1

    print("\nAfter eliminating edge(s)")
    print(f"edges_without_duplicated: {len(edges_without_duplicated)} element(s)")
    print(edges_without_duplicated)
    print(f"\nAmount of removed edges: {counter_number_of_removed_edges}")
    print(f"\nedges_finally_deleted: {edges_finally_deleted}")
    return edges_without_duplicated, edges_finally_deleted


def identify_blocked_links(results: List[Dict[str, Any]]) -> List[Dict[str, int]]:
    edges_to_be_deleted = []

    for result in results:
        device_id = result.get("id")
        stp_output_parsed = result.get("stp_output_parsed", [])
        cdp_output = result.get("cdp_output_parsed", [])

        for stp_entry in stp_output_parsed:
            interfaces = stp_entry.get("interfaces", [])

            # Step 1: Identify interfaces with Role = Alternate
            altn_interfaces = [interface for interface in interfaces if interface.get("interface_role") == "Alternate"]

            for altn_interface in altn_interfaces:
                interface_name = altn_interface.get("interface_name")

                # Step 2: Find matching CDP entry
                matching_cdp_entry = next((entry for entry in cdp_output if entry.get("local_interface_name") == interface_name), None)

                if matching_cdp_entry:
                    neighbor_name = matching_cdp_entry.get("neighbor_name")

                    # Step 3: Find neighbor device ID
                    neighbor_device = next((dev for dev in results if dev.get("prompt") == neighbor_name), None)

                    if neighbor_device:
                        neighbor_id = neighbor_device.get("id")

                        # Step 4: Create edge dictionary
                        edge = {
                            "from": device_id,
                            "to": neighbor_id
                        }
                        edges_to_be_deleted.append(edge)

    return edges_to_be_deleted

def print_edge_information(edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names) -> None:
    #print(switches)
    print(f"\nBetter way to show switches:\nSwitch references")
    for switch in switches:
        print(switch)

    #print(edges)
    print("\nBetter way to show edges:")
    for edge in edges:
        print(edge)
        
    #print(edges_with_names)
    print("\nBetter way to show edges_with_names:")
    for edges_with_name in edges_with_names:
        print(edges_with_name)

    #print(edges_without_duplicated)
    print("\nBetter way to show edges_without_duplicated:")
    for edge_wo in edges_without_duplicated:
        print(edge_wo)

    #print(edges_without_duplicated_with_names)
    print("\nBetter way to show edges_without_duplicated_with_names:")
    for edge_wo_with_name in edges_without_duplicated_with_names:
        print(edge_wo_with_name)

def process_edges(results) -> List[Dict[str, Any]]:
    edges: List[Dict[str, int]] = []
    edges_with_names: List[Dict[str, str]] = []
    switches: List[Dict[str, Any]] = []
    edges_without_duplicated: List[Dict[str, int]] = []
    edges_without_duplicated_with_blocked_links: List[Dict[str, int]] = []
    edges_without_duplicated_with_names: List[Dict[str, str]] = []

    seen_edges = set()

    # Extracting edges from results
    for result in results:
        switch_name = result.get("prompt")
        switch_id = result.get("id")
        cdp_data = result.get("cdp_output_parsed")
        #print("cdp_data: ", cdp_data)

        switch = {'name': switch_name, 'id': switch_id}   
        switches.append(switch)

        for entry in cdp_data:
            neighbor_prompt = entry.get("neighbor_name")
            local_interface = entry.get("local_interface_name")
            neighbor_interface = entry.get("neighbor_interface_name")

            edge_with_name = {'from': switch_name, 'to': neighbor_prompt}
            edges_with_names.append(edge_with_name)

            neighbor_id = None
            # Find neighbor id based on neighbor prompt
            for neighbor_switch in results:
                if neighbor_switch.get("prompt") == neighbor_prompt:
                    neighbor_id = neighbor_switch.get("id")
                    break
            
            if neighbor_id is not None:
                # # Find role and status interface for local switch
                # for entry in results:
                #     if entry.get("prompt") == switch_name:
                #         for stp_data in entry.get("stp_output_parsed"):
                #             if stp_data.get("interface_name") == local_interface:
                #                 local_role = stp_data.get("interface_role")
                #                 local_status = stp_data.get("interface_status")
                #                 title = f"{switch_name}: {local_interface} {local_role} {local_status} <-> {neighbor_prompt}: {neighbor_interface}"

                # # Find role and status interface for neighbor switch
                # for entry in results:
                #     if entry.get("prompt") == neighbor_prompt:
                #         for stp_data in entry.get("stp_output_parsed"):
                #             if stp_data.get("interface_name") == neighbor_interface:
                #                 neighbor_role = stp_data.get("interface_role")
                #                 neighbor_status = stp_data.get("interface_status")
                #                 title = f"{switch_name}: {local_interface} {local_role} {local_status} <-> {neighbor_prompt}: {neighbor_interface} {neighbor_role} {neighbor_status}"

                title = f"{switch_name}: {local_interface}\n⇆\n{neighbor_prompt}: {neighbor_interface}"
                
                edge = {'from': switch_id, 'to': neighbor_id, "title": title}
                edges.append(edge)

                # Create a tuple for the edge to check for duplicates
                edge_tuple = tuple(sorted((switch_id, neighbor_id)))
                if edge_tuple not in seen_edges:
                    seen_edges.add(edge_tuple)
                    edge_wo = {'from': switch_id, 'to': neighbor_id, "title": title}
                    edges_without_duplicated.append(edge_wo)
                    edges_without_duplicated_with_blocked_links.append(edge_wo)

                    edges_without_duplicated_with_names.append({'from': switch_name, 'to': neighbor_prompt})


    return edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names, edges_without_duplicated_with_blocked_links

def print_node_information(nodes) -> None:
    #print(nodes)
    print("\nBetter way to show nodes:")
    for node in nodes:
        print(node)

def update_node_title_with_level_info(nodes) -> List[Dict[str, Any]]:
    for node in nodes:
        level = node.get("level")        
        priority = node.get("priority")        
        mac_address = node.get("mac_address")       
        cost_to_root_bridge = node.get("cost_to_root_bridge")       

        title = node.get("title")  
        node["title"] = title + f"\nLevel: {level}\nPriority: {priority}\nMAC Address: {mac_address}\nCost to RB: {cost_to_root_bridge}"
    return nodes

def print_node_structure(nodes) -> None:
    # Sort nodes by key 'level'
    sorted_nodes = sorted(nodes, key = lambda x: x.get("level"))

    # Print the network tree structure
    print("\nOption 1: Network Tree Structure")
    print(32 * '-')
    # Option 1
    for sorted_node in sorted_nodes:
        indent = 2 * '-' * sorted_node.get("level")
        #print(f"{indent}{sorted_node.get("label")} - {sorted_node.get("title")}, Level: {sorted_node.get("level")}")
        print(f"{indent}{sorted_node.get("label")} - Level: {sorted_node.get("level")}")

    print("\nOption 2: Network Tree Structure")
    print(32 * '-')
    # Option 2
    for sorted_node in sorted_nodes:
        indent = 2 * ' ' * sorted_node.get("level")
        #print(f"({sorted_node.get("level")}) | {indent}{sorted_node.get("label")} - {sorted_node.get("title")}")
        print(f"({sorted_node.get("level")}) | {indent}{sorted_node.get("label")}")


def process_nodes(root_bridge_data, results) -> List[Dict[str, Any]]:
    # Level 0: Node for Root Bridge
    def calculate_node_for_level_0(root_bridge_data) -> List[Dict[str, Any]]:
        nodes = []
        node = {
            "id": root_bridge_data.get("id"),
            "label": root_bridge_data.get("label"),
            "level": root_bridge_data.get("level"),
            "title": root_bridge_data.get("title"),
            "priority": root_bridge_data.get("priority"),
            "mac_address": root_bridge_data.get("mac_address"),
            "cost_to_root_bridge": root_bridge_data.get("cost_to_root_bridge")
        }
        nodes.append(node)
        return nodes
    
    nodes = calculate_node_for_level_0(root_bridge_data)
    #print("\nLevel 0 - nodes:\n", nodes)

    # Once the root bridge node has been added, let's proceed with root bridge neighbors
    # Level 1: Nodes for Root Bridge neighbors
    def calculate_nodes_for_level_1(nodes, root_bridge_data, results) -> List[Dict[str, Any]]:
        root_bridge_neighbor_list = []
        root_bridge_neighbors = root_bridge_data.get("neighbors")

        for neighbor in root_bridge_neighbors:
            #neighbor_name = neighbor.get("neighbor_name").split(".")[0]
            neighbor_name = neighbor.get("neighbor_name")
            root_bridge_neighbor_list.append(neighbor_name)
        #print("\nroot_bridge_neighbor_list:\n", root_bridge_neighbor_list)
        
        for root_bridge_neighbor in root_bridge_neighbor_list:
            for result in results:
                if root_bridge_neighbor == result.get("prompt"):
                    node = {
                        "id": result.get("id"),
                        "label": result.get("label"),
                        "level": 1, # 1 because this node is a root bridge neighbor
                        "title": result.get("title"),
                        "priority": result.get("priority"),
                        "mac_address": result.get("mac_address"),
                        "cost_to_root_bridge": result.get("cost_to_root_bridge")
                    }
                    nodes.append(node)
                    result["level"] = 1 # Update results dictionary changing from 9999 to 1 for root bridge neighbors
        return nodes

    nodes = calculate_nodes_for_level_1(nodes, root_bridge_data, results)
    #print("\nLevel 1 - nodes:\n", nodes)

    # Level > 1: Remaining nodes
    #print("\nFunction: calculate_nodes_with_level_higher_than_1()")
    def calculate_nodes_with_level_higher_than_1(nodes) -> List[Dict[str, Any]]:
        current_level = max(node.get("level") for node in nodes)
        #print("\ncurrent_level:", current_level)

        nodes_to_analize = [
            node for node in nodes if node.get("level") == current_level
        ]

        #print(f"\nnodes to analize because we are in level {current_level}")
        #print("nodes to analize:", nodes_to_analize)

        neighbors_data = []
        for node in nodes_to_analize:
            node_name = node.get("label")
            #print("\nnode name to analize:", node_name)
            for result in results:
                if result.get("label") == node_name:
                    neighbors = result.get("cdp_output_parsed")
                    #print("\nneighbors:", neighbors)
                    for neighbor in neighbors:
                        #neighbor_name = neighbor.get("neighbor_name").split(".")[0]
                        neighbor_name = neighbor.get("neighbor_name")
                        #print("--", neighbor_name)
                        neighbors_data.append(neighbor_name)
        
        for neighbor in neighbors_data:
            #print("\nneighbor:", neighbor)
            for result in results:
                if result.get("label") == neighbor:
                    level_found = result.get("level")
                    #print("\nlevel_found:", level_found, "\n")
                    if level_found == 9999:
                        updated_level = current_level + 1
                        result["level"] = updated_level
                        #print(f"{neighbor}: Level changed from {level_found} to {updated_level}")
                        node = {
                            "id": result.get("id"),
                            "label": result.get("label"),
                            "level": updated_level,
                            "title": result.get("title"),
                            "priority": result.get("priority"),
                            "mac_address": result.get("mac_address"),
                            "cost_to_root_bridge": result.get("cost_to_root_bridge")
                        }
                        nodes.append(node)

        #print("\nresults:", results)
        #print("\nnodes:\n", nodes)
        return nodes
    
    for i in range(1, 10):
        #print(f"\nIteration {i = }")
        nodes = calculate_nodes_with_level_higher_than_1(nodes)
    return nodes

                            
def find_root_bridge(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    root_bridge_data: Dict[str, Any] = {
        "device": "",
        "device_type": "",
        "prompt": "",
        "level": "",
        "id": "",
        "label": "",
        "title": "",
        "neighbors": "",
        "priority": "",
        "mac_address": "",
        "cost_to_root_bridge": -1
    }

    CISCO_STP_RAW_OUTPUT_ROOT_BRIDGE_TEXT = "This bridge is the root"

    for result in results:
        if result.get("device_type") == "cisco_ios":
            if CISCO_STP_RAW_OUTPUT_ROOT_BRIDGE_TEXT in result.get("stp_output_raw"):
                root_bridge_data["device"] = result.get("device")
                root_bridge_data["device_type"] = result.get("device_type")
                root_bridge_data["prompt"] = result.get("prompt")
                root_bridge_data["level"] = 0 # 0 because this node is the root bridge and that is why it has level 0
                root_bridge_data["id"] = result.get("id")
                root_bridge_data["label"] = result.get("label")
                root_bridge_data["title"] = result.get("title")
                root_bridge_data["neighbors"] = result.get("cdp_output_parsed")
                root_bridge_data["priority"] = result.get("priority")
                root_bridge_data["mac_address"] = result.get("mac_address")
                root_bridge_data["cost_to_root_bridge"] = result.get("cost_to_root_bridge")

                result["level"] = 0 # Update results dictionary changing from 9999 to 0 for root bridge level value
                return root_bridge_data

    root_bridge_data = {}
    return root_bridge_data


def get_prompt(connection, device_type: str) -> str:
    if device_type == "cisco_ios":
        prompt = connection.find_prompt()
        # print(f"{prompt = }")
        if not prompt:
            return "prompt not found"

        if prompt[-1] == "#":
            prompt = prompt[:-1]

        # print(f"{prompt = }")
        return prompt

    prompt = connection.find_prompt()
    return prompt


def print_execution_time(end_total) -> Tuple[float, str]:
    end_total = round(end_total, 2)

    if end_total > 1:
        unit = "s"
        print(f"\nTotal script execution time: {end_total} {unit}")
    else:
        unit = "ms"
        end_total *= 1000
        print(f"\nTotal script execution time: {end_total} {unit}")
    
    return end_total, unit


def load_credentials(CREDENTIALS_FILE: str) -> List[Dict[str, Any]]:
    devices: List[Dict[str, Any]] = []
    try:
        with open(CREDENTIALS_FILE, "r") as file:
            devices = json.load(file)
    except FileNotFoundError:
        print(f"Error: File {CREDENTIALS_FILE} was not found")

        return devices
    
    return devices

def set_node_mac_address(device_type, stp_output_parsed_data) -> str:
    if device_type == "cisco_ios":
        for stp_data in stp_output_parsed_data:
            bridge_id = stp_data.get('bridge_id', {})
            mac_address = bridge_id.get('address')
            return mac_address
    return "N/A"

def set_node_priority(device_type, stp_output_parsed_data) -> int:
    if device_type == "cisco_ios":
        for stp_data in stp_output_parsed_data:
            bridge_id = stp_data.get('bridge_id', {})
            priority = bridge_id.get('priority')
            return priority
    return -1

def set_node_cost_to_root_bridge(device_type, stp_output_parsed_data) -> int:
    if device_type == "cisco_ios":
        for stp_data in stp_output_parsed_data:
            root_id = stp_data.get('root_id', {})
            cost_to_root_bridge = root_id.get('cost')
            return cost_to_root_bridge
    return -1

def obtain_some_values_from_version_command(parsed_version_output: List[Dict[str, str]], device_type: str) -> Tuple[str, str, str]:
    if device_type == "cisco_ios":
        # Initialize default values
        version = ''
        serial = ''
        uptime = ''
        
        # Process parsed_version_output
        for entry in parsed_version_output:
            if 'version' in entry:
                version = entry['version']
            if 'serial' in entry:
                serial = entry['serial']
            if 'uptime' in entry:
                uptime = entry['uptime']
        
        return version, serial, uptime
    return "N/A", "N/A", "N/A"

def modify_version_parsed_data(parsed_version_output, device_type: str) -> List[Dict[str, str]]:
    if device_type == "cisco_ios":
        for entry in parsed_version_output:
            if 'serial' in entry:
                entry['serial'] = entry['serial'][0]
        return parsed_version_output
    return parsed_version_output

# def modify_stp_parsed_data(parsed_stp_output, device_type) -> List[Dict[str, str]]:
#     if device_type == "cisco_ios":
#         for entry in parsed_stp_output:
#             if 'interface' in entry:
#                 entry['interface'] = entry['interface'].replace('Gi', 'G ')

#             if 'role' in entry:
#                 entry['role'] = entry['role'].replace('Desg', 'Designated')

#             if 'role' in entry:
#                 entry['role'] = entry['role'].replace('Altn', 'Alternate')

#             if 'status' in entry:
#                 entry['status'] = entry['status'].replace('FWD', 'Forwarding')

#             if 'status' in entry:
#                 entry['status'] = entry['status'].replace('BLK', 'Blocking')

#             if 'type' in entry:
#                 entry['type'] = entry['type'].replace('Shr ', 'Shr')

#         return parsed_stp_output
    
def parse_stp_data_per_vlan(raw_text: str) -> List[Dict[str, Any]]:
    parsed_stp_data = []
    current_vlan = None
    current_id = None
    interface_section = False

    role_mapping = {"Desg": "Designated", "Altn": "Alternate", "Root": "Root"}
    status_mapping = {"FWD": "Forwarding", "BLK": "Blocking"}
    interface_mapping = {"Gi": "G ", "Te": "T ", "Fa": "F "}
    type_mapping = {
        "Shr": "Shared",
        "P2p": "Point-to-point",
        "P2p Edge": "Point-to-point-edge",
    }

    lines = raw_text.split("\n")

    for line in lines:
        line = line.strip()

        vlan_match = re.match(r"VLAN(\d+)", line)
        if vlan_match:
            if current_vlan:
                parsed_stp_data.append(current_vlan)
            current_vlan = {
                "vlan_id": int(vlan_match.group(1)),
                "vlan_id_str": vlan_match.group(1),
                "protocol": "",
                "root_id": {},
                "bridge_id": {},
                "interfaces": [],
            }
            interface_section = False
            continue

        if current_vlan:
            protocol_match = re.search(r"Spanning tree enabled protocol (\S+)", line)
            if protocol_match:
                current_vlan["protocol"] = protocol_match.group(1)
                continue

            if line.startswith("Root ID") or line.startswith("Bridge ID"):
                current_id = "root_id" if line.startswith("Root ID") else "bridge_id"
                priority_match = re.search(r"Priority\s+(\d+)", line)
                if priority_match:
                    priority = int(priority_match.group(1))
                    current_vlan[current_id]["priority"] = priority
            elif line.startswith("Address"):
                address_match = re.search(r"Address\s+([0-9a-fA-F.]+)", line)
                if address_match:
                    current_vlan[current_id]["address"] = address_match.group(1)
            elif line.startswith("Cost"):
                cost_match = re.search(r"Cost\s+(\d+)", line)
                if cost_match:
                    cost = int(cost_match.group(1))
                    current_vlan[current_id]["cost"] = cost
            elif "This bridge is the root" in line:
                current_vlan[current_id]["cost"] = 0
            elif "Hello Time" in line:
                counters_match = re.search(
                    r"Hello Time\s+(\d+).*Max Age\s+(\d+).*Forward Delay\s+(\d+)", line
                )
                if counters_match:
                    current_vlan[current_id]["counters"] = {
                        "hello_time": int(counters_match.group(1)),
                        "max_age": int(counters_match.group(2)),
                        "forward_delay": int(counters_match.group(3)),
                    }
            elif line.startswith("Aging Time"):
                aging_time_match = re.search(r"Aging Time\s+(\d+)", line)
                if aging_time_match and current_id == "bridge_id":
                    if "counters" not in current_vlan[current_id]:
                        current_vlan[current_id]["counters"] = {}
                    current_vlan[current_id]["counters"]["aging_time"] = int(
                        aging_time_match.group(1)
                    )
            elif line.startswith("Interface"):
                interface_section = True
            elif interface_section and line:
                interface_match = re.match(
                    r"(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(\d+)\.(\d+)\s+(.+)", line
                )

                if interface_match:
                    role = interface_match.group(2)
                    status = interface_match.group(3)
                    interface_name = interface_match.group(1)
                    interface_type = interface_match.group(7).strip()

                    for prefix, replacement in interface_mapping.items():
                        if interface_name.startswith(prefix):
                            interface_name = replacement + interface_name[len(prefix) :]
                            break

                    interface = {
                        "interface_name": interface_name,
                        "interface_role": role_mapping.get(role, role),
                        "interface_status": status_mapping.get(status, status),
                        "interface_cost": int(interface_match.group(4)),
                        "interface_priority": int(interface_match.group(5)),
                        "interface_number": int(interface_match.group(6)),
                        "interface_type": type_mapping.get(interface_type, interface_type),
                    }
                    current_vlan["interfaces"].append(interface)

    # Añadir la última VLAN procesada
    if current_vlan:
        parsed_stp_data.append(current_vlan)

    return parsed_stp_data

def modify_cdp_parsed_data(parsed_cdp_output: List[Dict[str, Union[str, str]]], device_type: str) -> List[Dict[str, Union[str, int]]]:
    if device_type == "cisco_ios":
        for entry in parsed_cdp_output:
            if 'neighbor_name' in entry:
                entry['neighbor_name'] = entry['neighbor_name'].split('.')[0]

            if 'capability' in entry:
                entry['capability'] = entry['capability'].strip()

            if 'local_interface_name' in entry:
                entry['local_interface_name'] = entry['local_interface_name'].replace('Gig ', 'G ')
            
            if 'neighbor_interface_name' in entry:
                entry['neighbor_interface_name'] = entry['neighbor_interface_name'].replace('Gig ', 'G ') 

            if 'holdtime' in entry:
                entry['holdtime'] = int(entry['holdtime'])

        return parsed_cdp_output
    return parsed_cdp_output

def get_available_vlans(results: List[Dict[str, Any]]) -> List[int]:
    vlan_set = set()
    
    for result in results:
        stp_output_parsed = result.get('stp_output_parsed', [])
        for data in stp_output_parsed:
            vlan_id = data.get('vlan_id')
            if vlan_id is not None:
                vlan_set.add(vlan_id)
            
    return list(vlan_set)

def checks_all_prompts_are_different(results) -> bool:
    error_checking_prompts = False
    prompts_seen = set()
    duplicates = []

    for index, dictionary in enumerate(results):
        prompt = dictionary.get('prompt')
        if prompt:
            if prompt in prompts_seen:
                duplicates.append((index, prompt))
            else:
                prompts_seen.add(prompt)

    if duplicates:
        error_checking_prompts = True
        print("TEST: FAILED. Duplicated 'prompt' values have been found. Ending here")
        for result in results:
            prompt = result.get('prompt')
            print(f"Prompt: {prompt}")
    else:
        print("TEST: PASSED. All 'prompt' values are different")

    return error_checking_prompts

def connect_to_device(device: Dict[str, Any]) -> Dict[str, Any]:
    global connection_id

    result: Dict[str, Any] = {
        "device": device.get("host", ""),
        "port": device.get("port", ""),
        "device_type": device.get("device_type", ""),
        "prompt": "",
        "status": "success",
        "stp_output_raw": "",
        "stp_output_parsed": "",
        "cdp_output_raw": "",
        "cdp_output_parsed": "",
        "version_output_raw": "",
        "version_output_parsed": "",
        "version": "",
        "serial": "",
        "uptime": "",
        "id": "",
        "label": "",
        "title": "",
        "level": "",
        "priority": "",
        "mac_address": "",
        "cost_to_root_bridge": ""
    }

    # STP
    spanning_tree_command = device.get("spanning_tree_command", "show spanning-tree")
    stp_template_name = device.get("stp_template")

    # CDP
    cdp_neighbors_command = device.get("cdp_neighbors_command", "show cdp neighbors")
    cdp_template_name = device.get("cdp_template")

    # Version 
    version_command = device.get("version_command", "show version")
    version_template_name = device.get("version_template")

    # netmiko_device dictionary needs to have the correct arguments in order to use within ConnectHandler,
    # so to fix it we needed to eliminate some key: value pairs from device dictionary
    list_of_keys_to_delete = ["spanning_tree_command", "cdp_neighbors_command", "version_command", "stp_template", "cdp_template", "version_template"]
    netmiko_device = {
        k: v
        for k, v in device.items()
        if k not in list_of_keys_to_delete
    }

    try:
        with ConnectHandler(**netmiko_device) as connection:
            if "secret" in netmiko_device:
                connection.enable()  # Enter privileged EXEC mode

            device_type = netmiko_device.get("device_type")

            # Get prompt for each device
            result["prompt"] = get_prompt(connection, device_type)

            ## STP
            # 1. Get raw STP data
            result["stp_output_raw"] = connection.send_command(
                command_string=spanning_tree_command
            )

            # 2. Parse STP data
            stp_output_raw = result.get("stp_output_raw")

            if device_type == "cisco_ios":
                # Parse STP data with regex
                parsed_stp_output = parse_stp_data_per_vlan(stp_output_raw)
            else:
                # Parse STP data with textfsm
                parsed_stp_output = get_structured_data(
                    raw_output=stp_output_raw,
                    platform=connection.device_type,
                    command=spanning_tree_command,
                    template=f"my_own_ntc_templates/modified/{stp_template_name}"
                )
                # 3. Post processing for STP parsed data 
                #parsed_stp_output = modify_stp_parsed_data(parsed_stp_output, device_type)

            # 4. Assign post processed data to dictionary
            result["stp_output_parsed"] = parsed_stp_output

            ## CDP
            # 1. Get raw CDP data
            result["cdp_output_raw"] = connection.send_command(
                command_string=cdp_neighbors_command
            )

            # 2. Parse CDP data locally
            parsed_cdp_output = get_structured_data(
                raw_output=result.get("cdp_output_raw"),
                platform=connection.device_type,
                command=cdp_neighbors_command,
                template=f"my_own_ntc_templates/modified/{cdp_template_name}"
            )

            # 3. Post processing for CDP parsed data 
            parsed_cdp_output = modify_cdp_parsed_data(parsed_cdp_output, device_type)

            # 4. Assign post processed data to dictionary
            result["cdp_output_parsed"] = parsed_cdp_output

            ## Version
            # 1. Get raw version data
            result["version_output_raw"] = connection.send_command(
                command_string=version_command
            )

            # 2. Parse version data locally
            parsed_version_output = get_structured_data(
                raw_output=result.get("version_output_raw"),
                platform=connection.device_type,
                command=version_command,
                template=f"my_own_ntc_templates/modified/{version_template_name}"
            )

            # 3. Post processing for Version parsed data 
            parsed_version_output = modify_version_parsed_data(parsed_version_output, device_type)

            # 4. Assign post processed data to dictionary
            result["version_output_parsed"] = parsed_version_output

            # 5. Get values from version command
            version, serial, uptime = obtain_some_values_from_version_command(parsed_version_output, device_type)

            # 6. Set each value in results dictionary
            # version
            result["version"] = version

            # serial
            result["serial"] = serial

            # uptime
            result["uptime"] = uptime

            # 7. Set node MAC Address
            stp_output_parsed_data = result.get("stp_output_parsed")

            mac_address = set_node_mac_address(device_type, stp_output_parsed_data)
            result["mac_address"] = mac_address

            # 8. Set node priority
            priority = set_node_priority(device_type, stp_output_parsed_data)
            result["priority"] = priority

            # 9. Set node cost: This cost is the cost for the node in order to reach the Root Bridge
            cost_to_root_bridge = set_node_cost_to_root_bridge(device_type, stp_output_parsed_data)
            result["cost_to_root_bridge"] = cost_to_root_bridge

            ## Others
            # Assign ID to each device for being used in nodes later
            result["id"] = connection_id

            # Assign a label to each device for being used in nodes later
            # label is the exact info as prompt
            result["label"] = result.get("prompt")

            # Assign a title to each device for being used in nodes later
            result["title"] = f"SVI: {device.get("host")}\nPlatform: {device.get("device_type")}"
            
            # Assign a value of 9999 as a placeholder to each device. It will be updated in the process_nodes function later
            result["level"] = 9999

            # Increase connection_id
            connection_id += 1
    except NetMikoAuthenticationException:
        result["status"] = "authentication_failure"
    except NetMikoTimeoutException:
        result["status"] = "timeout"
    except Exception as e:
        result["status"] = f"other_failure:{str(e)}"
    return result


def main():
    global connection_id
    connection_id = 0

    # 1. Load credentials
    print("1. Load credentials")
    CREDENTIALS_FILE: str = "./device_credentials.json"
    devices: List[Dict[str, Any]] = load_credentials(CREDENTIALS_FILE)
    if not devices:
        data = {
            "nodes": [],
            "edges": [],
            "error": True,
            "error_description": f"File {CREDENTIALS_FILE} has not been found"
        }
        return data 

    total_devices: int = len(devices)
    if total_devices == 1:
        print(f"1 device found in {CREDENTIALS_FILE} file")
    else:
        print(f"{total_devices} devices found in {CREDENTIALS_FILE} file")

    # 2a. Connect to devices concurrently
    print("\n2a. Connect to devices concurrently")
    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=total_devices) as executor:
        future_to_device = {
            executor.submit(connect_to_device, device): device for device in devices
        }

        for future in as_completed(future_to_device):
            results.append(future.result())

    print("DEBUG:")
    for result in results:
        pprint(result)

    # 2b. Get available vlans
    print("\n2b. Get available vlans")
    vlans = get_available_vlans(results)
    print(vlans)

    # 3. Some checks before continuing
    print("\n3. Some checks before continuing")
    error_checking_prompts = checks_all_prompts_are_different(results)
    if error_checking_prompts:
        data = {
            "nodes": [],
            "edges": [],
            "error": True,
            "error_description": "There are switches with the same prompt"
        }
        return data

    # 4. Count successes and failures
    print("\n4. Count successes and failures")
    connection_counter: Counter = Counter()
    successful_connections: List[str] = []
    failed_connections: Dict[str, List[str]] = {
        "authentication_failure": [],
        "timeout": [],
        "other_failure": []
    }
    for result in results:
        status = result.get("status", "unknown")
        connection_counter[status] += 1
        device_info = f"{result['prompt']} - {result['device']}"
        if status == "success":
            successful_connections.append(device_info)
        else:
            failed_connections[status].append(device_info)
    print("Done")

    # 5. Print results
    print("\n5. Print results\n\nSummary of connections:")
    total_devices = len(devices)
    successful_count = connection_counter.get("success", 0)
    successful_percentage = 100 * successful_count / total_devices
    print(f"--Successful connections: {successful_count}/{total_devices} ({successful_percentage:.1f}%)")
    if successful_count > 0:
        for device in successful_connections:
            print(f"    {device}")

    failed_count = total_devices - successful_count
    failed_percentage = 100 * failed_count / total_devices
    print(f"--Failed connections: {failed_count}/{total_devices} ({failed_percentage:.1f}%)")

    all_statuses = {"authentication_failure", "timeout", "other_failure"}
    for status in sorted(all_statuses):
        count = connection_counter.get(status, 0)
        print(f"  --{status}: {count}/{total_devices}")
        if count > 0:
            for device in failed_connections[status]:
                print(f"      {device}")

    if not successful_count:
        print("\nNo successful connections were made. Ending here")
        data = {
            "nodes": [],
            "edges": [],
            "error": True,
            "error_description": f"ERROR: {failed_count}/{total_devices} devices failed when attempting to connect"
        }
        return data
    
    data_per_vlan = []
    for vlan_id in vlans:
        print(f"\n------ vlan_id: {vlan_id} ------")

        # 6. Find root bridge
        print("\n6. Find root bridge")
        root_bridge_data = find_root_bridge(results)
        if not root_bridge_data:
            print("\nNo root bridge found. Ending here")
            data = {
                "nodes": [],
                "edges": [],
                "error": True,
                "error_description": "No root bridge found"
            }
            return data 
        print(f"\nRoot bridge has been found:\n{root_bridge_data}")

        # 7. Build nodes
        print("\n7. Build nodes")
        nodes = process_nodes(root_bridge_data, results)
        print("Done")

        # 7a. Update each node title with level information
        print("\n7a. Update each node title with level information")
        nodes = update_node_title_with_level_info(nodes)
        print("Done")

        # 8. Print node information
        print("\n8. Print node information")
        print_node_information(nodes)

        # 9. Print node tree structure
        print("\n9. Print node tree structure")
        print_node_structure(nodes)

        # 10. Build edges
        print("\n10. Build edges")
        edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names, edges_without_duplicated_with_blocked_links = process_edges(results)
        print("Done")

        # 11. Print edge information
        print("\n11. Print edge information")
        print_edge_information(edges, edges_with_names, switches, edges_without_duplicated, edges_without_duplicated_with_names)

        # 12. Identify edges where exist blocked interfaces (Role = Alternate)
        print("\n12. Identify edges where exist blocked interfaces (Role = Alternate)")
        edges_to_be_deleted = identify_blocked_links(results)
        print("Edges identified:", edges_to_be_deleted)

        # 13. Remove edge(s)
        print("\n13. Remove edge(s)")
        edges_without_duplicated, edges_finally_deleted = remove_blocked_links(edges_to_be_deleted, edges_without_duplicated)
        
        # 14. Print updated edge information
        print("\n14. Print updated edge information")
        print_updated_edge_information(edges_without_duplicated)

        # 15. Select specific data to be sent
        print("\n15. Select specific data to be sent")
        filtered_results = select_specific_data(results)
        #print(filtered_results)
        print("Done")

        # 16. Set options to blocked edges
        print("\n16. Set options to blocked edges")
        edges_with_options = set_options_to_blocked_edges(edges_finally_deleted, edges_without_duplicated_with_blocked_links)
        print("Done")

        # 17. Print edges with options
        print("\n17. Print edges with options")
        print_edges_with_options(edges_with_options)

        # 18. Create a list of blocked interfaces for devices that have interfaces in an Alternate role
        print("\n18. Create a list of blocked interfaces for devices that have interfaces in an Alternate role")
        blocked_interfaces = find_blocked_interfaces(results)
        print(blocked_interfaces)

        # 19. Print final data
        print("\n19. Print final data\n") 
        data = {
            "nodes": nodes,
            "edges": edges_without_duplicated,
            "edges_with_blocked_links": edges_with_options,
            "blocked_interfaces": blocked_interfaces,
            "results": filtered_results,
            "error": False,
            "error_description": "",
            "vlan_id": vlan_id,
        }
        print(data)
        data_per_vlan.append(data)

        # # 20. Save data
        # print("\n20. Save final data")
        # save_data(data) 
        # print("Done")

    print("\ndata_per_vlan:\n", data_per_vlan)

    # 20. Save final data to be return
    print("\n20. Save final data to be return")
    save_data_per_vlan(data_per_vlan) 
    print("Done")

    return data_per_vlan
