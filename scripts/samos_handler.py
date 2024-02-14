"""
Handler for all samos executions.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""
import os, re
from datetime import datetime as date
import numpy as np

import samos_init.initialise_cells as init_cells
from paths_init import system_paths
from scripts.communication_handler import print_log, visualise_result_tree


def run_simulation(params, group_folder, session, naming_conv, run_samos=True):
    """
    For a dictionary of parameters (see run_samos.py), samos is executed within a folder named according to naming_conv
    inside the folder session.
    """
    # Import user system paths from paths_init.py
    samos_dir = system_paths["samos_dir"]
    if params["add_tracker_cells"]:
        configuration_file = system_paths["conf_file_trackers"]
    elif params["plane"]:
        if params["plane_abp"]:
            configuration_file = system_paths["conf_file_plane_abp"]
        else:
            configuration_file = system_paths["conf_file_plane"]
    else:
        configuration_file = system_paths["conf_file"]
    intialisation_file = system_paths["init_particles_file"]
    result_root_dir = system_paths["output_samos_dir"]

    params["cell_count"] = int(params["cell_count"])
    # The result path is initialised
    result_dir = os.path.join(result_root_dir, group_folder, session, naming_conv)
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
        configuration = re.sub("@DIVRATE", str(params["cell_division_rate"]), configuration)
        configuration = re.sub("@V0", str(params["v0"]), configuration)
        configuration = re.sub("@NUMTIMESTEPS", str(params["num_time_steps"]), configuration)
        configuration = re.sub("@REFACT", str(params["re_fact"]), configuration)
        configuration = re.sub("@POLY", str(params["cell_radius_poly"]), configuration)

        configuration = re.sub("@SEED", str(params["seed"]), configuration)
        configuration = re.sub("@Dr", str(params["Dr"]), configuration)
        configuration = re.sub("@L", str(params["L"]), configuration)
        configuration = re.sub("@FREQDAT", str(params["freq_dat"]), configuration)
        configuration = re.sub("@FREQVTP", str(params["freq_vtp"]), configuration)
        configuration = re.sub("@TIMESTEP", str(params["dt"]), configuration)
        conf_file.seek(0)
        conf_file.write(configuration)
        conf_file.truncate()

    # Executes Python script to initialise particles and save to the result folder
    if params["plane"]:
        collective = init_cells.Plane(L=params["L"], phi=params["phi"], cell_radius=params["cell_radius"],
                                      poly=params["cell_radius_poly"])
    else:
        collective = init_cells.Spheroid(cell_radius=params["cell_radius"], cell_count=params["cell_count"],
                                         poly=params["cell_radius_poly"], add_tracker_cells=params["add_tracker_cells"],
                                         tracker_cell_count=params["tracker_cell_count"])
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
    visualise_result_tree(path=system_paths["output_samos_dir"], tree_type="output")


def run_sweep(sweep_type, global_parameters, parameter_1D_sweep, parameter_2D_sweep, enable_samos_exec, group_folder,
              debug):
    """
    This multi-dimensional sweeping handler operates in 3 sweep_types: Single value, 1 parameter range and 2 parameter
    ranges. In the first case, the global_parameters are used.
    """
    if sweep_type == "0D":
        print_log("!! Running single simulation without sweep")
        param_pair_label = "t-{}_N-{}_{}-{}_{}-{}_{}-{}".format(
            global_parameters["num_time_steps"], global_parameters["cell_count"],
            "div", global_parameters["cell_division_rate"], "v0", global_parameters["v0"],
            "re", global_parameters["re_fact"])
        if global_parameters["add_tracker_cells"]:
            param_pair_label += "_track-{}".format(global_parameters["tracker_cell_count"])

        if global_parameters["plane"]:
            param_pair_label = "t-{}_L-{}_re-{}_phi-{}_v0-{}_Dr-{}".format(global_parameters["num_time_steps"],
                                                                           global_parameters["L"],
                                                                           global_parameters["re_fact"],
                                                                           global_parameters["phi"],
                                                                           global_parameters["v0"],
                                                                           global_parameters["Dr"])

        session_label = f"{param_pair_label}_{date.now().strftime('dump%H%M%S')}"
        if debug:
            session_label = "debug"
            param_pair_label = "debug"
        run_simulation(params=global_parameters, group_folder=group_folder, session=session_label,
                       naming_conv=param_pair_label, run_samos=enable_samos_exec)

    if sweep_type == "1D":
        session_label = "{}_{}_{}-{}_#{}".format(parameter_1D_sweep["var_1_short"], parameter_1D_sweep["var_1_type"],
                                                 parameter_1D_sweep["var_1_start"], parameter_1D_sweep["var_1_end"],
                                                 parameter_1D_sweep["var_1_num"])
        var_1_range = None
        if parameter_1D_sweep["var_1_type"] == "log":
            var_1_range = np.logspace(np.log10(parameter_1D_sweep["var_1_start"]),
                                      np.log10(parameter_1D_sweep["var_1_end"]), parameter_1D_sweep["var_1_num"])
        if parameter_1D_sweep["var_1_type"] == "linear":
            var_1_range = np.linspace(parameter_1D_sweep["var_1_start"], parameter_1D_sweep["var_1_end"],
                                      parameter_1D_sweep["var_1_num"])
        var_1_range = np.round(var_1_range, 5)
        print_log(f"!! Starting 1D parameter sweep for a total of {len(var_1_range)} parameter values...")
        i_progress = 0
        for var1_idx, var1 in enumerate(var_1_range):
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
                param_pair_label = "t-{}_{}-{}".format(global_parameters["num_time_steps"],
                                                       parameter_1D_sweep["var_1_short"], var1)
            if global_parameters["plane"]:
                param_pair_label = "t-{}_L-{}_re-{}_phi-{}_{}-{}".format(global_parameters["num_time_steps"],
                                                                         global_parameters["L"],
                                                                         global_parameters["re_fact"],
                                                                         global_parameters["phi"],
                                                                         parameter_1D_sweep["var_1_short"], var1)
            run_simulation(params=global_parameters, group_folder=group_folder, session=session_label,
                           naming_conv=param_pair_label, run_samos=enable_samos_exec)

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
                                      np.log10(parameter_2D_sweep["var_1_end"]),
                                      parameter_2D_sweep["var_1_num"])
        if parameter_2D_sweep["var_1_type"] == "linear":
            var_1_range = np.linspace(parameter_2D_sweep["var_1_start"], parameter_2D_sweep["var_1_end"],
                                      parameter_2D_sweep["var_1_num"])
        if parameter_2D_sweep["var_2_type"] == "log":
            var_2_range = np.logspace(np.log10(parameter_2D_sweep["var_2_start"]),
                                      np.log10(parameter_2D_sweep["var_2_end"]),
                                      parameter_2D_sweep["var_2_num"])
        if parameter_2D_sweep["var_2_type"] == "linear":
            var_2_range = np.linspace(parameter_2D_sweep["var_2_start"], parameter_2D_sweep["var_2_end"],
                                      parameter_2D_sweep["var_2_num"])
        var_1_range = np.round(var_1_range, 5)
        var_2_range = np.round(var_2_range, 5)
        print_log(
            f"!! Starting 2D parameter sweep for a total of {len(var_1_range) * len(var_2_range)} parameter pairs...")
        i_progress = 0
        for var1_idx, var1 in enumerate(var_1_range):
            for var2_idx, var2 in enumerate(var_2_range):
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
                if global_parameters["plane"]:
                    param_pair_label = "t-{}_L-{}_re-{}_phi-{}_{}-{}_{}-{}".format(global_parameters["num_time_steps"],
                                                                                   global_parameters["L"],
                                                                                   global_parameters["re_fact"],
                                                                                   global_parameters["phi"],
                                                                                   parameter_2D_sweep["var_1_short"],
                                                                                   var1,
                                                                                   parameter_2D_sweep["var_2_short"],
                                                                                   var2)
                run_simulation(params=global_parameters, group_folder=group_folder, session=session_label,
                               naming_conv=param_pair_label, run_samos=enable_samos_exec)
