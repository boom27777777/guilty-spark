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
}


def load_config(path):
    config = DEFAULT_CONFIG
    try:
        with open(path) as config_file:
            config = yaml.load(config_file)
    except IOError:
        with open(path, 'w') as config_file:
            yaml.dump(config, config_file, default_flow_style=False)
        raise IOError('No settings file found, making one for you now.')

    return config
