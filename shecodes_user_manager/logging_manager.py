import logging
import sys
import logging.handlers
import os


class LoggerException(Exception):
    pass


logger = None


def init_logger(process_name):
    global logger
    SCRIPT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    logPath = os.path.join(SCRIPT_DIR_PATH, f"shecodes_user_manager_{process_name}.log")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.handlers.RotatingFileHandler(logPath, maxBytes=4 * 1024 * 1024, backupCount=5)
    formatter_info =  logging.Formatter('%(asctime)s  %(levelname)s - %(message)s')
    file_handler.setFormatter(
        formatter_info)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter_info)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


