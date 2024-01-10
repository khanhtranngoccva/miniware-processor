import copy
import json
import pprint

from helpers import generate_ids


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
        "namespace": match_object["meta"].get("namespace", None),
        "scope": match_object["meta"]["scope"],
        "matches": matches
    }

    return truncated


def prepare_ds(data):
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
                    "description": None,
                }
            elif node["node"]["type"] == "feature":
                subtype = node["node"]["feature"]["type"]
                out_node = {
                    "type": "feature",
                    "subtype": subtype,
                    "data": json.dumps(node["node"]["feature"][subtype.replace(" ", "_")]),
                    "description": node["node"]["feature"].get("description", None)
                }
            else:
                raise Exception("Unknown node type")
        except Exception as e:
            print(node)
            raise e

        for index, child_node in enumerate(node["children"]):
            process_node(child_node, f"{path}.{index}")

        locations = []
        for location in copy.deepcopy(node["locations"]):
            if location["type"] == "no address":
                continue
            locations.append(location)

        flattened_nodes.append({
            "success": node["success"],
            "path": path,
            "node": out_node,
            "locations": locations,
        })

    process_node(root)
    return flattened_nodes


def insert_capa_entries(conn, analysis_id, capa_entries):
    layer_1 = prepare_ds(capa_entries)
    layer_2 = []
    layer_3 = []
    layer_4 = []

    insert_operation_id_1 = generate_ids.generate_insert_operation_id()
    insert_operation_id_2 = generate_ids.generate_insert_operation_id()
    insert_operation_id_3 = generate_ids.generate_insert_operation_id()

    with conn.cursor() as cursor:
        # Layer 1
        with cursor.copy(
                "COPY capa_entries "
                "(_insert_operation_id, _insert_operation_order, analysis_id, "
                "rule_name, rule_namespace, rule_scope) FROM STDIN") as copy:
            for order, entry in enumerate(layer_1):
                copy.write_row([
                    insert_operation_id_1, order, analysis_id,
                    entry["name"], entry["namespace"], entry["scope"]
                ])
        for entry_id, order in cursor.execute(
                "SELECT id, _insert_operation_order FROM capa_entries WHERE _insert_operation_id = %s",
                [insert_operation_id_1]):
            entry_object = layer_1[order]
            for match in entry_object["matches"]:
                match["entry_id"] = entry_id
                layer_2.append(match)
        # Layer 2
        with cursor.copy(
                "COPY capa_matches "
                "(_insert_operation_id, _insert_operation_order, capa_entry_id, "
                "location_type, location_value) FROM STDIN"
        ) as copy:
            for order, match in enumerate(layer_2):
                copy.write_row([
                    insert_operation_id_2, order, match["entry_id"],
                    match["location"]["type"], match["location"]["value"]
                ])
        for match_id, order in cursor.execute(
                "SELECT id, _insert_operation_order FROM capa_matches WHERE _insert_operation_id = %s",
                [insert_operation_id_2]):
            match_object = layer_2[order]
            for capa_node in match_object["nodes"]:
                capa_node["match_id"] = match_id
                layer_3.append(capa_node)
        # Layer 3
        with cursor.copy(
                "COPY capa_nodes (_insert_operation_id, _insert_operation_order, capa_match_id, "
                "path, success, type, "
                "subtype, feature_data, description) FROM STDIN"
        ) as copy:
            for order, node in enumerate(layer_3):
                copy.write_row([
                    insert_operation_id_3, order, node["match_id"],
                    node["path"], node["success"], node["node"]["type"],
                    node["node"]["subtype"], node["node"]["data"], node["node"]["description"]
                ])
        for node_id, order in cursor.execute(
                "SELECT id, _insert_operation_order FROM capa_nodes WHERE _insert_operation_id = %s",
                [insert_operation_id_3]):
            node_object = layer_3[order]
            for capa_node_location in node_object["locations"]:
                capa_node_location["capa_node_id"] = node_id
                layer_4.append(capa_node_location)
        # Layer 4
        with cursor.copy(
                "COPY capa_node_locations (capa_node_id, type, value) FROM STDIN"
        ) as copy:
            for order, node_location in enumerate(layer_4):
                copy.write_row([
                    node_location["capa_node_id"], node_location["type"], node_location["value"]
                ])
