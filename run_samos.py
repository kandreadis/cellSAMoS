"""
Executes SAMoS with initial (particle) configuration parameter ranges/values.
Author: Konstantinos Andreadis
"""
import argparse
from scripts.communication_handler import print_log
from scripts.samos_handler import run_sweep

if __name__ == "__main__":
    print_log("=== Start ===")

    parameter_1D_re = {
        "var_1": "re_fact",
        "var_1_short": "re",
        "var_1_type": "linear",  # "log"
        "var_1_start": 1,
        "var_1_end": 1.2,
        "var_1_num": 20,
    }
    parameter_1D_N = {
        "var_1": "cell_count",
        "var_1_short": "N",
        "var_1_type": "linear",  # "log"
        "var_1_start": 1,
        "var_1_end": 1000,
        "var_1_num": 5,
    }
    parameter_2D_div_alpha = {
        "var_1": "cell_division_rate",
        "var_1_short": "div",
        "var_1_type": "linear",  # "linear"
        "var_1_start": 0.01,
        "var_1_end": 0.1,
        "var_1_num": 10,
        "var_2": "propulsion_alpha",
        "var_2_short": "alpha",
        "var_2_type": "linear",  # "log"
        "var_2_start": 0.01,
        "var_2_end": 0.1,
        "var_2_num": 10
    }
    parameter_2D_re_alpha = {
        "var_1": "re_fact",
        "var_1_short": "re",
        "var_1_type": "linear",  # "log"
        "var_1_start": 1,
        "var_1_end": 1.2,
        "var_1_num": 5,
        "var_2": "propulsion_alpha",
        "var_2_short": "alpha",
        "var_2_type": "linear",  # "log"
        "var_2_start": 0.01,
        "var_2_end": 1,
        "var_2_num": 10
    }
    parameter_2D_re_div = {
        "var_1": "re_fact",
        "var_1_short": "re",
        "var_1_type": "linear",  # "log"
        "var_1_start": 1,
        "var_1_end": 1.2,
        "var_1_num": 5,
        "var_2": "cell_division_rate",
        "var_2_short": "div",
        "var_2_type": "linear",  # "log"
        "var_2_start": 0.01,
        "var_2_end": 1,
        "var_2_num": 10
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--num_time_steps", type=int, default=10000, help="Number of time steps")
    parser.add_argument("-N", "--cell_count", type=int, default=500, help="Number of initial cells")
    parser.add_argument("-R", "--spheroid_radius", type=float, default=8.735, help="Radius of initial spheroid")
    parser.add_argument("-r", "--cell_radius", type=float, default=1.0, help="Mean cell radius")
    parser.add_argument("-rpoly", "--cell_radius_poly", type=float, default=0.3, help="Polydispersity of cell radius")
    parser.add_argument("-div", "--cell_division_rate", type=float, default=0.1, help="Division rate of a cell")
    parser.add_argument("-alpha", "--propulsion_alpha", type=float, default=0.1, help="External propulsion factor")
    parser.add_argument("-re", "--re_fact", type=float, default=1.15, help="Soft sphere potential factor")

    parser.add_argument("-enableSAMoS", "--enable_samos", type=bool, default=True, help="Enable SAMoS executable?")

    parser.add_argument("-v1", "--var_1", type=str, default=None, help="Name of variable parameter 1?")
    parser.add_argument("-v1short", "--var_1_short", type=str, default=None, help="Tag of variable parameter 1?")
    parser.add_argument("-v1type", "--var_1_type", type=str, default="linear",
                        help="Range type of variable parameter 1?")
    parser.add_argument("-v1start", "--var_1_start", type=float, default=0.01,
                        help="Range start of variable parameter 1?")
    parser.add_argument("-v1end", "--var_1_end", type=float, default=0.1, help="Range end of variable parameter 1?")
    parser.add_argument("-v1num", "--var_1_num", type=int, default=5,
                        help="Range number of points of variable parameter 1?")

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
    global_parameters = {}
    parameter_1D_sweep = {}
    parameter_2D_sweep = {}
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
    run_sweep(sweep_type=sweep_type, global_parameters=global_parameters, parameter_1D_sweep=parameter_1D_sweep,
              parameter_2D_sweep=parameter_2D_sweep, enable_samos_exec=enable_samos_exec)
    print_log("=== End ===")
