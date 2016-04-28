from guilty_spark.bot import Monitor

try:
    bot = Monitor(settings_file='settings.yml')
except IOError:
    exit()
