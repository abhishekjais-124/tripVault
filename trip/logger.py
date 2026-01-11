import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'trip')
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logger for trip app
trip_logger = logging.getLogger('trip')
trip_logger.setLevel(logging.DEBUG)

# Create file handler for all logs
log_file = os.path.join(LOG_DIR, 'trip.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create file handler for errors only
error_log_file = os.path.join(LOG_DIR, 'trip_errors.log')
error_file_handler = logging.FileHandler(error_log_file)
error_file_handler.setLevel(logging.ERROR)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler.setFormatter(formatter)
error_file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
if not trip_logger.handlers:
    trip_logger.addHandler(file_handler)
    trip_logger.addHandler(error_file_handler)
    trip_logger.addHandler(console_handler)

def get_logger(module_name):
    """Get a logger instance for a specific module"""
    return logging.getLogger(f'trip.{module_name}')
