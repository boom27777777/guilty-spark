from guilty_spark import get_resource

def plugin_file(name: str, mode: str='r'):
    with open(get_resource('plugin_data', name), mode) as data_file:
        return data_file
