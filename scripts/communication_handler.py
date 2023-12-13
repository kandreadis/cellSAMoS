"""
Collection of independent functions that perform all internal / external (user) communication. 
Author: Konstantinos Andreadis
"""

import os, datetime, sys


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        root_dir = os.getcwd()
        progress_msg_file = os.path.join(root_dir, "Dropbox", "cellsim.log")
        self.log = open(progress_msg_file, "a")

    def write(self, message):
        self.terminal.write(message)
        message = message.replace("\n", " ")
        msg = f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}] {message}"

        self.log.write(msg)
        self.log.write("\n")

    def flush(self):
        pass
