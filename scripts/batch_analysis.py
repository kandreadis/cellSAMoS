"""
Collection of functions that perform batch analysis of SAMoS simulation results.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""
import os
import numpy as np
import pandas as pd

from paths_init import system_paths
from scripts.data_handler import read_dat, read_xyz, add_result, add_var, read_radii, read_vel
from scripts.visualisation import plot_heatmap, plot_scatterplot, plot_lineplot, plot_boxplot, plot_profile, \
    plot_phase_diagram
from scripts.analysis import calc_radius_gyration, calc_cell_count, calc_msd_fit, calc_r, calc_phi, calc_msd
from scripts.communication_handler import print_log


def analyse_folder(root, session_folder, vars_select, result_folder, dpi):
    """
    For a folder within ../figures/root/session_folder, all sub-folders are analysed by investigating .dat files.
    """
    # Directory management
    session_label = os.path.join(result_folder, session_folder)
    result_folder_path = os.path.join(root, session_folder)
    analysis_result_dict = {}
    result_folder_subdirs = sorted(os.listdir(result_folder_path))
    result_folder_subdirs_num = len(result_folder_subdirs)
    print_log(f"Found {result_folder_subdirs_num} folders in {result_folder_path}")
    progress_bar = "[__________]"
    for idx, output_dir in enumerate(result_folder_subdirs):
        # Performed for each samos output folder
        progress = 10 * (idx + 1) / result_folder_subdirs_num
        if progress in range(11):
            str_list = list(progress_bar)
            if progress > 0:
                for i in range(int(progress)):
                    str_list[i + 1] = "="
            progress_bar = "".join(str_list)
            print_log(f"Processing {progress_bar}")
        folder_path = os.path.join(result_folder_path, output_dir)
        dat_files = [f for f in sorted(os.listdir(folder_path)) if f.endswith(".dat")]
        if len(dat_files) == 0:
            # If folder is empty, continue to next one
            continue

        # Find all parameters inside folder name
        var_list = output_dir.split("_")

        if "phi" in var_list[3]:
            plane = True

        # Time-dependent measurements (MSD, etc.)
        tracked = True
        xyz_trackers = []
        for dat_dir in dat_files:
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            if 2 not in dat_content["type"].values:
                tracked = False
                # No trackers present, moving on to next analysis..
                break
            xyz_trackers.append(read_xyz(data=dat_content, group_index=2))
        if tracked:
            print("Tracker analysis...")
            txyz_trackers = np.stack(xyz_trackers, axis=0)
            msd_trackers = calc_msd(tnxyz=txyz_trackers, L=100.0, substract_CM=True)
            msd_trackers_fit, msd_trackers_slope = calc_msd_fit(tmsd=msd_trackers)

        if plane:
            # print("Plane analysis...")
            xyz_plane = []
            for dat_iter, dat_dir in enumerate(dat_files):
                dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
                dat_content = read_dat(path=dat_file_dir)
                xyz_plane.append(read_xyz(data=dat_content, group_index=1))
                # if dat_iter == 10: break # !!!!!!!!!!!!!!!

            txyz_plane = np.stack(xyz_plane, axis=0)
            msd_plane = calc_msd(tnxyz=txyz_plane, L=100.0)

        # print("Static analysis...")
        # Static measurements (Radial density profile, etc.)
        for dat_iter, dat_dir in enumerate(dat_files):
            # Performed for each .dat file
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            time_index = int(os.path.splitext(os.path.basename(dat_file_dir))[0].split("_")[-1])
            xyz_cells = read_xyz(data=dat_content, group_index=1)

            if plane:
                vel_cells = read_vel(data=dat_content, group_index=1)
                avg_vel = np.average(np.sqrt(np.sum(np.square(vel_cells), axis=1)), axis=0)
            else:
                radii_cells = read_radii(data=dat_content, group_index=1)
                cell_count = calc_cell_count(xyz_cells)
                r_cells = calc_r(xyz_cells)
                r_cells_binned, phi, dphidr, r_core = calc_phi(r_cells, radii_cells)
                r_gyration_cells = calc_radius_gyration(xyz=xyz_cells)

            # Add found results
            add_result(target=analysis_result_dict, tag="dir", item=output_dir)
            add_result(target=analysis_result_dict, tag=".data dir", item=dat_dir)
            add_result(target=analysis_result_dict, tag="time", item=time_index)

            if plane:
                add_result(target=analysis_result_dict, tag="average velocity", item=avg_vel)
            else:
                add_result(target=analysis_result_dict, tag="cell count", item=cell_count)
                add_result(target=analysis_result_dict, tag="radius of gyration", item=r_gyration_cells)
                add_result(target=analysis_result_dict, tag="radius of core", item=r_core)
                add_result(target=analysis_result_dict, tag="phi cells", item=[phi])
                add_result(target=analysis_result_dict, tag="derivative of phi cells", item=[dphidr])
                add_result(target=analysis_result_dict, tag="r", item=[r_cells_binned])

            if plane:
                add_result(target=analysis_result_dict, tag="MSD", item=msd_plane[dat_iter])

            if tracked:
                add_result(target=analysis_result_dict, tag="MSD trackers", item=msd_trackers[dat_iter])
                add_result(target=analysis_result_dict, tag="MSD trackers fit", item=msd_trackers_fit[dat_iter])
                add_result(target=analysis_result_dict, tag="MSD trackers slope", item=round(msd_trackers_slope, 2))

            for item in vars_select.values():
                add_var(target=analysis_result_dict, var_list=var_list, var_short=item[0], var_long=item[1],
                        var_type=item[2])

            # if dat_iter == 10: break # !!!!!!!!!!!!!!!

    # Process result dictionary
    result_df = pd.DataFrame.from_dict(analysis_result_dict, orient="columns")
    dt = 0.01
    result_df["time"] = (result_df["time"] - min(result_df["time"].values)) * dt
    print_log(f"Result dataframe with shape:{result_df.shape} and categories: {list(result_df.columns)}")
    print_log("----")
    # TODO replace visualisation logic with itertools for all parameter combinations
    show = False
    if tracked:
        plot_lineplot(session=session_label, data=result_df, x="time", y=["msd", "msd fit"], hue="msd slope",
                      style=None, show=show, dpi=dpi, loglog=True)
        plot_lineplot(session=session_label, data=result_df, x="time", y="msd", hue="msd slope",
                      style=None, show=show, dpi=dpi, loglog=True)
    if plane:
        # General phase diagram
        plot_phase_diagram(session=session_label, data=result_df, rows="rotational diffusion Dr",
                           columns="propulsion v0", values="average velocity", show=show, dpi=dpi)
        # Velocity fluctuations in steady state
        plot_lineplot(session=session_label, data=result_df, x="time", y="average velocity",
                      hue="propulsion v0", style="rotational diffusion Dr", show=show, dpi=dpi)
        # Average velocity vs. v0 | Dr
        plot_lineplot(session=session_label, data=result_df, x="propulsion v0", y="average velocity",
                      hue="rotational diffusion Dr", style=None, show=show, dpi=dpi)
        plot_lineplot(session=session_label, data=result_df, x="propulsion v0", y="average velocity",
                      hue="rotational diffusion Dr", style=None, show=show, dpi=dpi, loglog=True,
                      extra_label="_loglog")
        # Average velocity vs. Dr | v0
        plot_lineplot(session=session_label, data=result_df, x="rotational diffusion Dr", y="average velocity",
                      hue="propulsion v0", style=None, show=show, dpi=dpi, logx=True, extra_label="_logx")
        plot_lineplot(session=session_label, data=result_df, x="rotational diffusion Dr", y="average velocity",
                      hue="propulsion v0", style=None, show=show, dpi=dpi, loglog=True, extra_label="_loglog")

        try:
            # MSD vs. time grouped by Dr
            for Drval in np.unique(result_df["rotational diffusion Dr"].values):
                result_dr = result_df.groupby("rotational diffusion Dr").get_group(Drval)
                plot_lineplot(session=session_label, data=result_dr, x="time", y="MSD", hue="propulsion v0",
                              style=None, show=show, dpi=dpi, loglog=True, extra_label=f"_Dr-{Drval}",
                              log_offset=-1)
        except:
            print("no Dr values in folder names")
            plot_lineplot(session=session_label, data=result_df, x="time", y="MSD", hue="propulsion v0",
                          style=None, show=show, dpi=dpi, loglog=True, log_offset=-2)
    else:
        plot_profile(session=session_label, data=result_df, x="r", y="phi cells", hue="time", show=show,
                     dpi=dpi, loglog=False)
        plot_profile(session=session_label, data=result_df, x="r", y="derivative of phi cells", hue="time",
                     show=show, dpi=dpi, loglog=False)

        plot_lineplot(session=session_label, data=result_df, x="time", y="radius of core", hue=None,
                      style=None, show=show, dpi=dpi)

        plot_lineplot(session=session_label, data=result_df, x="time", y="radius of gyration", hue=None,
                      style=None, show=show, dpi=dpi)
        plot_lineplot(session=session_label, data=result_df, x="time", y="cell count", hue=None, style=None,
                      show=show, dpi=dpi)

        # if "cell radius polydispersity" in list(result_df.columns):
    #     plot_lineplot(session=session_label, data=result_df, x="time", y="cell count",
    #                   hue="cell radius polydispersity", style=None, show=show, dpi=dpi)
    #     plot_scatterplot(session=session_label, data=result_df, x="cell radius polydispersity", y="radius of gyration",
    #                      hue="time", style=None, show=show, dpi=dpi)
    #     result_df_last_time = result_df.groupby("time").get_group(max(result_df["time"]))
    #     plot_lineplot(session=session_label, data=result_df_last_time, x="cell radius polydispersity",
    #                   y="radius of gyration", hue=None, style=None, show=show, dpi=dpi)
    #
    # if "potential re factor" in list(result_df.columns):
    #     plot_lineplot(session=session_label, data=result_df, x="time", y="cell count", hue="potential re factor",
    #                   style=None, show=show, dpi=dpi)
    #     plot_scatterplot(session=session_label, data=result_df, x="potential re factor", y="radius of gyration",
    #                      hue="time", style=None, show=show, dpi=dpi)
    #     result_df_last_time = result_df.groupby("time").get_group(max(result_df["time"]))
    #     plot_lineplot(session=session_label, data=result_df_last_time, x="potential re factor", y="radius of gyration",
    #                   hue=None, style=None, show=show, dpi=dpi)
    #
    # if "cell division rate" in list(result_df.columns) and "propulsion alpha" in list(result_df.columns):
    #     plot_lineplot(session=session_label, data=result_df, x="time", y="cell count", hue="propulsion alpha",
    #                   style=None, show=show, dpi=dpi)
    #     plot_lineplot(session=session_label, data=result_df, x="time", y="cell count", hue="cell division rate",
    #                   style=None, show=show, dpi=dpi)
    #     print_log("Last time index: {}".format(max(result_df["time"])))
    #     result_df_last_time = result_df.groupby("time").get_group(max(result_df["time"]))
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="cell division rate",
    #                  columns="propulsion alpha", values="cell count", show=show, dpi=dpi)
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="cell division rate",
    #                  columns="propulsion alpha", values="radius of gyration", show=show, dpi=dpi)
    #
    # if "potential re factor" in list(result_df.columns) and "propulsion alpha" in list(result_df.columns):
    #     print_log("Last time index: {}".format(max(result_df["time"])))
    #     result_df_last_time = result_df.groupby("time").get_group(max(result_df["time"]))
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="potential re factor",
    #                  columns="propulsion alpha", values="cell count", show=show, dpi=dpi)
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="potential re factor",
    #                  columns="propulsion alpha", values="radius of gyration", show=show, dpi=dpi)
    #
    # if "potential re factor" in list(result_df.columns) and "cell division rate" in list(result_df.columns):
    #     print_log("Last time index: {}".format(max(result_df["time"])))
    #     result_df_last_time = result_df.groupby("time").get_group(max(result_df["time"]))
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="potential re factor",
    #                  columns="cell division rate", values="cell count", show=show, dpi=dpi)
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="potential re factor",
    #                  columns="cell division rate", values="radius of gyration", show=show, dpi=dpi)


def analyse_root_subfolders(vars_select, result_folder, dpi):
    """
    Finds all paths within a given root folder, and performs analysis for a dict of parameters and resolution dpi.
    """
    root = os.path.join(system_paths["output_samos_dir"], result_folder)
    print_log(f"|| Searching {root}...")
    session_root = os.listdir(root)
    for session_folder in session_root:
        print_log(f"-- {session_folder} --")
        analyse_folder(root, session_folder, vars_select, result_folder, dpi)
