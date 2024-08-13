import re
import time
from typing import Dict, Any

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


def parse_stp_data_per_vlan(raw_text: str) -> Dict[str, Dict[str, Any]]:
    parsed_stp_data = {}
    current_vlan = None
    current_id = None

    lines = raw_text.split("\n")

    for line in lines:
        line = line.strip()

        vlan_match = re.match(r"VLAN(\d+)", line)
        if vlan_match:
            current_vlan = vlan_match.group(1)
            parsed_stp_data[current_vlan] = {
                "vlan_id": int(current_vlan),
                "vlan_id_str": current_vlan,
                "protocol": "",
                "root_id": {},
                "bridge_id": {},
            }
            continue

        if current_vlan:
            protocol_match = re.search(r"Spanning tree enabled protocol (\S+)", line)
            if protocol_match:
                parsed_stp_data[current_vlan]["protocol"] = protocol_match.group(1)
                continue

            if line.startswith("Root ID") or line.startswith("Bridge ID"):
                current_id = "root_id" if line.startswith("Root ID") else "bridge_id"
                priority_match = re.search(r"Priority\s+(\d+)", line)
                if priority_match:
                    priority = int(priority_match.group(1))
                    parsed_stp_data[current_vlan][current_id]["priority"] = priority
            elif line.startswith("Address"):
                address_match = re.search(r"Address\s+([0-9a-fA-F.]+)", line)
                if address_match:
                    parsed_stp_data[current_vlan][current_id]["address"] = (
                        address_match.group(1)
                    )
            elif line.startswith("Cost"):
                cost_match = re.search(r"Cost\s+(\d+)", line)
                if cost_match:
                    cost = int(cost_match.group(1))
                    parsed_stp_data[current_vlan][current_id]["cost"] = cost
            elif "This bridge is the root" in line:
                parsed_stp_data[current_vlan][current_id]["cost"] = 0
            elif "Hello Time" in line:
                counters_match = re.search(
                    r"Hello Time\s+(\d+).*Max Age\s+(\d+).*Forward Delay\s+(\d+)", line
                )
                if counters_match:
                    parsed_stp_data[current_vlan][current_id]["counters"] = {
                        "hello_time": int(counters_match.group(1)),
                        "max_age": int(counters_match.group(2)),
                        "forward_delay": int(counters_match.group(3)),
                    }
            elif line.startswith("Aging Time"):
                aging_time_match = re.search(r"Aging Time\s+(\d+)", line)
                if aging_time_match and current_id == "bridge_id":
                    if "counters" not in parsed_stp_data[current_vlan][current_id]:
                        parsed_stp_data[current_vlan][current_id]["counters"] = {}
                    parsed_stp_data[current_vlan][current_id]["counters"][
                        "aging_time"
                    ] = int(aging_time_match.group(1))

    return parsed_stp_data


def format_stp_parsed_info(parsed_stp_data: Dict[str, Dict[str, Any]]) -> str:
    formatted_data = []
    for vlan, data in parsed_stp_data.items():
        formatted_data.append(f"\nVLAN{vlan}")
        formatted_data.append(f"  vlan_id      {data['vlan_id']}")
        formatted_data.append(f"  vlan_id_str  {data['vlan_id_str']}")
        if "protocol" in data:
            formatted_data.append(f"  protocol     {data['protocol']}")
        for id_type in ["root_id", "bridge_id"]:
            if data[id_type]:
                formatted_data.append(f"  {id_type}")
                for key, value in data[id_type].items():
                    if key == "counters":
                        formatted_data.append("    counters")
                        for counter_key, counter_value in value.items():
                            formatted_data.append(
                                f"      {counter_key:<14} {counter_value}"
                            )
                    else:
                        formatted_data.append(f"    {key:<14} {value}")

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

    vlans_found = list(parsed_stp_data_list[0].keys())
    print(f"\nvlans_found: {vlans_found}")
    print(f"\nNumber of VLANs found: {len(vlans_found)}\n")

    print(20 * "*")
    # Extraer información para cada VLAN encontrada
    for vlan_id in vlans_found:
        vlan_info = parsed_stp_data_list[0].get(vlan_id)
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
