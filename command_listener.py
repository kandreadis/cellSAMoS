"""
Listens to new run commands from a shared Dropbox folder to enable remote access to the simulation.
Author: Konstantinos Andreadis
"""
import os, shutil

from paths_init import system_paths
from scripts.communication_handler import print_portstatus
import subprocess


def open_listen_port():
    """
    Listens for new added commands (bash files), executes them, and communicates results live.
    ! This is a never-ending while loop.
    """
    while True:
        # TODO add feature to cancel active task(s) remotely!
        listen_path = system_paths["listen_dir"]
        completed_tasks_path = system_paths["completed_tasks_dir"]
        bash_tasks = [f for f in os.listdir(listen_path) if f.endswith(".sh")]
        print(f"---------- Found task {bash_tasks} in {listen_path} ----------")
        for task in bash_tasks:
            task_path = os.path.join(listen_path, task)
            print_portstatus(f"=> Executing task {task}...")
            with open(task_path, 'rb') as bash_script:
                script = bash_script.read()
            subprocess.call(script, shell=True)
            shutil.move(task_path, os.path.join(completed_tasks_path,task))
            print_portstatus(f"! Completed task {task}, moving script to /completed_tasks ...")


if __name__ == "__main__":
    open_listen_port()
