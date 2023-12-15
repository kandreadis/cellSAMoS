"""
Listens to new run commands from a shared Dropbox folder to enable remote access to the simulation.
Author: Konstantinos Andreadis
"""
import os

from paths_init import system_paths
from scripts.communication_handler import print_log
import subprocess

if __name__ == "__main__":
    completed_tasks = []
    while True:
        listen_path = system_paths["listen_dir"]
        bash_tasks = [os.path.join(listen_path, f) for f in os.listdir(listen_path) if f.endswith(".sh")]
        print(f"---------- Found task {bash_tasks} in {listen_path} ----------")
        for task in bash_tasks:
            if not (task in completed_tasks):
                print_log(f"=> Executing task {task}...")
                with open(task, 'rb') as file:
                    script = file.read()
                subprocess.call(script, shell=True)
                completed_tasks.append(task)
        print(f"Completed tasks: {completed_tasks}")