# OHM-blacklist-4-HA

OpenHardwareMonitor component for Home Assistant logs in databases everything it gets from OHM.
There can be big number of parameters, for my PC I get 85 items, not everyone neccessary for monitoring.
Data of these measurements takes space logged every minute.

I was looking for some method to be able to filter what I want to be logged and way to get rid of unnecesary data, not found.

I started to try make it myself.

**Test at your own risk.
HA can broke 
you need to make full backup**

# 0
At first, there was a very ambitious plan to collect and manage configuration from within the program using configuration.yaml,
made two additional boolean flags and start to program gathering OHM ouput data to files,
than user should find the files, edit them to make blacklist file, and than set in configuration flag to use blacklist.
But I failed, I was unable to find place in my configuration to write a file from "sensor.py", the file is in the docker and I was unable to write anything to file system.
So folder "0 unable to write file" is a "work in progress" of the idea to preserve some ideas.

# 1
Second idea was to gather OHM ouput data manually and than making blacklist and put in in the code of OHM component script.
This version is in folder "1 change and configure in sensor script".

First we need to get list of measure names from OHM.

I get openhardwaremonitor sensor.py edited to make just this,
https://github.com/home-assistant/core/blob/dev/homeassistant/components/openhardwaremonitor/sensor.py

file name is get_ohm_data.py and you can call it with hostname and service port (default 8085)
```
c:\get_ohm_data.py 192.168.2.100
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

c:\
```
program shows list and write it to file.
Contents of example OHM_192.168.2.100_input_list.txt:

```
        blacklist_content = [
        'SUGO9 NVMe 1 Load Used Space',
        'SUGO9 NVMe 2 Load Used Space',
        'SUGO9 z390 plyta Voltages Voltage #6'
        ]
```
After collecting these files for every OHM instance you want to filter
you need to join them and edit to leave only lines which you want to filter out, to not collect its data.


Next you need to find your openhardwaremonitor sensor.py
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

And now I change it to
```python
        blacklist_content = [
        ]

        if fullname not in blacklist_content:
            dev = OpenHardwareMonitorDevice(self, fullname, path, unit_of_measurement)
            result.append(dev)
        else:
            _LOGGER.info("Eliminate OHW %s from logging", fullname)

        return result
```
changing "blacklist_content = []" to prepared black \list

```python
        blacklist_content = [
        'SUGO9 NVMe 1 Load Used Space',
        'SUGO9 NVMe 2 Load Used Space',
        'SUGO9 z390 plyta Voltages Voltage #6'
        ]

        if fullname not in blacklist_content:
            dev = OpenHardwareMonitorDevice(self, fullname, path, unit_of_measurement)
            result.append(dev)
        else:
            _LOGGER.info("Eliminate OHW %s from logging", fullname)

        return result
```

After edit you save, restart Homeassistant and filtering should work, 

you can check it on overview, find the names of filtered objects and check how long ago new data arrived, 
for not filtered items there should come new data every minute
for blacklisted it should get older and older.

Other way to observe if changes work is change logging in configuration.yaml to 
```
# Configure a default setup of Home Assistant (frontend, api, etc)
default_config:

logger:
  default: warning
  logs:
    homeassistant.components.openhardwaremonitor: info
```
and after restart you should found in logs such info:
```
2024-09-27 14:52:06.175 INFO (SyncWorker_2) [homeassistant.components.openhardwaremonitor.sensor] Eliminate OHW SUGO9 i9-9900K Clocks CPU Core #2 from logging
2024-09-27 14:52:06.176 INFO (SyncWorker_2) [homeassistant.components.openhardwaremonitor.sensor] Eliminate OHW SUGO9 i9-9900K Clocks CPU Core #3 from logging
2024-09-27 14:52:09.461 WARNING (MainThread) [homeassistant.components.sensor] Platform openhardwaremonitor not ready yet: None; Retrying in background in 30 seconds
```

# 2
I don't like configuration of blacklist is in script file
I was looking for way to store it and make accesible in configuration.yaml
It was for me hard to understand how info from the file is transfered to the program, but with tries and errors,
with looking for other code, I managed.

It is not rock solid, I got some errors from time to time, but I decided to share.

**Implementing this version and previous "1" version anyway is all your responsibility.**


_By the way, _

_I think all this workaround is stupid, _

_there should be another checkbox in OHM if the data should be transfered to webserver, as it is checkbox to making graphs._

_And there is still problerm, new data is not collected, but how to easy get rid of old data and remove old names form Home assistant?_


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
it need to be changed to this

```python
        fullname = " ".join(child_names)

        if fullname not in self._config.get( CONF_OPTIONS ):
            dev = OpenHardwareMonitorDevice(self, fullname, path, unit_of_measurement)
            result.append(dev)
        else:
            _LOGGER.info("Eliminate OHW %s from logging", fullname)


        return result
```

We need another change in code to make it able to read blacklist info form configuration.yaml

find this part:

```python
OHM_NAME = "Text"

PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_HOST): cv.string, vol.Optional(CONF_PORT, default=8085): cv.port}
)
```

and change to


```python
OHM_NAME = "Text"

CONF_OPTIONS: Final = "blacklist"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_HOST): cv.string
	, vol.Optional(CONF_PORT, default=8085): cv.port
	, vol.Optional(CONF_OPTIONS, default=[]): vol.All(cv.ensure_list, [cv.string])
     }
)
```

After changing sensor.py you need to restart Home Assistant to make it able to read new format of configuration.yaml

Than you still need to collect OHM info.
With another prepared script, it makes another format file to edit it to blacklist:

file name is get_ohm_data.py and you can call it with hostname and service port (default 8085)
```
c:\get_ohm_data.py 192.168.2.100
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

c:\
```
program shows list and write it to file.
Contents of example OHM_192.168.2.100_input_list.txt:

```
    blacklist:
      - 'SUGO9 NVMe 1 Load Used Space'
      - 'SUGO9 NVMe 2 Load Used Space'
      - 'SUGO9 RAM 64GB Data Available Memory'
      - 'SUGO9 RAM 64GB Data Used Memory'
      - 'SUGO9 RAM 64GB Load Memory'
```

This list you need to edit leaving only items you don't want data anymmore,
and move it to configuration.yaml:

```
sensor:
  - platform: openhardwaremonitor
    host: 192.168.2.100
    blacklist:
      - 'SUGO9 i9-9900K Clocks CPU Core #2'
      - 'SUGO9 i9-9900K Clocks CPU Core #3'
```
repeat for every OHM sensor.

restart Homeassistant and filtering should work, 
you can check it on overview, find the names of filtered objects and check how long ago new data arrived, 
for not filtered items there should come new data every minute
for blacklisted it should get older and older.

Other way to observe if changes work is changing logging in configuration.yaml to 
```
# Configure a default setup of Home Assistant (frontend, api, etc)
default_config:

logger:
  default: warning
  logs:
    homeassistant.components.openhardwaremonitor: info
```
and after restart you should found in logs such info:
```
2024-09-27 14:52:06.175 INFO (SyncWorker_2) [homeassistant.components.openhardwaremonitor.sensor] Eliminate OHW SUGO9 i9-9900K Clocks CPU Core #2 from logging
2024-09-27 14:52:06.176 INFO (SyncWorker_2) [homeassistant.components.openhardwaremonitor.sensor] Eliminate OHW SUGO9 i9-9900K Clocks CPU Core #3 from logging
2024-09-27 14:52:09.461 WARNING (MainThread) [homeassistant.components.sensor] Platform openhardwaremonitor not ready yet: None; Retrying in background in 30 seconds
```


