def convert_datatypes(dictionary: dict) -> dict:
    for key, value in dictionary.items():
        try:
            dictionary[key] = int(dictionary[key])
        except ValueError:
            try:
                dictionary[key] = float(dictionary[key])
            except ValueError:
                pass

    return dictionary


def parse(string_to_parse: str) -> dict:
    data = string_to_parse.split(',')
    result = {}
    for i in data:
        key, value = i.strip().split(':')
        result[key.strip()] = value.strip()

    result = convert_datatypes(result)

    return result
