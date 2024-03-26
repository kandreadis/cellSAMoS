"""
Collection of functions that perform batch analysis of SAMoS simulation results.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""
import os
import numpy as np

from paths_init import system_paths
from scripts.data_handler import dict2dataframe, dataframe2csv, read_dat, read_xyz, add_result, add_vars, read_radii, \
    read_vel, import_resultdf, read_dr_l, read_params_dict
from scripts.visualisation import plot_lineplot, plot_profile, plot_msd
from scripts.analysis import calc_radius_gyration, calc_r, calc_phi, calc_msd
from scripts.communication_handler import print_log, visualise_result_tree, print_progressbar
from multiprocessing import Pool


def analyse_folder(session_folder, type_analysis, root, vars_select, result_folder, dt, freq, debug, dat_iter_debug,
                   idx_iter_debug):
    """
    For a folder within ../figures/root/session_folder, all SAMoS output folders are analysed by their .dat files.
    """
    print_log(f"Looking for folder vars {list(vars_select.keys())}...")
    analysis_output_dir = system_paths["output_analysis_dir"]
    res_root_dir = os.path.join(analysis_output_dir, result_folder, session_folder)

    # Directory management
    result_folder_path = os.path.join(root, session_folder)
    analysis_result_dict = {}
    msd_dict = {}
    ossearch = sorted(os.listdir(result_folder_path))
    result_folder_subdirs = []
    for i, folder in enumerate(ossearch):
        if os.path.isdir(os.path.join(root, session_folder, folder)):
            result_folder_subdirs.append(folder)

    result_folder_subdirs_num = len(result_folder_subdirs)
    print_log(f"-- Found {result_folder_subdirs_num} folders, starting analysis !")

    # Loop through all SAMoS output folders
    for idx, output_dir in enumerate(result_folder_subdirs):
        print_progressbar(idx=idx, idxmax=result_folder_subdirs_num)
        folder_path = os.path.join(result_folder_path, output_dir)

        params = read_params_dict(path=folder_path)

        dat_files = [f for f in sorted(os.listdir(folder_path)) if f.endswith(".dat")]

        # If folder is empty, continue to next one
        if len(dat_files) == 0: continue

        # Find all parameters inside folder name
        var_list = output_dir.split("_")

        # ***********************************************************
        # *    Dynamic Analysis (MSD)                               *
        # ***********************************************************
        Dr, L = read_dr_l(var_list=var_list)
        if debug: print_log(f"-- MSD analysis Dr: {Dr} L: {L}...")

        # Extract the xyz positions for each time frame (.dat file)
        xyz = []
        t = []
        for dat_iter, dat_dir in enumerate(dat_files):
            if debug and (dat_iter % 100 == 0):
                print_log(f"  {len(dat_files) - dat_iter} .dat files left...")
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            xyz.append(read_xyz(data=dat_content, group_index=1))
            time_index = int(os.path.splitext(os.path.basename(dat_file_dir))[0].split("_")[-1])
            t.append(time_index)
            if dat_iter == dat_iter_debug: break

        # Rescale the time range
        t = np.asarray(t)
        t = (t - np.min(t)) * dt
        txyz = np.stack(xyz, axis=0)

        # If only 1 particle is present or 2D plane analysis, don't substract CM!
        if txyz.shape[1] == 1 or type_analysis == "plane":
            delta_t, msd, msderr = calc_msd(tnxyz=txyz, L=L, t=t, tau=1 / Dr, freqdt=freq * dt, debug=debug,
                                            substract_CM=False)
        else:
            delta_t, msd, msderr = calc_msd(tnxyz=txyz, L=L, t=t, tau=1 / Dr, freqdt=freq * dt, debug=debug,
                                            substract_CM=True)

        # Save MSD measurements
        for delta_t_i in range(len(delta_t)):
            add_result(target=msd_dict, tag="lag time", item=delta_t[delta_t_i])
            add_result(target=msd_dict, tag="MSD", item=msd[delta_t_i])
            add_result(target=msd_dict, tag="MSD/t", item=msd[delta_t_i] / delta_t[delta_t_i])
            add_result(target=msd_dict, tag="MSD error", item=msderr[delta_t_i])
            add_result(target=msd_dict, tag="freq", item=freq)
            add_result(target=msd_dict, tag="dt", item=dt)
            if "Dr" not in var_list:
                add_result(target=msd_dict, tag="Dr", item=Dr)
            add_vars(target=msd_dict, var_list=var_list, vars_select=vars_select)

        # ***********************************************************
        # *     Static Analysis (Radial density profile, etc..)     *
        # ***********************************************************
        if debug: print_log("Static analysis...")
        for dat_iter, dat_dir in enumerate(dat_files):
            # Performed for each timestep (.dat file)
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            time_index = int(os.path.splitext(os.path.basename(dat_file_dir))[0].split("_")[-1])
            xyz_cells = read_xyz(data=dat_content, group_index=1)

            if type_analysis == "plane":
                vel_cells = read_vel(data=dat_content, group_index=1)
                avg_vel = np.average(np.sqrt(np.sum(np.square(vel_cells), axis=1)), axis=0)
            else:
                radii_cells = read_radii(data=dat_content, group_index=1)
                cell_count = len(xyz_cells)
                r_cells = calc_r(xyz_cells)
                r_cells_binned, phi_cells, r_cells_core, r_cell_invasion = calc_phi(r_cells, radii_cells)
                r_gyration_cells = calc_radius_gyration(xyz=xyz_cells)

                xyz_ecm = read_xyz(data=dat_content, group_index=2)
                ecm_count = len(xyz_ecm)
                radii_ecm = read_radii(data=dat_content, group_index=2)
                r_ecm = calc_r(xyz_ecm)
                r_ecm_binned, phi_ecm, _, _ = calc_phi(r_ecm, radii_ecm)

                # MECHANICS TO BE ADDED

            # Add found results
            add_result(target=analysis_result_dict, tag="dir", item=output_dir)
            add_result(target=analysis_result_dict, tag=".data dir", item=dat_dir)
            add_result(target=analysis_result_dict, tag="time", item=time_index)

            if type_analysis == "plane":
                add_result(target=analysis_result_dict, tag="average velocity", item=avg_vel)
            else:
                add_result(target=analysis_result_dict, tag="cell count", item=cell_count)
                add_result(target=analysis_result_dict, tag="ECM count", item=ecm_count)
                add_result(target=analysis_result_dict, tag="radius of gyration", item=r_gyration_cells)

                add_result(target=analysis_result_dict, tag="r cells", item=r_cells_binned.tolist())
                add_result(target=analysis_result_dict, tag="phi cells", item=phi_cells.tolist())
                add_result(target=analysis_result_dict, tag="radius of core", item=r_cells_core)
                add_result(target=analysis_result_dict, tag="radius of invasion", item=r_cell_invasion)

                add_result(target=analysis_result_dict, tag="r ECM", item=r_ecm_binned.tolist())
                add_result(target=analysis_result_dict, tag="phi ECM", item=phi_ecm.tolist())

                add_vars(target=analysis_result_dict, var_list=var_list, vars_select=vars_select)
            if dat_iter == dat_iter_debug: break
        if idx == idx_iter_debug: break

    # *****************************
    # *     Save measurements     *
    # *****************************
    if type_analysis == "plane":
        msd_df = dict2dataframe(measurement_dict=msd_dict)
        dataframe2csv(res_root_dir=res_root_dir, df=msd_df, csv_filename="measurements.csv")
    else:
        analysis_result_df = dict2dataframe(measurement_dict=analysis_result_dict)
        analysis_result_df["time"] = (analysis_result_df["time"] - min(analysis_result_df["time"].values)) * dt
        dataframe2csv(res_root_dir=res_root_dir, df=analysis_result_df, csv_filename="measurements.csv")
        msd_df = dict2dataframe(measurement_dict=msd_dict)
        dataframe2csv(res_root_dir=res_root_dir, df=msd_df, csv_filename="tumoroid_msd.csv")

    print_log(f"Saved analysis results to {res_root_dir}!")


def visualise_folder(session_folder, type_analysis, result_folder, vars_select, dt, freq, dpi, show):
    """
    DOCSTRING
    """
    session_label = os.path.join(result_folder, session_folder)
    analysis_output_dir = system_paths["output_analysis_dir"]
    res_root_dir = os.path.join(analysis_output_dir, result_folder, session_folder)
    result_df = import_resultdf(res_root_dir=res_root_dir, name="measurements.csv")
    experimental_msd_df = import_resultdf(res_root_dir=res_root_dir, name="tumoroid_msd.csv")
    try:
        print_log(f"Imported data with keys {list(result_df.keys())}")
        if experimental_msd_df is not None:
            print_log(f"Imported data with keys {list(experimental_msd_df.keys())}")
    except:
        print_log(f"No data found, run analysis first...")
        return
    if type_analysis == "plane":
        # MSD vs. time grouped by group_key
        group_key = "rotational diffusion Dr"
        color_key = "propulsion v0"
        group_short = "Dr"
        try:
            test1, test2 = np.unique(result_df[group_key]), np.unique(result_df[color_key])
        except:
            print_log("Old naming convention...")
            group_key = "Dr"
            color_key = "v0"

        color_range = list(np.unique(result_df[color_key]))
        for group_val in np.unique(result_df[group_key].values):
            msd_dr = result_df.groupby(group_key).get_group(group_val)
            print_log(f"{group_key}: {group_val}")
            plot_msd(session=session_label, data=msd_dr, x="lag time", y="MSD", hue=color_key,
                     show=show, dpi=dpi, extra_label=f" {group_short}={group_val}", log_offsets=[-2, -2],
                     t_offset=0.1, error="MSD error", color_range=color_range)
            plot_msd(session=session_label, data=msd_dr, x="lag time", y="MSD/t", hue=color_key,
                     show=show, dpi=dpi, extra_label=f" {group_short}={group_val}", log_offsets=[-1, -1],
                     t_offset=0.1, color_range=color_range)


    else:
        plotkeys_profile = {  # X, Y, COLOR
            0: ["r cells", "phi cells", "time"],
            1: ["r ECM", "phi ECM", "time"]
        }

        plotkeys_line = {  # X, Y
            0: ["time", "radius of core"],
            1: ["time", "radius of invasion"],
            2: ["time", "cell count"],
            3: ["time", "ECM count"]

        }

        var_sweep = ["phiecm", "divcell", "v0", "kce"]
        if np.unique(result_df["cell count"])[0] == 1:
            var_sweep = ["phiecm", "kce", "v0", "divcell"]
        avail_params = []
        for key in var_sweep:
            if key in result_df.keys():
                avail_params.append(key)
        v1key, v2key, v3key, v4key = avail_params
        v4val = np.unique(result_df[v4key])[0]
        print_log(f"Sweep parameters: {v1key, v2key, v3key}")

        for v1 in np.unique(result_df[v1key]):
            params_label_1v = f" {v4key}-{v4val}_{v1key}-{v1}"
            res_sel_1v = result_df.groupby(v1key).get_group(v1)

            for v2 in np.unique(result_df[v2key]):
                params_label_2v = f" {v4key}-{v4val}_{v1key}-{v1}_{v2key}-{v2}"
                res_sel_2v = res_sel_1v.groupby(v2key).get_group(v2)
                experimental_msd_set = experimental_msd_df.groupby(v1key).get_group(v1).groupby(v2key).get_group(v2)
                color_range = list(np.unique(experimental_msd_set[v3key]))

                plot_msd(session=session_label, data=experimental_msd_set, x="lag time", y="MSD", hue=v3key,
                         show=show, dpi=dpi, extra_label=params_label_2v, log_offsets=[-2, -2], t_offset=freq * dt,
                         error="MSD error", color_range=color_range)
                plot_msd(session=session_label, data=experimental_msd_set, x="lag time", y="MSD/t", hue=v3key,
                         show=show, dpi=dpi, extra_label=params_label_2v, log_offsets=[-1, -1], t_offset=freq * dt,
                         color_range=color_range)

                for plotkey in plotkeys_line:
                    X, Y = plotkeys_line[plotkey]
                    plot_lineplot(session=session_label, data=res_sel_2v, x=X, y=Y, hue=v3key, style=v2key, show=show,
                                  dpi=dpi, extra_label=params_label_2v)

                for v3 in np.unique(result_df[v3key]):
                    params_label_3v = f" {v4key}-{v4val}_{v1key}-{v1}_{v2key}-{v2}_{v3key}-{v3}"
                    res_sel_3v = res_sel_2v.groupby(v3key).get_group(v3)
                    for plotkey in plotkeys_profile:
                        X, Y, HUE = plotkeys_profile[plotkey]
                        plot_profile(session=session_label, data=res_sel_3v, x=X, y=Y, hue=HUE, show=show, dpi=dpi,
                                     extra_label=params_label_3v, varlabels=vars_select)


def pool_task(args, session_folder, result_folder, vars_select, root):
    """
    Executes core pool tasks
    """
    analyse = args.analyse
    visualise = args.visualise
    dpi = args.dpi
    debug = args.debug
    dt = args.dt
    freq = args.freq
    show = args.show
    type_analysis = args.type_analysis
    dat_iter_debug = args.dat_iter_debug
    idx_iter_debug = args.idx_iter_debug
    if analyse:
        analyse_folder(session_folder, type_analysis, root, vars_select, result_folder, dt, freq, debug, dat_iter_debug,
                       idx_iter_debug)
    if visualise:
        visualise_folder(session_folder, type_analysis, result_folder, vars_select, dt, freq, dpi, show)


def analyse_root_subfolders(folders_of_interests, args, vars_select):
    """
    Finds all paths within a given root folder, and performs analysis for a dict of parameters and resolution dpi.
    """
    analyse = args.analyse
    visualise = args.visualise
    num_cores = args.Ncores

    processes = []
    pool = Pool(processes=num_cores)

    for result_folder in folders_of_interests:
        if not analyse and visualise:
            analysis_output_dir = system_paths["output_analysis_dir"]
            root = os.path.join(analysis_output_dir, result_folder)
        else:
            root = os.path.join(system_paths["output_samos_dir"], result_folder)

        print_log(f"|- Searching {root} -|")

        ossearch = sorted(os.listdir(root))
        session_root = []
        for i, folder in enumerate(ossearch):
            if os.path.isdir(os.path.join(root, folder)):
                session_root.append(folder)

        for session_folder in session_root:
            print_log(f"- {session_folder} -")
            session_vars = session_folder.split("_")
            for i in session_vars:
                if "freq" in i:
                    freq_override = float(session_vars[-1].split("-")[-1])
                    args.freq = freq_override

            processes.append(
                pool.apply_async(func=pool_task, args=(args, session_folder, result_folder, vars_select, root)))

            visualise_result_tree(path=system_paths["output_figures_dir"], tree_type="analysis", show_subfolders=True)

    for p in processes:
        p.get()

    pool.close()
    pool.join()
