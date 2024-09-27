# OHM-blacklist-4-HA

OpenHardwareMonitor component fo Home Assistant logs in databases everything it gets from OHM.
There can be big number of parameters,m for my PC I get 85 items, not everyone neccessery for monitoring.
Data of these measurements takes space logged every minute.

I was looking for some method to be ablle to filter what I want to be logged and way to get rid of unnecesary data, not found.

I start to try make it myself, 

0
At first, there was a very ambitious plan to colect and manage configuration from within the program using configuration.yaml,
made two additional boolin flags and start to program gathering OHM inpout data to files,
than user shopuld find the files, edit them to make blacklist file, and than set in configuration flag to use blacklist.
But I failed, I was unable to find place in my configuration to write a file from "sensor.py", the file is in the docker and I was unable to write anything to file system.
So folder "0 unable to write file" is a "work in progress" of the idea.

1
Second is gathering OHM ouput data manually and than making blacklist and put in in the code of OHM component script.
This version is in folder "1 change and configure in sensor script".

First we need to get list of measure names form OHM.
I get openhardwaremonitor sensor.py edited to make just this,
https://github.com/home-assistant/core/blob/dev/homeassistant/components/openhardwaremonitor/sensor.py
file name is get_ohm_data.py and you can call it with hostname and service port (default 8085)
```
get_ohm_data.py 192.168.2.100
Writing input list to file  OHM_192.168.2.100_input_list.txt
1. SUGO9 NVMe 1 Load Used Space
2. SUGO9 NVMe 2 Load Used Space
5. SUGO9 RAM 64GB Load Memory
6. SUGO9 RTX3080 Clocks GPU Core
7. SUGO9 RTX3080 Clocks GPU Memory
8. SUGO9 RTX3080 Clocks GPU Shader
......
36. SUGO9 i9-9900K Load CPU Core #1
37. SUGO9 i9-9900K Load CPU Core #2
46. SUGO9 i9-9900K Powers CPU DRAM
47. SUGO9 i9-9900K Powers CPU Graphics
48. SUGO9 i9-9900K Powers CPU Package
49. SUGO9 i9-9900K Temperatures CPU Core #1
50. SUGO9 i9-9900K Temperatures CPU Core #2
85. SUGO9 z390 plyta Voltages Voltage #6
```
program shows list and write it to file configured for next steps.
Contents of example OHM_192.168.2.100_input_list.txt:

```
        blacklist_content = [
        'SUGO9 NVMe 1 Load Used Space',
        'SUGO9 NVMe 2 Load Used Space',
        'SUGO9 z390 plyta Voltages Voltage #6'
        ]
```
After collecting these files for every OHM instance you want to filter
you need to join them and edit to leave only lines wchich you want to filter out, to not collect its data.


Next you need to find your openhardwaremonitor sensor.py,
mine was at this path:
```
/var/lib/docker/overlay2/09090e774b30a3f259b562a510059e5095d1837fb9aed05c8ca16edbcffd4912/merged/usr/src/homeassistant/homeassistant/components/openhardwaremonitor/sensor.py
```
because I have old HA version, for long time not upgraded, I will show what I changed.
At the end of file I have such code:
```python
        fullname = " ".join(child_names)

        dev = OpenHardwareMonitorDevice(self, fullname, path, unit_of_measurement)

        result.append(dev)
        return result
```

