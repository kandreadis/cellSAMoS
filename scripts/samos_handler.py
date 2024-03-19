"""
Handler for all samos executions.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""
import os, re
from datetime import datetime as date
import numpy as np
import samos_init.initialise_cells as init_cells
import samos_init.initialise_tumoroid_ECM as init_tumoroid_ecm
from paths_init import system_paths
from scripts.communication_handler import print_log, visualise_result_tree, create_samos_folder_name
from scripts.data_handler import save_dict
import multiprocessing
import copy


def run_simulation(params, group_folder, session, naming_conv, run_samos=True):
    """
    For a dictionary of parameters (see run_samos.py), samos is executed within a folder named according to naming_conv
    inside the folder session.
    """
    # Import user system paths from paths_init.py
    samos_dir = system_paths["samos_dir"]
    if params["track"]:
        configuration_file = system_paths["conf_file_trackers"]
    elif params["tumoroid_ecm"]:
        configuration_file = system_paths["conf_file_tumoroid_ecm"]
    elif params["plane"]:
        if params["plane_abp"]:
            configuration_file = system_paths["conf_file_plane_abp"]
        else:
            configuration_file = system_paths["conf_file_plane"]
    else:
        configuration_file = system_paths["conf_file"]

    intialisation_file = system_paths["init_particles_file"]
    if params["tumoroid_ecm"]: intialisation_file = system_paths["init_tumoroid_ecm_file"]
    result_root_dir = system_paths["output_samos_dir"]

    params["Ncell"] = int(params["Ncell"])
    # The result path is initialised
    session_dir = os.path.join(result_root_dir, group_folder, session)
    result_dir = os.path.join(session_dir, naming_conv)
    try:
        os.makedirs(result_dir)
    except:
        print_log("Result directory already exists, overwriting...")
    save_dict(dict=params, path=session_dir)
    save_dict(dict=params, path=result_dir)
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

        for varname in params.keys():
            configuration = re.sub("@" + varname, str(params[varname]), configuration)

        conf_file.seek(0)
        conf_file.write(configuration)
        conf_file.truncate()
    # Executes Python script to initialise particles and save to the result folder
    if params["plane"]:
        collective = init_cells.Plane(L=params["L"], phi=params["phi"], cell_radius=params["cell_radius"],
                                      poly=params["cell_radius_poly"])
        init_cells.save_initial_cells(collective.cells, new_particles_dir)
    elif params["tumoroid_ecm"]:
        all_particles = init_tumoroid_ecm.Spheroid(cell_N=params["Ncell"], cell_radius=params["rcell"],
                                                   cell_poly=params["polycell"],
                                                   ecm_phi=params["phiecm"], ecm_radius=params["recm"],
                                                   ecm_poly=params["polyecm"], ecm_size=params["L"]).cells
        init_tumoroid_ecm.save_initial_cells(cells_data=all_particles, outfile=new_particles_dir)
    else:
        collective = init_cells.Spheroid(cell_radius=params["cell_radius"], cell_count=params["Ncell"],
                                         poly=params["cell_radius_poly"], add_tracker_cells=params["track"],
                                         tracker_cell_count=params["Ntrack"])
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


def run_sweep(sweep_type, global_parameters, parameter_1D_sweep, parameter_2D_sweep, parameter_3D_sweep,
              enable_samos_exec, group_folder, debug, digit_precision, num_cores):
    """
    This multi-dimensional sweeping handler operates in 3 sweep_types: Single value, 1 parameter range and 2 parameter
    ranges. In the first case, the global_parameters are used.
    """
    processes = []
    pool = multiprocessing.Pool(processes=num_cores)
    folder_values = ["Nframes", "Ncell", "L", "phiecm", "kce", "divcell", "v0", "divasymprob"]
    if sweep_type == 0:
        print_log("!! Running single simulation without sweep")
        params_dict = copy.deepcopy(global_parameters)
        param_pair_label = create_samos_folder_name(folder_values=folder_values, global_parameters=params_dict)
        if params_dict["track"]:
            param_pair_label += "_track-{}".format(params_dict["Ntrack"])

        session_label = param_pair_label
        if debug:
            session_label = "debug"
            param_pair_label = "debug"
        processes.append(pool.apply_async(func=run_simulation, args=(
        params_dict, group_folder, session_label, param_pair_label, enable_samos_exec)))

    if sweep_type == 1:
        if parameter_1D_sweep["v1type"] == "custom":
            v1range = parameter_1D_sweep["v1custom"]
        else:
            if parameter_1D_sweep["v1type"] == "log":
                v1range = np.logspace(np.log10(parameter_1D_sweep["v1start"]),
                                      np.log10(parameter_1D_sweep["v1end"]), parameter_1D_sweep["v1num"])
            if parameter_1D_sweep["v1type"] == "linear":
                v1range = np.linspace(parameter_1D_sweep["v1start"], parameter_1D_sweep["v1end"],
                                      parameter_1D_sweep["v1num"])
        v1range = np.round(v1range, digit_precision)

        session_label = "{}_{}_{}-{}_#{}".format(parameter_1D_sweep["v1"], parameter_1D_sweep["v1type"],
                                                 min(v1range), max(v1range), len(v1range))

        print_log(f"!! Starting 1D parameter sweep for a total of {len(v1range)} parameter values...")
        for var1_idx, var1 in enumerate(v1range):
            progress = f"{round(100 * var1_idx / (len(v1range)))} %"
            status = "{} {}".format(parameter_1D_sweep["v1"], var1)
            progress_msg = f"[{progress}] --- {status} ---"
            print_log(progress_msg)
            params_dict = copy.deepcopy(global_parameters)
            params_dict[parameter_3D_sweep["v1"]] = var1
            param_pair_label = create_samos_folder_name(folder_values=folder_values, global_parameters=params_dict)
            processes.append(pool.apply_async(func=run_simulation, args=(
            params_dict, group_folder, session_label, param_pair_label, enable_samos_exec)))

    if sweep_type == 2:
        if parameter_2D_sweep["v1type"] == "custom":
            v1range = parameter_2D_sweep["v1custom"]
        else:
            if parameter_2D_sweep["v1type"] == "log":
                v1range = np.logspace(np.log10(parameter_2D_sweep["v1start"]),
                                      np.log10(parameter_2D_sweep["v1end"]),
                                      parameter_2D_sweep["v1num"])
            if parameter_2D_sweep["v1type"] == "linear":
                v1range = np.linspace(parameter_2D_sweep["v1start"], parameter_2D_sweep["v1end"],
                                      parameter_2D_sweep["v1num"])
        if parameter_2D_sweep["v2type"] == "custom":
            v2range = parameter_2D_sweep["v2custom"]
        else:
            if parameter_2D_sweep["v2type"] == "log":
                v2range = np.logspace(np.log10(parameter_2D_sweep["v2start"]),
                                      np.log10(parameter_2D_sweep["v2end"]),
                                      parameter_2D_sweep["v2num"])
            if parameter_2D_sweep["v2type"] == "linear":
                v2range = np.linspace(parameter_2D_sweep["v2start"], parameter_2D_sweep["v2end"],
                                      parameter_2D_sweep["v2num"])
        v1range = np.round(v1range, digit_precision)
        v2range = np.round(v2range, digit_precision)

        session_label = "{}_{}_{}-{}_#{}_vs_{}_{}_{}-{}_#{}".format(parameter_2D_sweep["v1"],
                                                                    parameter_2D_sweep["v1type"],
                                                                    min(v1range), max(v1range), len(v1range),
                                                                    parameter_2D_sweep["v2"],
                                                                    parameter_2D_sweep["v2type"],
                                                                    min(v2range), max(v2range), len(v2range))

        print_log(
            f"!! Starting 2D parameter sweep for {len(v1range) * len(v2range)} parameter pairs...")
        i_progress = 0
        for var1_idx, var1 in enumerate(v1range):
            for var2_idx, var2 in enumerate(v2range):
                i_progress += 1
                progress = f"{round(100 * i_progress / (len(v1range) * len(v2range)))} %"
                status = "{} {} {} {}".format(parameter_2D_sweep["v1"], var1, parameter_2D_sweep["v2"], var2)
                progress_msg = f"[{progress}] --- {status} ---"
                print_log(progress_msg)
                params_dict = copy.deepcopy(global_parameters)
                params_dict[parameter_3D_sweep["v1"]] = var1
                params_dict[parameter_3D_sweep["v2"]] = var2
                param_pair_label = create_samos_folder_name(folder_values=folder_values, global_parameters=params_dict)
                processes.append(pool.apply_async(func=run_simulation, args=(
                params_dict, group_folder, session_label, param_pair_label, enable_samos_exec)))

    if sweep_type == 3:
        if parameter_3D_sweep["v1type"] == "custom":
            v1range = parameter_3D_sweep["v1custom"]
        else:
            if parameter_3D_sweep["v1type"] == "log":
                v1range = np.logspace(np.log10(parameter_3D_sweep["v1start"]),
                                      np.log10(parameter_3D_sweep["v1end"]),
                                      parameter_3D_sweep["v1num"])
            if parameter_3D_sweep["v1type"] == "linear":
                v1range = np.linspace(parameter_3D_sweep["v1start"], parameter_3D_sweep["v1end"],
                                      parameter_3D_sweep["v1num"])
        if parameter_3D_sweep["v2type"] == "custom":
            v2range = parameter_3D_sweep["v2custom"]
        else:
            if parameter_3D_sweep["v2type"] == "log":
                v2range = np.logspace(np.log10(parameter_3D_sweep["v2start"]),
                                      np.log10(parameter_3D_sweep["v2end"]),
                                      parameter_3D_sweep["v2num"])
            if parameter_3D_sweep["v2type"] == "linear":
                v2range = np.linspace(parameter_3D_sweep["v2start"], parameter_3D_sweep["v2end"],
                                      parameter_3D_sweep["v2num"])
        if parameter_3D_sweep["v3type"] == "custom":
            v3range = parameter_3D_sweep["v3custom"]
        else:
            if parameter_3D_sweep["v3type"] == "log":
                v3range = np.logspace(np.log10(parameter_3D_sweep["v3start"]),
                                      np.log10(parameter_3D_sweep["v3end"]),
                                      parameter_3D_sweep["v3num"])
            if parameter_3D_sweep["v3type"] == "linear":
                v3range = np.linspace(parameter_3D_sweep["v3start"], parameter_3D_sweep["v3end"],
                                      parameter_3D_sweep["v3num"])

        v1range = np.round(v1range, digit_precision)
        v2range = np.round(v2range, digit_precision)
        v3range = np.round(v3range, digit_precision)
        session_label = "{}_{}_{}-{}_#{}_vs_{}_{}_{}-{}_#{}_vs_{}_{}_{}-{}_#{}".format(parameter_3D_sweep["v1"],
                                                                                       parameter_3D_sweep["v1type"],
                                                                                       min(v1range), max(v1range),
                                                                                       len(v1range),
                                                                                       parameter_3D_sweep["v2"],
                                                                                       parameter_3D_sweep["v2type"],
                                                                                       min(v2range), max(v2range),
                                                                                       len(v2range),
                                                                                       parameter_3D_sweep["v3"],
                                                                                       parameter_3D_sweep["v3type"],
                                                                                       min(v3range), max(v3range),
                                                                                       len(v3range))

        print_log(
            f"!! Starting 3D parameter sweep for {len(v1range) * len(v2range) * len(v3range)} parameter pairs...")
        i_progress = 0
        for var1_idx, var1 in enumerate(v1range):
            for var2_idx, var2 in enumerate(v2range):
                for var3_idx, var3 in enumerate(v3range):
                    i_progress += 1
                    progress = f"{round(100 * i_progress / (len(v1range) * len(v2range) * len(v3range)))} %"
                    status = "{} {} {} {} {} {}".format(parameter_3D_sweep["v1"], var1, parameter_3D_sweep["v2"], var2,
                                                        parameter_3D_sweep["v3"], var3)
                    progress_msg = f"[{progress}] --- {status} ---"
                    print_log(progress_msg)
                    params_dict = copy.deepcopy(global_parameters)
                    params_dict[parameter_3D_sweep["v1"]] = var1
                    params_dict[parameter_3D_sweep["v2"]] = var2
                    params_dict[parameter_3D_sweep["v3"]] = var3
                    param_pair_label = create_samos_folder_name(folder_values=folder_values,
                                                                global_parameters=params_dict)
                    processes.append(pool.apply_async(func=run_simulation, args=(
                    params_dict, group_folder, session_label, param_pair_label, enable_samos_exec)))

    for p in processes:
        p.get()

    pool.close()
    pool.join()
