"""
Collection of independent functions that perform all internal / external (user) communication.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import os, datetime

from paths_init import system_paths


def print_log(message):
    """
    Print and log a string message at the same time.
    """
    log = f"[{datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}] {message}\n"
    progress_msg_file = os.path.join(system_paths["log_file"])
    with open(progress_msg_file, "a") as f:
        f.write(log)
        f.close()
    print(message)


def print_dirstatus(message, tree_type):
    """
    Save last known folder structure to a file.
    """
    if tree_type == "output":
        dirstatus_file = os.path.join(system_paths["output_dirstatus_file"])
    else:
        dirstatus_file = os.path.join(system_paths["analysis_dirstatus_file"])
    with open(dirstatus_file, "w") as f:
        for msg in message:
            f.write(msg + "\n")
        f.close()


def visualise_result_tree(path, tree_type, show_subfolders=False):
    """
    Visualise folder tree structure within a path directory and save it to a file.
    """
    tree = ["== START Directory tree of {} ==".format(path)]
    for folders in os.listdir(path):
        tree.append(f"{folders}")
        for folder in os.listdir(os.path.join(path, folders)):
            try:
                subfolders = os.listdir(os.path.join(path, folders, folder))
                if show_subfolders:
                    for subfolder in subfolders:
                        tree.append(f"-- {folder} / {subfolder}")
                else:
                    example_subfolder = subfolders[0]
                    tree.append(f"-- {folder} / {example_subfolder} ...")

            except:
                pass
                tree.append(f"-- {folder}")

    tree.append("== END Directory tree of {} ==".format(path))
    print_dirstatus(tree, tree_type=tree_type)
