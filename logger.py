import time
import logging
import sys

log_level = 'DEBUG'
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(stream = sys.stdout, level = log_level, format = log_format)
# logging.basicConfig(filename='logging.log', level = log_level, format = log_format)

# Set the log to use GMT time zone
logging.Formatter.converter = time.gmtime

# Add milliseconds
logging.Formatter.default_msec_format = '%s.%03d'
