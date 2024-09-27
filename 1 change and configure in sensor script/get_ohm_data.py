import argparse
import requests

# Tworzenie parsera argumentów
parser = argparse.ArgumentParser()


parser.add_argument('HOST', type=str, help='HOST address')
parser.add_argument('--port', type=int, default=8085, help='PORT number (default 8085)')

args = parser.parse_args()

if not args.HOST:
    parser.print_help()
    exit(1)

data_url = f"http://{args.HOST}:{args.port}/data.json"

response = requests.get(data_url, timeout=30)
jsondata = response.json()

import os



input_list_content = []

input_list = "OHM_"+ args.HOST +"_input_list.txt"

# striped 
# https://github.com/home-assistant/core/blob/dev/homeassistant/components/openhardwaremonitor/sensor.py
# to get mesurements names from OpenHardwareMonitor

OHM_CHILDREN = "Children"
OHM_NAME = "Text"
OHM_VALUE = "Value"
OHM_VALUE = "Value"
OHM_MIN = "Min"
OHM_MAX = "Max"
	
def parse_children(json, devices, path, names):
        """Recursively loop through child objects, finding the values."""
        result = devices.copy()

        if json["Children"]:
            for child_index in range(len(json[OHM_CHILDREN])):
                child_path = path.copy()
                child_path.append(child_index)

                child_names = names.copy()
                if path:
                    child_names.append(json[OHM_NAME])

                obj = json[OHM_CHILDREN][child_index]
#                 print(obj)

                added_devices = parse_children(
                    obj, devices, child_path, child_names
                )

                result = result + added_devices
            return result

        if json[OHM_VALUE].find(" ") == -1:
            return result

        unit_of_measurement = json[OHM_VALUE].split(" ")[1]
        child_names = names.copy()
        child_names.append(json[OHM_NAME])
        fullname = " ".join(child_names)

        input_list_content.append(fullname)

        return result

devices = parse_children(jsondata, [], [], [])

if len(input_list_content):
    print("Writing input list to file ", input_list)
    with open(input_list, 'w') as file:
        file.write("        blacklist_content = [\n")
        for i, element in enumerate( sorted(set(input_list_content)), start = 1 ):
            print(f"{i}. {element}")
            if i < len(input_list_content):
                file.write(f"        '{element}',\n")
            else:
                file.write(f"        '{element}'\n        ]")
else:
    print("No data collected")