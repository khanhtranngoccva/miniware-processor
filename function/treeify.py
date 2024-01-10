import copy
import json
import pprint

with open('data_function.json', 'r') as file:
    data = json.loads(file.read().rstrip("[0m\r\n "))


def analyze_match_object(match_object):
    def analyze_match(match):
        return {
            "location": match[0],
            "nodes": process_tree(match[1])
        }

    matches = []

    for match in match_object["matches"]:
        matches.append(analyze_match(match))

    truncated = {
        "name": match_object["meta"]["name"],
        "scope": match_object["meta"]["scope"],
        "matches": matches
    }

    return truncated


def parse_ds(data):
    out = []

    rules = data["rules"]
    for item in rules.values():
        out.append(analyze_match_object(item))

    return out


def process_tree(root):
    flattened_nodes = []

    def process_node(node, path="0"):
        try:
            if node["node"]["type"] == "statement":
                out_node = {
                    "type": "statement",
                    "subtype": node["node"]["statement"]["type"],
                    "data": None,
                }
            elif node["node"]["type"] == "feature":
                subtype = node["node"]["feature"]["type"]
                out_node = {
                    "type": "feature",
                    "subtype": subtype,
                    "data": node["node"]["feature"][subtype.replace(" ", "_")],
                    "description": node["node"]["feature"].get("description", None)
                }
            else:
                raise Exception("Unknown node type")
        except Exception as e:
            print(node)
            raise e

        for index, child_node in enumerate(node["children"]):
            process_node(child_node, f"{path}.{index}")

        flattened_nodes.append({
            "success": node["success"],
            "path": path,
            "node": out_node,
            "locations": copy.deepcopy(node["locations"]),
        })

    process_node(root)
    return flattened_nodes


pprint.pprint(parse_ds(data))
