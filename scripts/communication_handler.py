"""
Collection of independent functions that perform all internal / external (user) communication. 
Author: Konstantinos Andreadis
"""

import os, datetime


def print_log(message):
    root_dir = "/data1/andreadis/CellSim"
    log = f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}] {message}\n"
    progress_msg_file = os.path.join(root_dir, "cellsim.log")
    with open(progress_msg_file, "a") as f:
        f.write(log)
        f.close()
    print(message)
