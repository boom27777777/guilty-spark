"""
:Date: 2016-08-03
:Author:
    - Jackson McCrea (jacksonmccrea@gmail.com)
"""
import yaml


DEFAULT_CONFIG = {
    'owner': '[Your discord id string]',
    'token': '[API token]',
    'command_prefix': '!',
    'character_limit': 2000
}


def write_config(path, config):
    with open(path, 'w') as config_file:
        yaml.dump(config, config_file, default_flow_style=False)


def load_config(path):
    config = DEFAULT_CONFIG
    try:
        with open(path) as config_file:
            config = yaml.load(config_file)
    except IOError:
        write_config(path, config)
        raise IOError('No settings file found, making one for you now.')

    dirty = False
    for key in DEFAULT_CONFIG:
        if key not in config:
            config[key] = DEFAULT_CONFIG[key]
            dirty = True

    if dirty:
        write_config(path, config)

    return config
