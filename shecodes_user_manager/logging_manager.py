import logging
import sys
import logging.handlers
import os
import traceback


class LoggerException(Exception):
    pass


logger = None


def init_logger(log_file_name):
    global logger
    SCRIPT_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    logPath = os.path.join(SCRIPT_DIR_PATH, log_file_name)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.handlers.RotatingFileHandler(logPath, maxBytes=4 * 1024 * 1024, backupCount=5)
    formatter_info = logging.Formatter('%(asctime)s  %(levelname)s - %(message)s')
    file_handler.setFormatter(
        formatter_info)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter_info)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def log_error_with_stacktrace(error_message, end_program=False):
    global logger
    stacktrace_lines = '\n'.join([str(x) for x in traceback.extract_stack()][0:-1])
    logger.error(f"{error_message}:\n {stacktrace_lines}")
    if end_program:
        sys.exit(1)
