"""
Executes SAMoS with initial (particle) configuration parameter ranges/values.
Author: Konstantinos Andreadis
"""
import argparse
from scripts.communication_handler import print_log
from scripts.samos_handler import run_sweep

if __name__ == "__main__":
    print_log("=== Start ===")
    # Interpret arguments given by the user when this script is run
    parser = argparse.ArgumentParser()

    # Enable SAMoS execution. This is useful to first look at the result folder structure during debugging
    parser.add_argument("-path", "--group_folder", type=str, default="20231218", help="Group folder name?")

    # Enable tracker cells embedded within spheroid.
    parser.add_argument("-track", "--add_tracker_cells", type=bool, default=True, help="Add tracker cells to Spheroid?")
    parser.add_argument("-track_count", "--tracker_cell_count", type=int, default=50, help="Number of tracker cells?")

    # Conf file global parameter to replace @VAR variables
    parser.add_argument("-t", "--num_time_steps", type=int, default=20000, help="Number of time steps")
    parser.add_argument("-N", "--cell_count", type=int, default=500, help="Number of initial cells")

    parser.add_argument("-r", "--cell_radius", type=float, default=1.0, help="Mean cell radius")
    parser.add_argument("-rpoly", "--cell_radius_poly", type=float, default=0.3, help="Polydispersity of cell radius")
    parser.add_argument("-div", "--cell_division_rate", type=float, default=0.1, help="Division rate of a cell")
    parser.add_argument("-alpha", "--propulsion_alpha", type=float, default=0.1, help="External propulsion factor")
    parser.add_argument("-re", "--re_fact", type=float, default=1.15, help="Soft sphere potential factor")

    # Enable SAMoS execution. This is useful to first look at the result folder structure during debugging
    parser.add_argument("-enableSAMoS", "--enable_samos", type=bool, default=True, help="Enable SAMoS executable?")

    # First/only parameter to vary. v1 = None -> only global variables are used for a single run.
    parser.add_argument("-v1", "--var_1", type=str, default=None, help="Name of variable parameter 1?")
    parser.add_argument("-v1short", "--var_1_short", type=str, default=None, help="Tag of variable parameter 1?")
    parser.add_argument("-v1type", "--var_1_type", type=str, default="linear",
                        help="Range type of variable parameter 1?")
    parser.add_argument("-v1start", "--var_1_start", type=float, default=0.01,
                        help="Range start of variable parameter 1?")
    parser.add_argument("-v1end", "--var_1_end", type=float, default=0.1, help="Range end of variable parameter 1?")
    parser.add_argument("-v1num", "--var_1_num", type=int, default=5,
                        help="Range number of points of variable parameter 1?")

    # Second parameter to vary. v2 = None -> only previous parameter is varied.
    parser.add_argument("-v2", "--var_2", type=str, default=None, help="Name of variable parameter 2?")
    parser.add_argument("-v2short", "--var_2_short", type=str, default=None, help="Tag of variable parameter 2?")
    parser.add_argument("-v2type", "--var_2_type", type=str, default="linear",
                        help="Range type of variable parameter 2?")
    parser.add_argument("-v2start", "--var_2_start", type=float, default=0.01,
                        help="Range start of variable parameter 2?")
    parser.add_argument("-v2end", "--var_2_end", type=float, default=0.1, help="Range end of variable parameter 2?")
    parser.add_argument("-v2num", "--var_2_num", type=int, default=5,
                        help="Range number of points of variable parameter 2?")
    args = parser.parse_args()
    if args.add_tracker_cells:
        args.group_folder += "_trackers"

    # User input processing logic
    global_parameters = {}
    parameter_1D_sweep = {}
    parameter_2D_sweep = {}
    sweep_type = None
    for var in args.__dict__.keys():
        if var[:3] != "var":
            global_parameters[var] = args.__dict__[var]
        elif args.__dict__["var_1"] is None and args.__dict__["var_2"] is None:
            sweep_type = "0D"
        elif args.__dict__["var_1"] is not None and args.__dict__["var_2"] is None and var[:5] == "var_1":
            parameter_1D_sweep[var] = args.__dict__[var]
            sweep_type = "1D"
        elif args.__dict__["var_1"] is not None and args.__dict__["var_2"] is not None:
            parameter_2D_sweep[var] = args.__dict__[var]
            sweep_type = "2D"
    enable_samos_exec = global_parameters["enable_samos"]
    group_folder = global_parameters["group_folder"]
    # Execution of main samos handling script(s).
    run_sweep(sweep_type=sweep_type, global_parameters=global_parameters, parameter_1D_sweep=parameter_1D_sweep,
              parameter_2D_sweep=parameter_2D_sweep, enable_samos_exec=enable_samos_exec, group_folder=group_folder)
    print_log("=== End ===")
