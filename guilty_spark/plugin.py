import logging
from os import listdir
from importlib import import_module, invalidate_caches

from guilty_spark import get_resource
from guilty_spark.bot import Monitor


class PluginManager():
    def __init__(self):
        self.plugin_dir = get_resource('plugins')
        self.plugins = {}

    def plugin_functions(self, module):
        return [(f, getattr(module, f)) for f in dir(module) if 'on_' in f]

    def load_plugin(self, name):
        module = import_module('guilty_spark.plugins.{}'.format(name))
        plug_func = self.plugin_functions(module)

        if not plug_func:
            return

        coro_test = [n for n, f in plug_func if not f._is_coroutine]
        if coro_test:
            logging.error('Failed to load plugin %s, function %s is not '
                          'a coroutine', name, ','.join(coro_test))
            return

        self.plugins[name] = plug_func
        logging.info('Loaded plugin %s', name)

    def load(self):
        invalidate_caches()
        for plugin in listdir(self.plugin_dir):
            if plugin in ['__init__.py', '__pycache__.py']:
                continue

            name = plugin.split('.')[0]
            self.load_plugin(name)

    def bind(self, bot: Monitor):
        for plugin in self.plugins.values():
            for name, func in plugin:
                bot.register_function(name, func)
