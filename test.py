import json
import pprint


def filter_true_nodes(nodelist):
    result = []
    for node in nodelist:
        if node.get('success'):
            result.append({
                **node,
                "children": filter_true_nodes(node.get('children') or [])
            })
    return result


if __name__ == '__main__':
    with open("./test2.json", "r") as file:
        data = json.load(file)
    pprint.pp(filter_true_nodes([data[1]]))
