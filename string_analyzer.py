import definitions
import definition_helper


def analyze_string(data: str):
    result: set[str] = {*""}
    for variable_entry in definitions.__dir__():
        definition = getattr(definitions, variable_entry)
        if isinstance(definition, definition_helper.Definition):
            if definition(data):
                result.add(definition.tag)
    return [*result]


if __name__ == '__main__':
    print(analyze_string("%http://crl.globalsign.com/root-r3.crl0c"))
