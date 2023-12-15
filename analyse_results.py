"""
Visualisation and Analysis of SAMoS simulation results.
Author: Konstantinos Andreadis
"""
from paths_init import system_paths
from scripts.communication_handler import print_log, visualise_result_tree
from scripts.batch_analysis import analyse_root_subfolders
import argparse

if __name__ == "__main__":
    print_log("=== Start ===")
    vars_select = {  # folder short version of variable, label for plotting, type (float/int)
        0: ["N", "initial cell count", int],
        1: ["t", "# time steps", int],
        2: ["div", "cell division rate", float],
        3: ["alpha", "propulsion alpha", float],
        4: ["re", "potential re factor", float],
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default="20231215_queue", help="Result path to analyse")
    parser.add_argument("-dpi", "--dpi", type=int, default=100, help="Resolution dpi")
    args = parser.parse_args()
    folders_of_interests = [args.path]
    for folder in folders_of_interests:
        analyse_root_subfolders(vars_select, folder, args.dpi)
        visualise_result_tree(path=system_paths["output_figures_dir"], tree_type="analysis")
    print_log("=== End ===")
