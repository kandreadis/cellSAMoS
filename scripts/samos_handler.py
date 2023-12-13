"""
Handler for all samos executions.
Author: Konstantinos Andreadis
"""
import os, re
from datetime import datetime as date
import numpy as np

import samos_init.initialise_cells as init_cells
from paths_init import system_paths
from scripts.communication_handler import print_log

# Specify the path to the samos executable
samos_dir = system_paths["samos_dir"]

# Specify the path to the Python and configuration script inside "CellSim"
configuration_file = system_paths["conf_file"]
intialisation_file = system_paths["init_particles_file"]
result_root_dir = system_paths["output_samos_dir"]


def run_simulation(parameters_dict, session, naming_conv, run_samos=True):
    parameters_dict["cell_count"] = int(parameters_dict["cell_count"])
    # The result path is initialised with a datestamp inside "samos_output"
    result_dir = os.path.join(result_root_dir, date.today().strftime("%Y%m%d")+"_queue", session, naming_conv)
    try:
        os.makedirs(result_dir)
    except:
        print_log("Result directory already exists, overwriting...")

    # Creates path for copied configuration file
    new_configuration_dir = os.path.join(result_dir, "configuration.conf")
    # Creates path for copied initialisation script
    new_initialisation_dir = os.path.join(result_dir, "initialisation.py")
    # Creates path for copied initial particle group(s)
    new_particles_dir = os.path.join(result_dir, "particles.txt")
    try:
        # Copies configuration file to results folder.
        os.system(f"cp {configuration_file} {new_configuration_dir}")
        # Copies initialisation Python script to results folder.
        os.system(f"cp {intialisation_file} {new_initialisation_dir}")
    except:
        print_log("Could not copy file to result directory...")

    with open(new_configuration_dir, "r+") as conf_file:
        configuration = conf_file.read()
        configuration = re.sub("@DIVRATE", str(parameters_dict["cell_division_rate"]), configuration)
        configuration = re.sub("@ALPHA", str(parameters_dict["propulsion_alpha"]), configuration)
        configuration = re.sub("@NUMTIMESTEPS", str(parameters_dict["num_time_steps"]), configuration)
        configuration = re.sub("@REFACT", str(parameters_dict["re_fact"]), configuration)
        conf_file.seek(0)
        conf_file.write(configuration)
        conf_file.truncate()

    # Executes Python script to initialise particles and save to the result folder
    collective = init_cells.Spheroid(spheroid_radius=parameters_dict["spheroid_radius"],
                                     cell_radius=parameters_dict["cell_radius"],
                                     cell_count=parameters_dict["cell_count"], poly=parameters_dict["cell_radius_poly"])
    init_cells.save_initial_cells(collective.cells, new_particles_dir)

    # Finally, moves to the result folder and executes SAMoS using the configuration file.
    try:
        os.chdir(result_dir)
    except:
        print_log("Could not move to result directory...")

    if run_samos:
        try:
            print_log("Executing SAMoS...")
            os.system(f"{samos_dir} {new_configuration_dir}")
        except:
            print_log("Could not locate SAMoS executable...")
    print_log(f"Finished! Location of results: {result_dir}")


def run_sweep(sweep_type, global_parameters, parameter_1D_sweep, parameter_2D_sweep, enable_samos_exec):
    if sweep_type == "0D":
        print_log("!! Running single simulation without sweep")
        param_pair_label = "t-{}_N-{}_{}-{}_{}-{}_{}-{}".format(global_parameters["num_time_steps"],
                                                                global_parameters["cell_count"], "div",
                                                                global_parameters["cell_division_rate"], "alpha",
                                                                global_parameters["propulsion_alpha"], "re",
                                                                global_parameters["re_fact"])
        session_label = f"0D_{date.now().strftime('%Y%m%d_%H-%M')}"
        run_simulation(parameters_dict=global_parameters, session=session_label, naming_conv=param_pair_label,
                       run_samos=enable_samos_exec)

    if sweep_type == "1D":
        session_label = "{}_{}_{}-{}_#{}".format(parameter_1D_sweep["var_1_short"], parameter_1D_sweep["var_1_type"],
                                                 parameter_1D_sweep["var_1_start"], parameter_1D_sweep["var_1_end"],
                                                 parameter_1D_sweep["var_1_num"])
        var_1_range = None
        if parameter_1D_sweep["var_1_type"] == "log":
            var_1_range = np.logspace(np.log10(parameter_1D_sweep["var_1_start"]),
                                      np.log(parameter_1D_sweep["var_1_end"]),
                                      parameter_1D_sweep["var_1_num"])
        if parameter_1D_sweep["var_1_type"] == "linear":
            var_1_range = np.linspace(parameter_1D_sweep["var_1_start"], parameter_1D_sweep["var_1_end"],
                                      parameter_1D_sweep["var_1_num"])
        var_1_range = np.round(var_1_range, 5)
        print_log(f"!! Starting 1D parameter sweep for a total of {len(var_1_range)} parameter values...")
        i_progress = 0
        for div_idx, var1 in enumerate(var_1_range):
            i_progress += 1
            progress = f"{round(100 * i_progress / (len(var_1_range)))} %"
            status = "{} {}".format(parameter_1D_sweep["var_1"], var1)
            progress_msg = f"[{progress}] --- {status} ---"
            print_log(progress_msg)
            global_parameters[parameter_1D_sweep["var_1"]] = var1
            param_pair_label = "t-{}_N-{}_{}-{}".format(global_parameters["num_time_steps"],
                                                        global_parameters["cell_count"],
                                                        parameter_1D_sweep["var_1_short"], var1)
            if parameter_1D_sweep["var_1_short"] == "N":
                global_parameters["spheroid_radius"] = int((var1 / 0.74) ** (1 / 3) * global_parameters["cell_radius"])
                param_pair_label = "t-{}_{}-{}".format(global_parameters["num_time_steps"],
                                                       parameter_1D_sweep["var_1_short"],
                                                       var1)
            run_simulation(parameters_dict=global_parameters, session=session_label, naming_conv=param_pair_label,
                           run_samos=enable_samos_exec)

    if sweep_type == "2D":
        session_label = "{}_{}_{}-{}_#{}_vs_{}_{}_{}-{}_#{}".format(parameter_2D_sweep["var_1_short"],
                                                                    parameter_2D_sweep["var_1_type"],
                                                                    parameter_2D_sweep["var_1_start"],
                                                                    parameter_2D_sweep["var_1_end"],
                                                                    parameter_2D_sweep["var_1_num"],
                                                                    parameter_2D_sweep["var_2_short"],
                                                                    parameter_2D_sweep["var_2_type"],
                                                                    parameter_2D_sweep["var_2_start"],
                                                                    parameter_2D_sweep["var_2_end"],
                                                                    parameter_2D_sweep["var_2_num"])
        var_1_range, var_2_range = None, None
        if parameter_2D_sweep["var_1_type"] == "log":
            var_1_range = np.logspace(np.log10(parameter_2D_sweep["var_1_start"]),
                                      np.log(parameter_2D_sweep["var_1_end"]),
                                      parameter_2D_sweep["var_1_num"])
        if parameter_2D_sweep["var_1_type"] == "linear":
            var_1_range = np.linspace(parameter_2D_sweep["var_1_start"], parameter_2D_sweep["var_1_end"],
                                      parameter_2D_sweep["var_1_num"])
        if parameter_2D_sweep["var_2_type"] == "log":
            var_2_range = np.logspace(np.log10(parameter_2D_sweep["var_2_start"]),
                                      np.log(parameter_2D_sweep["var_2_end"]),
                                      parameter_2D_sweep["var_2_num"])
        if parameter_2D_sweep["var_2_type"] == "linear":
            var_2_range = np.linspace(parameter_2D_sweep["var_2_start"], parameter_2D_sweep["var_2_end"],
                                      parameter_2D_sweep["var_2_num"])
        var_1_range = np.round(var_1_range, 5)
        var_2_range = np.round(var_2_range, 5)
        print_log(
            f"!! Starting 2D parameter sweep for a total of {len(var_1_range) * len(var_2_range)} parameter pairs...")
        i_progress = 0
        for div_idx, var1 in enumerate(var_1_range):
            for alpha_idx, var2 in enumerate(var_2_range):
                i_progress += 1
                progress = f"{round(100 * i_progress / (len(var_1_range) * len(var_2_range)))} %"
                status = "{} {} {} {}".format(parameter_2D_sweep["var_1"], var1, parameter_2D_sweep["var_2"], var2)
                progress_msg = f"[{progress}] --- {status} ---"
                print_log(progress_msg)
                global_parameters[parameter_2D_sweep["var_1"]] = var1
                global_parameters[parameter_2D_sweep["var_2"]] = var2
                param_pair_label = "t-{}_N-{}_{}-{}_{}-{}".format(global_parameters["num_time_steps"],
                                                                  global_parameters["cell_count"],
                                                                  parameter_2D_sweep["var_1_short"], var1,
                                                                  parameter_2D_sweep["var_2_short"], var2)
                run_simulation(parameters_dict=global_parameters, session=session_label, naming_conv=param_pair_label,
                               run_samos=enable_samos_exec)
