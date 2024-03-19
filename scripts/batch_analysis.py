"""
Collection of functions that perform batch analysis of SAMoS simulation results.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""
import os
import numpy as np
import pandas as pd

from paths_init import system_paths
from scripts.data_handler import read_dat, read_xyz, add_result, add_vars, read_radii, read_vel, import_resultdf
from scripts.visualisation import plot_heatmap, plot_scatterplot, plot_lineplot, plot_boxplot, plot_profile, \
    plot_phase_diagram, plot_msd
from scripts.analysis import calc_radius_gyration, calc_msd_fit, calc_r, calc_phi, calc_msd
from scripts.communication_handler import print_log, visualise_result_tree
from multiprocessing import Pool


def analyse_folder(session_folder, type_analysis, root, vars_select, result_folder, dt, freq, debug, dat_iter_debug,
                   idx_iter_debug):
    """
    For a folder within ../figures/root/session_folder, all sub-folders are analysed by investigating .dat files.
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
    progress_bar = "[__________]"
    for idx, output_dir in enumerate(result_folder_subdirs):
        # Performed for each samos output folder
        progress = 10 * (idx + 1) / result_folder_subdirs_num
        if round(progress, 1) in range(11):
            str_list = list(progress_bar)
            if progress > 0:
                for i in range(int(progress)):
                    str_list[i + 1] = "="
            progress_bar = "".join(str_list)
            print_log(f"-- Processing {progress_bar}")
        folder_path = os.path.join(result_folder_path, output_dir)
        dat_files = [f for f in sorted(os.listdir(folder_path)) if f.endswith(".dat")]
        if len(dat_files) == 0:
            # If folder is empty, continue to next one
            continue

        # Find all parameters inside folder name
        var_list = output_dir.split("_")

        # # Time-dependent measurements (MSD, etc.)
        # tracked = True
        # xyz_trackers = []
        # for dat_dir in dat_files:
        #     dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
        #     dat_content = read_dat(path=dat_file_dir)
        #     if 2 not in dat_content["type"].values:
        #         tracked = False
        #         # No trackers present, moving on to next analysis..
        #         break
        #     xyz_trackers.append(read_xyz(data=dat_content, group_index=2))
        # if tracked:
        #     # print("-- Tracker analysis...")
        #     txyz_trackers = np.stack(xyz_trackers, axis=0)
        #     delta_t_trackers, msd_trackers = calc_msd(tnxyz=txyz_trackers, L=100.0, substract_CM=True, tau=10,
        #                                               freqdt=freq * dt)
        #     msd_trackers_fit, msd_trackers_slope = calc_msd_fit(tmsd=msd_trackers)

        if type_analysis == "plane":
            print("-- Plane analysis...")
            Dr = 0.1
            L = 100.0
            for var in var_list:
                if "Dr" in var:
                    Dr = float(var.split("-")[1])
                if "L" in var:
                    L = float(var.split("-")[1])

            # if Dr != 0.01: #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #     continue  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            print(f"Dr: {Dr} L: {L}...")
            xyz_plane = []
            t = []
            for dat_iter, dat_dir in enumerate(dat_files):
                if debug and (dat_iter % 100 == 0): print(f"  {len(dat_files) - dat_iter} .dat files left...")
                dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
                dat_content = read_dat(path=dat_file_dir)
                xyz_plane.append(read_xyz(data=dat_content, group_index=1))
                time_index = int(os.path.splitext(os.path.basename(dat_file_dir))[0].split("_")[-1])
                t.append(time_index)
                if dat_iter == dat_iter_debug: break  # !!!!!!!!!!!!!!!
            t = np.asarray(t)
            t = (t - np.min(t)) * dt
            txyz_plane = np.stack(xyz_plane, axis=0)

            delta_t_plane, msd_plane, msderr_plane = calc_msd(tnxyz=txyz_plane, L=L, t=t, tau=1 / Dr,
                                                              freqdt=freq * dt,
                                                              debug=debug)

            for delta_t_i in range(len(delta_t_plane)):
                add_result(target=msd_dict, tag="lag time", item=delta_t_plane[delta_t_i])
                add_result(target=msd_dict, tag="MSD", item=msd_plane[delta_t_i])
                add_result(target=msd_dict, tag="MSD/t", item=msd_plane[delta_t_i] / delta_t_plane[delta_t_i])
                add_result(target=msd_dict, tag="MSD error", item=msderr_plane[delta_t_i])
                add_result(target=msd_dict, tag="freq", item=freq)
                add_result(target=msd_dict, tag="dt", item=dt)
                if "Dr" not in var_list:
                    add_result(target=msd_dict, tag="Dr", item=Dr)
                add_vars(target=msd_dict, var_list=var_list, vars_select=vars_select)

        print("Static analysis...")
        # Static measurements (Radial density profile, etc.)
        for dat_iter, dat_dir in enumerate(dat_files):
            # Performed for each .dat file
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
                r_cells_binned, phi_cells, r_cells_core = calc_phi(r_cells, radii_cells)
                r_gyration_cells = calc_radius_gyration(xyz=xyz_cells)

                xyz_ecm = read_xyz(data=dat_content, group_index=2)
                ecm_count = len(xyz_ecm)
                radii_ecm = read_radii(data=dat_content, group_index=2)
                r_ecm = calc_r(xyz_ecm)
                r_ecm_binned, phi_ecm, r_ecm_core = calc_phi(r_ecm, radii_ecm)

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
                add_result(target=analysis_result_dict, tag="radius of cell core", item=r_cells_core)

                add_result(target=analysis_result_dict, tag="r ECM", item=r_ecm_binned.tolist())
                add_result(target=analysis_result_dict, tag="phi ECM", item=phi_ecm.tolist())

                # if tracked:
                #     add_result(target=analysis_result_dict, tag="MSD trackers", item=msd_trackers[dat_iter])
                #     add_result(target=analysis_result_dict, tag="MSD trackers fit", item=msd_trackers_fit[dat_iter])
                #     add_result(target=analysis_result_dict, tag="MSD trackers slope", item=round(msd_trackers_slope, 2))
                add_vars(target=analysis_result_dict, var_list=var_list, vars_select=vars_select)
            if dat_iter == dat_iter_debug: break  # !!!!!!!!!!!!!!!

        if idx == idx_iter_debug: break  # !!!!!!!!!!!!!!!!!!!!!!!!

    # Process result dictionary
    try:
        os.makedirs(res_root_dir)
    except:
        pass

    if type_analysis == "plane":
        msd_df = pd.DataFrame.from_dict(msd_dict, orient="columns")
        msd_df.to_csv(os.path.join(res_root_dir, "measurements.csv"), index=False)
    else:
        result_df = pd.DataFrame.from_dict(analysis_result_dict, orient="columns")
        try:
            result_df["time"] = (result_df["time"] - min(result_df["time"].values)) * dt
        except:
            print("No .dat files were processed.. at all... aborting!")
            return
        result_df.to_csv(os.path.join(res_root_dir, "measurements.csv"), index=False)

    print_log(f"Saved analysis results to {res_root_dir}!")


def visualise_folder(session_folder, type_analysis, result_folder, vars_select, dt, freq, dpi, show):
    session_label = os.path.join(result_folder, session_folder)
    analysis_output_dir = system_paths["output_analysis_dir"]
    res_root_dir = os.path.join(analysis_output_dir, result_folder, session_folder)
    result_df = import_resultdf(res_root_dir=res_root_dir)
    try:
        print_log(f"Imported data with keys {result_df.keys()}")
    except:
        print_log(f"No data found, run analysis first...")
        return
    if type_analysis == "plane":
        # MSD vs. time grouped by group_key
        group_key = "rotational diffusion Dr"
        color_key = "propulsion v0"
        group_short = "Dr"

        try:
            test = np.unique(result_df[group_key])
            test = np.unique(result_df[color_key])
        except:
            print("Old naming convention...")
            group_key = "Dr"
            color_key = "v0"

        color_range = list(np.unique(result_df[color_key]))
        for group_val in np.unique(result_df[group_key].values):
            msd_dr = result_df.groupby(group_key).get_group(group_val)
            print(f"{group_key}: {group_val}")
            plot_msd(session=session_label, data=msd_dr, x="lag time", y="MSD", hue=color_key,
                     show=show, dpi=dpi, extra_label=f" {group_short}={group_val}", log_offsets=[-2, -2],
                     t_offset=0.1, error="MSD error", color_range=color_range)
            plot_msd(session=session_label, data=msd_dr, x="lag time", y="MSD/t", hue=color_key,
                     show=show, dpi=dpi, extra_label=f" {group_short}={group_val}", log_offsets=[-1, -1],
                     t_offset=0.1, color_range=color_range)

        # for phival in np.unique(result_df["phiecm"]):
        #     result_df_phi = result_df.groupby("phiecm").get_group(phival)
        #     for kceval in np.unique(result_df["kce"]):
        #         result_df_phi_kce = result_df_phi.groupby("kce").get_group(kceval)
        #         color_range = list(np.unique(result_df_phi_kce[color_key]))
        #         for group_val in np.unique(result_df_phi_kce[group_key]):
        #             msd_dr = result_df_phi_kce.groupby(group_key).get_group(group_val)
        #             print(f"{group_key}: {group_val}")
        #             plot_msd(session=session_label, data=msd_dr, x="lag time", y="MSD", hue=color_key,
        #                     show=show, dpi=dpi, extra_label=f"phiecm={phival} kce={kceval} {group_short}={group_val}", log_offsets=[-2, -2],
        #                     t_offset=0.1, error="MSD error", color_range=color_range)
        #             plot_msd(session=session_label, data=msd_dr, x="lag time", y="MSD/t", hue=color_key,
        #                     show=show, dpi=dpi, extra_label=f"phiecm={phival} kce={kceval} {group_short}={group_val}", log_offsets=[-1, -1],
        #                     t_offset=0.1, color_range=color_range)

    else:
        x1, y1, hue1 = "r cells", "phi cells", "time"
        x2, y2, hue2 = "r ECM", "phi ECM", "time"
        x3, y3 = "time", "radius of cell core"
        x4, y4 = "time", "cell count"
        x5, y5 = "time", "ECM count"
        vset = "phiecm"
        # var_sweep = ["divasymprob", "phiecm", "divcell", "kce", "v0"]
        # var_sweep = ["divcell", "kce", "v0"]
        # var_sweep = ["phiecm", "divcell", "kce"]
        # var_sweep = ["phiecm", "divasymprob", "divcell"]
        # var_sweep = ["divcell", "kce", "v0"]
        # var_sweep = ["v0", "kce", "divcell"]
        var_sweep = ["phiecm", "divcell", "v0"]
        print(f"Looking for {var_sweep}...")
        # plot_lineplot(session=session_label, data=result_df, x=x3, y=y3, hue=vset, show=show, dpi=dpi)
        # plot_lineplot(session=session_label, data=result_df, x=x4, y=y4, hue=vset, show=show, dpi=dpi)
        # plot_lineplot(session=session_label, data=result_df, x=x5, y=y5, hue=vset, show=show, dpi=dpi)

        # for vsetval in np.unique(result_df[vset].values):
        #     print_log(f"{vset}={vsetval}")
        #     result_df_set = result_df.groupby(vset).get_group(vsetval)
        #     params_label = f"_{vset}={vsetval}"
        #     plot_profile(session=session_label, data=result_df_set, x=x1, y=y1, hue=hue1, show=show, dpi=dpi, loglog=False, extra_label=params_label, varlabels=vars_select)
        #     plot_profile(session=session_label, data=result_df_set, x=x2, y=y2, hue=hue2, show=show, dpi=dpi, loglog=False, extra_label=params_label, varlabels=vars_select)

        try:
            avail_params = []
            for key in var_sweep:
                if key in result_df.keys():
                    avail_params.append(key)
            v1key = avail_params[0]
            v2key = avail_params[1]
            v3key = avail_params[2]
            print(f"Sweep parameters: {v1key, v2key, v3key}")

            for vsetval in np.unique(result_df[vset].values):
                print(f"phi={vsetval}")
                result_df_set = result_df.groupby(vset).get_group(vsetval)
                for var in [v1key, v2key, v3key]:
                    if var != vset:
                        plot_lineplot(session=session_label, data=result_df_set, x=x3, y=y3, hue=var, show=show,
                                      dpi=dpi, extra_label=f"_{vset}={vsetval}")
                        plot_lineplot(session=session_label, data=result_df_set, x=x4, y=y4, hue=var, show=show,
                                      dpi=dpi, extra_label=f"{vset}={vsetval}")
                        plot_lineplot(session=session_label, data=result_df_set, x=x5, y=y5, hue=var, show=show,
                                      dpi=dpi, extra_label=f"{vset}={vsetval}")

            # for v1 in np.unique(result_df[v1key]):
            #     for v2 in np.unique(result_df[v2key]):
            #         for v3 in np.unique(result_df[v3key]):
            #             params_label = f"{v1key}-{v1}_{v2key}-{v2}_{v3key}-{v3}"
            #             result_df_select = result_df.groupby(v1key).get_group(v1).groupby(v2key).get_group(v2).groupby(v3key).get_group(v3)
            #             plot_profile(session=session_label, data=result_df_select, x=x1, y=y1, hue=hue1, show=show, dpi=dpi, loglog=False, extra_label=params_label, varlabels=vars_select)
            #             plot_profile(session=session_label, data=result_df_select, x=x2, y=y2, hue=hue2, show=show, dpi=dpi, loglog=False, extra_label=params_label, varlabels=vars_select)

        except:
            print_log("Could not find (all) sweep data...")
            plot_profile(session=session_label, data=result_df, x=x1, y=y1, hue=hue1, show=show, dpi=dpi, loglog=False,
                         extra_label="_debug", varlabels=vars_select)
            plot_profile(session=session_label, data=result_df, x=x2, y=y2, hue=hue2, show=show, dpi=dpi, loglog=False,
                         extra_label="_debug", varlabels=vars_select)
            plot_lineplot(session=session_label, data=result_df, x=x3, y=y3, show=show, dpi=dpi, extra_label=f"_debug")
            plot_lineplot(session=session_label, data=result_df, x=x4, y=y4, show=show, dpi=dpi, extra_label=f"_debug")
            plot_lineplot(session=session_label, data=result_df, x=x5, y=y5, show=show, dpi=dpi, extra_label=f"_debug")


def pool_task(args, session_folder, result_folder, vars_select, root):
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
