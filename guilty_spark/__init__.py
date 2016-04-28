from os.path import abspath, join, dirname


def get_resource(*path):
    return abspath(join(dirname(__file__), *path))
