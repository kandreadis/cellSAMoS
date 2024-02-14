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
        3: ["v0", "propulsion v0", float],
        4: ["re", "potential re factor", float],
        5: ["poly", "cell radius polydispersity", float],
        6: ["Ntrack", "track cell count", int],
        7: ["L", "box dimension L", float],
        8: ["phi", "packing fraction phi", float],
        9: ["Dr", "rotational diffusion Dr", float],
    }
    # Interpret arguments given by the user when this script is run
    parser = argparse.ArgumentParser()
    default_folder = "20240208_ABP_no-poly_L-100.0_phi-1.0_re-1.0_Dr-0.1"
    parser.add_argument("-p", "--p", type=str, default=[default_folder],
                        help="Result path(s) to analyse", nargs='*')
    parser.add_argument("-dpi", "--dpi", type=int, default=300, help="Resolution dpi")
    parser.add_argument("-dt", "--dt", type=float, default=0.01, help="Time step dt")
    parser.add_argument("-freq", "--freq", type=float, default=1000, help="Sampling frequency")
    parser.add_argument("-analyse", "--analyse", action="store_true", help="Run analysis (again)?")
    parser.add_argument("-visualise", "--visualise", action="store_true", help="Visualise results?")
    parser.add_argument("-show", "--show", action="store_true", help="Show results?")
    parser.add_argument("-debug", "--debug", action="store_true", help="Debug?")
    parser.add_argument("-type_analysis", "--type_analysis", type=str, default="plane",
                        help="Type of analysis? (tumoroid/plane")
    args = parser.parse_args()
    folders_of_interests = args.p
    print("Number of root folders =", len(folders_of_interests))
    for folder in folders_of_interests:
        # Analyse all folders within the root path given by the user.
        analyse_root_subfolders(analyse=args.analyse, visualise=args.visualise, vars_select=vars_select,
                                result_folder=folder, dpi=args.dpi, debug=args.debug,
                                dt=args.dt, freq=args.freq, show=args.show, type_analysis=args.type_analysis)
        # Update result folder tree structure.
        visualise_result_tree(path=system_paths["output_figures_dir"], tree_type="analysis", show_subfolders=True)
    print_log("=== End ===")


if __name__ == "__main__":
    run_analysis()
