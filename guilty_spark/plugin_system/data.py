import yaml

from guilty_spark import get_resource


def plugin_file(name: str, mode: str='r'):
    """ Helper function to get a file located in the bot's plugin data
    directory

    :param name:
        File name
    :param mode:
        Appropriate open() mode Default: 'r'
    :return:
        An open file handle of the given mode ready for IO
    """
    return open(get_resource('plugin_data', name), mode)


def cache_yml(cache_path: str, data: dict):
    with plugin_file(cache_path, 'w') as cache:
        yaml.dump(data, cache)


def load_yml(cache_path: str, empty=None):
    try:
        with plugin_file(cache_path) as cache:
            data = yaml.load(cache)
    except IOError:
        data = empty

    return data
