import logging
from os import listdir
from importlib import import_module, invalidate_caches

from guilty_spark import get_resource
from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.plugin import BasePlugin


class PluginManager():
    def __init__(self):
        self.plugin_dir = get_resource('plugins')
        self.plugins = {}

    def plugin_objects(self, module):
        objects = []
        for name in dir(module):
            item = getattr(module, name)
            if isinstance(item, type) and issubclass(item, BasePlugin):
                objects.append(item)

        return objects

    def load_plugin(self, name):
        module = import_module('guilty_spark.plugins.{}'.format(name))
        plug_objs = self.plugin_objects(module)

        if plug_objs:
            self.plugins[name] = plug_objs
            logging.info('Loaded plugin %s', name)

    def load(self):
        invalidate_caches()
        for plugin in listdir(self.plugin_dir):
            if plugin in ['__init__.py', '__pycache__.py']:
                continue

            name = plugin.split('.')[0]
            self.load_plugin(name)

    def bind(self, bot: Monitor):
        for name, obj in self.plugins.values():
            plugin = obj(bot)
            bot.register_plugin(name, plugin)
