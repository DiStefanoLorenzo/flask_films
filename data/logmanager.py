import logging
import logging.handlers
import os

LOGS_FOLDER = '.'

def get_configured_logger(name=None):
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # This logger has no handlers, so we can assume it hasn't yet been configured
        # Create RotatingFileHandler
        formatter = "%(asctime)s | %(levelname)s | %(process)s | %(thread)s | %(filename)s | %(funcName)s():%(lineno)d | %(message)s"
        handler = logging.handlers.RotatingFileHandler(os.path.join(LOGS_FOLDER,'app.log'), maxBytes = 1024*1024*10, backupCount = 6)
        handler.setFormatter(logging.Formatter(formatter))
        handler.setLevel(logging.INFO)
        
        handler_d = logging.handlers.RotatingFileHandler(os.path.join(LOGS_FOLDER,'app_debug.log'), maxBytes = 1024*1024*10, backupCount = 2)
        handler_d.setFormatter(logging.Formatter(formatter))
        handler_d.setLevel(logging.DEBUG)

        handler_c = logging.StreamHandler()
        handler_c.setFormatter(logging.Formatter(formatter))
        handler_c.setLevel(logging.DEBUG)          

        logger.addHandler(handler)
        logger.addHandler(handler_d)
        logger.addHandler(handler_c)
        logger.setLevel(logging.DEBUG)
    else:
        logging.info(f'logger {logger} already has {len(logger.handlers)}')

    return logger

get_configured_logger()