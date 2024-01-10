import json
import pprint
from server.database import db_connect

connection = db_connect()

with open('data_function.json', 'r') as file:
    data = json.loads(file.read().rstrip("[0m\r\n "))


def analyze_match_object(item):
    def analyze_match(match):
        positive_nodes = []

        def analyze_match_node(node):
            if not node["success"]:
                return
            if node["node"].get("type") == 'feature':
                feature_data = node["node"].get("feature")
                positive_nodes.append({
                    "feature": {
                        "type": feature_data["type"],
                        "data": json.dumps(feature_data[feature_data["type"]])
                    },
                    "locations": node["locations"]
                })
            for child in node["children"]:
                analyze_match_node(child)

        analyze_match_node(match[1])

        return {
            "location": match[0],
            "true_feature_nodes": positive_nodes
        }

    matches = []

    for match in item["matches"]:
        matches.append(analyze_match(match))

    truncated = {
        "name": item["meta"]["name"],
        "scope": item["meta"]["scope"],
        "matches": matches
    }

    return truncated


out = []

rules = data["rules"]
for item in rules.values():
    out.append(analyze_match_object(item))

pprint.pp(out)
