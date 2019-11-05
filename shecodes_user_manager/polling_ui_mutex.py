import os
import time

FILE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "polling_ui_mutex.lock")

class PollingUiMutex(object):

    def __init__(self, name):
        self._name = name

    def __enter__(self):
        while os.path.exists(FILE_NAME):
            with open(FILE_NAME, "rb") as fp:
                if self._name in fp.readline().decode("utf-8"):
                    break
            time.sleep(0.1)
        with open(FILE_NAME, "wb") as fp:
            fp.write(self._name.encode("utf-8"))

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.unlink(FILE_NAME)
