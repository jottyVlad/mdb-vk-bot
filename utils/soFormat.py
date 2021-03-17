from typing import Dict, Union


def convert_datatypes(dictionary: Dict[str, str]) -> dict:
    result = {}
    for key, value in dictionary.items():
        if dictionary[key].isdigit() \
                or (dictionary[key][0] == '-' and dictionary[key][1:].isdigit()):
            result[key] = int(dictionary[key])

        elif dictionary[key].count('.') == 1 \
                and all([a.isdigit() for a in dictionary[key].split('.')]):
            result[key] = float(dictionary[key])

        else:
            result[key] = dictionary[key]

    return result


def parse(string_to_parse: str) -> Dict[str, Union[int, str, float]]:
    data = string_to_parse.split(',')
    result = {}
    for i in data:
        key, value = i.strip().split(':')
        result[key.strip()] = value.strip()

    result = convert_datatypes(result)

    return result
