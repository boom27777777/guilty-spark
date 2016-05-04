from guilty_spark import get_resource

def plugin_file(name: str, mode: str='r'):
    return open(get_resource('plugin_data', name), mode)
