"""
Visualisation and Analysis of SAMoS simulation results.
Author: Konstantinos Andreadis
"""
from paths_init import system_paths
from scripts.communication_handler import print_log, visualise_result_tree
from scripts.batch_analysis import analyse_root_subfolders
import argparse


def run_analysis():
    """
    For a set of variables all samos result folder(s) are analysed in batch.
    """
    print_log("=== Start ===")
    # For each variable: [short version of variable (str), label for plotting (str), type (float/int)]
    vars_select = {
        0: ["N", "initial cell count", int],
        1: ["t", "max time steps", int],
        2: ["div", "cell division rate", float],
        3: ["alpha", "propulsion alpha", float],
        4: ["re", "potential re factor", float],
        5: ["poly", "cell radius polydispersity", float],
        6: ["Ntrack", "track cell count", int],
    }
    # Interpret arguments given by the user when this script is run
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default="20240129_tracked", help="Result path to analyse")
    parser.add_argument("-dpi", "--dpi", type=int, default=300, help="Resolution dpi")
    args = parser.parse_args()
    # TODO User arguments for -p should be looped through
    folders_of_interests = [args.path]
    for folder in folders_of_interests:
        # Analyse all folders within the root path given by the user.
        analyse_root_subfolders(vars_select, folder, args.dpi)
        # Update result folder tree structure.
        visualise_result_tree(path=system_paths["output_figures_dir"], tree_type="analysis", show_subfolders=True)
    print_log("=== End ===")


if __name__ == "__main__":
    run_analysis()
