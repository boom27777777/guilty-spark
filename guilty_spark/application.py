from guilty_spark.bot import Monitor

try:
    # Attempt to load a new bot instance with the default settings location
    bot = Monitor(settings_file='settings.yml')
except IOError:
    exit()
