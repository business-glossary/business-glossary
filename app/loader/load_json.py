'''Load data from json file'''
from os.path import dirname, join
import pprint
import json

from config import BASE_DIR


file_path = join(dirname(BASE_DIR), 'bg_interface')

file_name = join(file_path, "bg_interface_terms_1.json")

json_data = open(file_name).read()

data = json.loads(json_data)

pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(data)

for p in data:
    print p["name"]
    print "Links:", p["links"]
    print "Rules:", p["rules"]