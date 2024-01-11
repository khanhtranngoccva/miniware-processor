import definitions
from helpers import definition_helper
import types
import pkgutil
import os
import importlib

definitions: types.ModuleType


def import_modules(package: types.ModuleType):
    for _, module_name, ispkg in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
        module = importlib.import_module(module_name)

        if ispkg:
            for sub_module in import_modules(module):
                yield sub_module
        yield module


def load_definitions():
    res = []
    for module in import_modules(definitions):
        for name in module.__dir__():
            entry = getattr(module, name)
            if isinstance(entry, definition_helper.Definition):
                res.append(entry)
    return res


loaded_definitions = load_definitions()


def analyze_string(data: str):
    result: set[str] = {*""}
    matches = []
    for definition in loaded_definitions:
        # Definitions can return True, False, or an array of strings.
        definition_return = definition(data)
        if definition_return:
            result.add(definition.tag)
            # If return value is an array, iterate through it
            if isinstance(definition_return, list):
                for match in definition_return:
                    matches.append({
                        "match": match,
                        "definition": definition.name
                    })
    return {
        "tags": [*result],
        "matches": [*matches]
    }
