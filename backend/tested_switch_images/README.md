# Tested images

## Server information

- VMware® Workstation 17 Pro - *Version: 17.5.2 build-23775571*
- Linux pnetlab 4.15.18-pnetlab2 #1 SMP Sun Jan 31 20:04:56 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
- PNETLab v4.2.10
- ishare2: 3.5.4-main

## List of tested images

|  #  | Image name                                      | Working? | Description                                                   | *ishare2* command     |
| :-: | :---------------------------------------------: | :------: | :-----------------------------------------------------------: | :-------------------: |             
|  1  | vios-15.5.3M                                    |   No     | No *interface vlan 1* command available                       | ishare2 pull qemu 918 |
|  2  | viosl2-adventerpriseK9-M_152_May_2018           |   No     | Problem with STP interface Role/Status                        | ishare2 pull qemu 931 |
|  3  | viosl2-adventerprisek9-m.ssa.high_iron_20190423 |   No     | Booting constantly. It crashes after a while                  | ishare2 pull qemu 935 |
|  4  | viosl2-15.2.4.55e                               |   Yes/No    | It works fine most of the time but suddendly an error appears (See Comment 1 below)    | ishare2 pull qemu 930 |

## Comments

### Comment 1

#### Problem description

This log message may appear after the initial startup (not for all devices) and after a few minutes of the startup time (again, not for all devices). Apparently, it appears on SW4 and SW5. All devices are the same, same configuration. 

#### Error content

*Jul 15 18:30:07.783: %CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on GigabitEthernet0/3
 (not full duplex), with SW5.jeremysitlab.com GigabitEthernet0/0 (full duplex).

*Jul 15 18:30:10.495: %CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on GigabitEthernet0/3
 (not full duplex), with SW5.jeremysitlab.com GigabitEthernet0/0 (full duplex).

*Jul 15 18:30:12.238: %CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on GigabitEthernet0/3
 (not full duplex), with SW5.jeremysitlab.com GigabitEthernet0/0 (full duplex).

*Jul 15 18:30:13.524: %CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on GigabitEthernet0/3
 (not full duplex), with SW5.jeremysitlab.com GigabitEthernet0/0 (full duplex).