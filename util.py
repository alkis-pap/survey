
def flatten(data):
    result = {}
    for key in data:
        if type(data[key]) is dict:
            for subkey in data[key]:
                result[key + "_" + subkey] = data[key][subkey]
        else:
            result[key] = data[key]
    return result