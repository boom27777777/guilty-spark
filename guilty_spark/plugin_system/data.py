import asyncio
import yaml
import json
import aioredis

from guilty_spark import get_resource


def plugin_file(name: str, mode: str = 'r'):
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


def cache_yml(cache_path: str, data):
    with plugin_file(cache_path, 'w') as cache:
        yaml.dump(data, cache)


def load_yml(cache_path: str, empty=None):
    try:
        with plugin_file(cache_path) as cache:
            data = yaml.load(cache)
    except IOError:
        data = empty

    return data


class CachedDict(dict):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = 'CachedDict-' + name
        self._redis = None

    def _serializable(self):
        serializable = {}
        for key in [k for k in self if k != '_redis']:
            serializable[key] = self[key]
        return serializable

    async def _make_redis(self):
        self._redis = await aioredis.create_redis(
            ('localhost', 6379), loop=asyncio.get_event_loop())

    def _load_keys(self, data: bytes):
        for key, item in json.loads(data.decode()).items():
            self[key] = item

    async def load(self):
        if not self._redis:
            await self._make_redis()

        data = await self._redis.get(self.name)

        if isinstance(data, bytes):
            try:
                self._load_keys(data)
            except:
                for k in self._serializable():
                    del self[k]

            return True
        return False

    async def cache(self):
        if self._redis:
            data = self._serializable()
            dump = json.dumps(data, separators=(',', ':'))
            await self._redis.set(self.name, dump)
