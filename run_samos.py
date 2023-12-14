"""
Executes SAMoS with initial (particle) configuration parameter ranges/values.
Author: Konstantinos Andreadis
"""
import argparse
from scripts.communication_handler import print_log
from scripts.samos_handler import run_sweep

global_parameters = {
    "num_time_steps": 20000,
    "cell_count": 500,
    "spheroid_radius": 8.735,
    "cell_radius": 1.0,
    "cell_radius_poly": 0.3,
    "cell_division_rate": 0.1,
    "propulsion_alpha": 0.15,
    "re_fact": 1.15,
    "plot_config": False
}
parameter_1D_re = {
    "var_1": "re_fact",
    "var_1_short": "re",
    "var_1_type": "linear",  # "log"
    "var_1_start": 1,
    "var_1_end": 1.2,
    "var_1_num": 40,
}
parameter_1D_re_confined = {
    "var_1": "re_fact",
    "var_1_short": "re",
    "var_1_type": "linear",  # "log"
    "var_1_start": 1.1,
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
    "var_1_end": 1,
    "var_1_num": 10,
    "var_2": "propulsion_alpha",
    "var_2_short": "alpha",
    "var_2_type": "linear",  # "log"
    "var_2_start": 0.01,
    "var_2_end": 1,
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

parameter_selection = {
    "0D": global_parameters,
    "1D_re": parameter_1D_re,
    "1D_N": parameter_1D_N,
    "2D_div_alpha": parameter_2D_div_alpha,
    "2D_re_alpha": parameter_2D_re_alpha,
    "2D_re_div": parameter_2D_re_div
}

enable_samos_exec = True

if __name__ == "__main__":
    print_log("=== Start ===")
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--option", type=str, default="1D_re", help="parameter (sweep) task")
    args = parser.parse_args()
    sweep_task = args.option
    sweep_type = sweep_task[:2]
    parameter_1D_sweep = parameter_selection[sweep_task]
    parameter_2D_sweep = parameter_selection[sweep_task]

    run_sweep(sweep_type=sweep_type, global_parameters=global_parameters, parameter_1D_sweep=parameter_1D_sweep,
              parameter_2D_sweep=parameter_2D_sweep, enable_samos_exec=enable_samos_exec)

    print_log("=== End ===")
