import definitions
import definition_helper
import types
import pkgutil
import os

definitions: types.ModuleType


def module_dir_scan(module_dir: types.ModuleType):
    paths = []
    for parent, _, __ in os.walk(module_dir.__path__[0]):
        paths.append(parent)

    for loader, module_name, is_pkg in pkgutil.walk_packages(paths):
        module_dir = loader.find_module(module_name).load_module(module_name)
        yield module_dir


def load_definitions():
    res = []
    for module in module_dir_scan(definitions):
        for name in module.__dir__():
            entry = getattr(module, name)
            if isinstance(entry, definition_helper.Definition):
                res.append(entry)
    return res


loaded_definitions = load_definitions()


def analyze_string(data: str):
    result: set[str] = {*""}
    matches: set[str] = {*""}
    for definition in loaded_definitions:
        # Definitions can return True, False, or an array of strings.
        definition_return = definition(data)
        if definition_return:
            result.add(definition.tag)
            # If return value is an array, iterate through it
            if isinstance(definition_return, list):
                for match in definition_return:
                    matches.add(match)
    return {
        "tags": [*result],
        "matches": [*matches]
    }


if __name__ == '__main__':
    for i in module_dir_scan(definitions):
        print(i)
