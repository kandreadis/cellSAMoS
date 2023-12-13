"""
Collection of independent functions that perform all internal / external (user) communication. 
Author: Konstantinos Andreadis
"""

import os, datetime

from paths_init import system_paths


def print_log(message):
    log = f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}] {message}\n"
    progress_msg_file = os.path.join(system_paths["log_file"])
    with open(progress_msg_file, "a") as f:
        f.write(log)
        f.close()
    print(message)
