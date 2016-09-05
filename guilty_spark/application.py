import logging
from guilty_spark.bot import Monitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s|%(levelname)s|%(message)s',
)
logger = logging.getLogger(__package__)

try:
    # Attempt to load a new bot instance with the default settings location
    bot = Monitor(settings_file='settings.yml')
except IOError:
    exit()
