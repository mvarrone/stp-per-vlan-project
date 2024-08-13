import re
import time
from typing import List, Dict, Any

input_text_1 = """
VLAN0001
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            Cost        4
            Port        5 (GigabitEthernet1/0)
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
            Address     5042.7200.0d00
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
            Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Desg FWD 4         128.1    Shr 
Gi0/1               Desg FWD 4         128.2    Shr 
Gi0/2               Desg FWD 4         128.3    Shr 
Gi0/3               Desg FWD 4         128.4    Shr 
Gi1/0               Root FWD 4         128.5    Shr 
Gi1/1               Desg FWD 4         128.6    Shr 
Gi1/2               Desg FWD 4         128.7    Shr 
Gi1/3               Desg FWD 4         128.8    Shr

VLAN0099
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            Cost        12
            Port        5 (GigabitEthernet1/0)
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
            Address     5042.7200.0d00
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
            Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Desg FWD 4         128.1    Shr 
Gi0/1               Desg FWD 4         128.2    Shr 
Gi0/2               Desg FWD 4         128.3    Shr 
Gi0/3               Desg FWD 4         128.4    Shr 
Gi1/0               Root FWD 4         128.5    Shr 
Gi1/1               Desg FWD 4         128.6    Shr 
Gi1/2               Desg FWD 4         128.7    Shr 
Gi1/3               Desg FWD 4         128.8    Shr

VLAN0100
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            Cost        16
            Port        5 (GigabitEthernet1/0)
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
            Address     5042.7200.0d00
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
            Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Desg FWD 4         128.1    Shr 
Gi0/1               Desg FWD 4         128.2    Shr 
Gi0/2               Desg FWD 4         128.3    Shr 
Gi0/3               Desg FWD 4         128.4    Shr 
Gi1/0               Root FWD 4         128.5    Shr 
Gi1/1               Desg FWD 4         128.6    Shr 
Gi1/2               Desg FWD 4         128.7    Shr 
Gi1/3               Desg FWD 4         128.8    Shr
"""

input_text_2 = """
VLAN0001
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            This bridge is the root
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
            Address     5000.5800.0200
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
            Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type     
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Desg FWD 4         128.1    Shr      
Gi0/1               Desg FWD 4         128.2    Shr      
Gi0/2               Desg FWD 4         128.3    Shr      
Gi0/3               Desg FWD 4         128.4    Shr      
Gi1/0               Desg FWD 4         128.5    Shr      
Gi1/1               Desg FWD 4         128.6    Shr      
Gi1/2               Desg FWD 4         128.7    Shr      
Gi1/3               Desg FWD 4         128.8    Shr      

VLAN0100
Spanning tree enabled protocol rstp
Root ID     Priority    32769
            Address     5000.5800.0200
            Cost        16
            Port        5 (GigabitEthernet1/0)
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

Bridge ID   Priority    32769  (priority 32768 sys-id-ext 1)
            Address     5042.7200.0d00
            Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
            Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Gi0/0               Desg FWD 4         128.1    Shr 
Gi0/1               Desg FWD 4         128.2    Shr 
Gi0/2               Desg FWD 4         128.3    Shr 
Gi0/3               Desg FWD 4         128.4    Shr 
Gi1/0               Root FWD 4         128.5    Shr 
Gi1/1               Desg FWD 4         128.6    Shr 
Gi1/2               Desg FWD 4         128.7    Shr 
Gi1/3               Desg FWD 4         128.8    Shr
"""


def print_execution_time(end_total: float) -> None:
    # end_total = round(end_total, 2)

    if end_total > 1:
        unit = "s"
        print(f"\nTotal script execution time: {end_total} {unit}")
    else:
        unit = "ms"
        end_total *= 1000
        print(f"\nTotal script execution time: {end_total:.2f} {unit}")


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
                        "interface": interface_name,
                        "role": role_mapping.get(role, role),
                        "status": status_mapping.get(status, status),
                        "cost": int(interface_match.group(4)),
                        "priority": int(interface_match.group(5)),
                        "number": int(interface_match.group(6)),
                        "type": type_mapping.get(interface_type, interface_type),
                    }
                    current_vlan["interfaces"].append(interface)

    # Añadir la última VLAN procesada
    if current_vlan:
        parsed_stp_data.append(current_vlan)

    return parsed_stp_data


def format_stp_parsed_info(parsed_stp_data: List[Dict[str, Any]]) -> str:
    formatted_data = []
    for vlan_data in parsed_stp_data:
        formatted_data.append(f"\nVLAN{vlan_data['vlan_id_str']}")
        formatted_data.append(f"  vlan_id      {vlan_data['vlan_id']}")
        formatted_data.append(f"  vlan_id_str  {vlan_data['vlan_id_str']}")
        if "protocol" in vlan_data:
            formatted_data.append(f"  protocol     {vlan_data['protocol']}")
        for id_type in ["root_id", "bridge_id"]:
            if vlan_data[id_type]:
                formatted_data.append(f"  {id_type}")
                for key, value in vlan_data[id_type].items():
                    if key == "counters":
                        formatted_data.append("    counters")
                        for counter_key, counter_value in value.items():
                            formatted_data.append(
                                f"      {counter_key:<14} {counter_value}"
                            )
                    else:
                        formatted_data.append(f"    {key:<14} {value}")

        formatted_data.append("  interfaces")
        for interface in vlan_data["interfaces"]:
            formatted_data.append(f"    {interface['interface']}")
            for key, value in interface.items():
                if key != "interface":
                    formatted_data.append(f"      {key:<14} {value}")

    formatted_data = "\n".join(formatted_data)
    return formatted_data


def main() -> None:
    texts = [input_text_1]
    # texts = [input_text_2]
    # texts = [input_text_1, input_text_2]

    parsed_stp_data_list = []
    for i, raw_text in enumerate(texts, start=1):
        print(f"Processing input_text_{i}:")

        parsed_stp_data = parse_stp_data_per_vlan(raw_text)
        print("\nparsed_stp_data:\n\n", parsed_stp_data)
        parsed_stp_data_list.append(parsed_stp_data)

        formatted_data = format_stp_parsed_info(parsed_stp_data)
        print("\nformatted_data:\n", formatted_data)

        print(20 * "-")

    print(f"parsed_stp_data_list:\n\n{(parsed_stp_data_list)}")

    # Extraer los IDs de VLAN del primer conjunto de datos parseados
    vlans_found = [vlan["vlan_id_str"] for vlan in parsed_stp_data_list[0]]
    print(f"\nvlans_found: {vlans_found}")
    print(f"\nNumber of VLANs found: {len(vlans_found)}\n")

    print(20 * "*")
    # Extraer información para cada VLAN encontrada
    for vlan_id in vlans_found:
        vlan_info = next(
            (
                vlan
                for vlan in parsed_stp_data_list[0]
                if vlan["vlan_id_str"] == vlan_id
            ),
            None,
        )
        if vlan_info:
            print(f"\nInformation for VLAN {vlan_id}:")
            print(vlan_info)
        else:
            print(f"No information found for VLAN {vlan_id}")


if __name__ == "__main__":
    start_total = time.time()
    main()
    end_total = time.time() - start_total
    print_execution_time(end_total)
