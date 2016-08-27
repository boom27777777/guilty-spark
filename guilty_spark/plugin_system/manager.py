import logging
from os import listdir
from importlib import import_module, invalidate_caches

from guilty_spark import get_resource
from guilty_spark.bot import Monitor
from guilty_spark.plugin_system.dynamic import Dynamic
from guilty_spark.plugin_system.plugin import Plugin


class PluginManager:
    """ Plugin managing class """

    def __init__(self):
        """ Initializes a new plugin manager with the base plugin directory """
        self.plugin_dir = 'plugins'
        self.plugins = []

    @staticmethod
    def plugin_objects(module):
        """ Walks a modules global names and searches for the plugin class

        :param module:
            The module to search
        :return:
            The plugin class if a plugin was found, else None
        """

        for name in dir(module):
            item = getattr(module, name)
            if isinstance(item, type):
                if issubclass(item, Plugin):
                    if item != Plugin:
                        return item

            if isinstance(item, Dynamic):
                if item != Dynamic:
                    return item.make_plug()

    def load_plugin(self, name):
        """ Load a given name and search for a plugin

        :param name:
            The name to import
        """

        try:
            module = import_module('plugins.{}'.format(name))
        except:
            logging.error('Failed to load plugin %s', name)
            raise
            return

        plug_obj = self.plugin_objects(module)

        if plug_obj:
            self.plugins.append((name, plug_obj))

            logging.info('Loaded plugin %s', name)

    def load(self):
        """ Loads all plugins found in the **self.plugin_dir**

            Invalidates module caches and loads all modules under the plugin
            Directory
        """

        invalidate_caches()
        for plugin in listdir(self.plugin_dir):
            if plugin in ['__init__.py', '__pycache__.py']:
                continue

            name = plugin.split('.')[0]
            self.load_plugin(name)

    def bind(self, bot: Monitor):
        """ Iterates through bots plugins and calls bot.register_plugin for
            each one

        :param bot:
            The Monitor object to bind to
        """
        for name, obj in self.plugins:
            plugin = obj(name, bot)
            bot.register_plugin(plugin)
