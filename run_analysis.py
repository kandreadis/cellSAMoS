"""
Visualisation and Analysis of SAMoS simulation results.
Author: Konstantinos Andreadis
"""
from paths_init import system_paths
from scripts.communication_handler import print_log
from scripts.batch_analysis import analyse_root_subfolders
import argparse


def run_analysis():
    """
    For a set of variables all samos result folder(s) are analysed in batch.
    """
    print_log("=== Start ===")
    # For each variable: [short version of variable (str), label for plotting (str), type (float/int)]
    vars_select = {
        "Nframes": ["number of frames", int],
        "Ncell": ["initial cell count", int],
        "L": ["box dimension L", float],
        "phiecm": ["ECM packing fraction phi", float],
        "kce": ["stiffness cell-ECM kce", float],
        "divcell": ["cell division rate", float],
        "v0": ["propulsion v0", float],
        "Ntrack": ["track cell count", int],
        "Dr": ["rotational diffusion Dr", float],
        "re": ["potential re factor", float],
        "Ntrack": ["track cell count", int]
    }
    # Interpret arguments given by the user when this script is run
    parser = argparse.ArgumentParser()
    parser.add_argument("p", type=str, help="Result path(s) to analyse", nargs='*')
    parser.add_argument("-dpi", type=int, default=300, help="Resolution dpi")
    parser.add_argument("-dt", type=float, default=0.01, help="Time step dt")
    parser.add_argument("-freq", type=float, default=1000, help="Sampling frequency")
    parser.add_argument("-analyse", action="store_true", help="Run analysis (again)?")
    parser.add_argument("-visualise", action="store_true", help="Visualise results?")
    parser.add_argument("-show", action="store_true", help="Show results?")
    parser.add_argument("-debug", action="store_true", help="Debug?")

    parser.add_argument("-dat_iter_debug", type=int, default=None, help="Number of cores to run on in parallel?")
    parser.add_argument("-idx_iter_debug", type=int, default=None, help="Number of cores to run on in parallel?")

    parser.add_argument("-type_analysis", type=str, default="tumoroid", help="Type of analysis? (tumoroid/plane")
    parser.add_argument("-Ncores", type=int, default=8, help="Number of cores to run on in parallel?")
    args = parser.parse_args()

    # Execute Analysis
    folders_of_interests = args.p
    if len(folders_of_interests) > 0:
        print_log(f"Number of root folders = {len(folders_of_interests)}")
        analyse_root_subfolders(folders_of_interests=folders_of_interests, args=args, vars_select=vars_select)
    else:
        print_log("No root folder name was given!")
    print_log("=== End ===")


if __name__ == "__main__":
    run_analysis()
