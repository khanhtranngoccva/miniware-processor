import copy
import json
import pprint

with open('data_function.json', 'r') as file:
    data = json.loads(file.read().rstrip("[0m\r\n "))

from server.entity.capa_entries import prepare_ds

raw_out = prepare_ds(data)
print(raw_out[0])