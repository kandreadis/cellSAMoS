"""
Collection of functions that perform batch analysis of SAMoS simulation results.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""
import os
import numpy as np
import pandas as pd

from paths_init import system_paths
from scripts.data_handler import read_dat, read_xyz, add_result, add_var, read_radii
from scripts.visualisation import plot_heatmap, plot_scatterplot, plot_lineplot, plot_boxplot, plot_profile
from scripts.analysis import calc_radius_gyration, calc_cell_count, calc_msd, \
    calc_radius_fit, calc_r, calc_phi
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
            break
        tracked = True
        xyz_trackers = []
        for dat_dir in dat_files:
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            if 2 not in dat_content["type"].values:
                tracked = False
                break
            xyz_trackers.append(read_xyz(data=dat_content, group_index=2))
        if tracked:
            txyz_trackers = np.stack(xyz_trackers, axis=0)
            Ntrackers = txyz_trackers.shape[1]
            msd_trackers = calc_msd(txyz_trackers)
        # Find all parameters inside folder name
        var_list = output_dir.split("_")
        for dat_iter, dat_dir in enumerate(dat_files):
            # Performed for each .dat file
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            time_index = int(os.path.splitext(os.path.basename(dat_file_dir))[0].split("_")[-1])
            xyz_cells = read_xyz(data=dat_content, group_index=1)
            radii_cells = read_radii(data=dat_content, group_index=1)
            cell_count = calc_cell_count(xyz_cells)
            r_cells = calc_r(xyz_cells)
            r_cells_binned, phi = calc_phi(r_cells, radii_cells)
            r_gyration_cells = calc_radius_gyration(xyz=xyz_cells)
            # r_core_cells, r_max_cells, r_std = calc_radius_fit(r=r_cells)
            # r_ratio = r_max_cells / r_core_cells

            # Add found results
            add_result(target=analysis_result_dict, tag="dir", item=output_dir)
            add_result(target=analysis_result_dict, tag=".data dir", item=dat_dir)
            add_result(target=analysis_result_dict, tag="time frame", item=time_index)
            add_result(target=analysis_result_dict, tag="cell count", item=cell_count)
            add_result(target=analysis_result_dict, tag="radius of gyration", item=r_gyration_cells)
            # add_result(target=analysis_result_dict, tag="radius of core sphere", item=r_core_cells)
            # add_result(target=analysis_result_dict, tag="radius of max sphere", item=r_max_cells)
            # add_result(target=analysis_result_dict, tag="radius ratio max vs core", item=r_ratio)
            # add_result(target=analysis_result_dict, tag="radial standard deviation", item=r_std)
            add_result(target=analysis_result_dict, tag="phi cells", item=[phi])
            add_result(target=analysis_result_dict, tag="r cells", item=[r_cells_binned])

            if tracked:
                add_result(target=analysis_result_dict, tag="msd", item=msd_trackers[dat_iter])

            for item in vars_select.values():
                add_var(target=analysis_result_dict, var_list=var_list, var_short=item[0], var_long=item[1],
                        var_type=item[2])
    # Process result dictionary
    result_df = pd.DataFrame.from_dict(analysis_result_dict, orient="columns")
    print_log(f"Result dataframe shape:{result_df.shape}")
    print_log(list(result_df.columns))
    print_log("----")
    # TODO replace visualisation logic with itertools for all parameter combinations
    show = True
    if "time frame" in list(result_df.columns):
        if tracked:
            plot_lineplot(session=session_label+f" [{Ntrackers} trackers]", data=result_df, x="time frame", y="msd", hue=None,
                          style=None, show=show, dpi=dpi, loglog=True)
        plot_profile(session=session_label, data=result_df, x="r cells",
                      y="phi cells", hue="time frame", show=show, dpi=dpi, loglog=False)

        # plot_boxplot(session=session_label, data=result_df, x="time frame", y="cell count", hue=None, show=show,
        #              dpi=dpi)
        # plot_lineplot(session=session_label, data=result_df, x="time frame", y="radius of gyration", hue=None,
        #               style=None, show=show, dpi=dpi)
        # plot_lineplot(session=session_label, data=result_df, x="time frame",
        #               y=["radius of core sphere", "radius of max sphere"], hue=None,
        #               style=None, show=show, dpi=dpi, loglog=False)
        # plot_lineplot(session=session_label, data=result_df, x="time frame",
        #               y=["radius ratio max vs core", "radial standard deviation"], hue=None, style=None, show=show, dpi=dpi, loglog=False)

        # if "cell radius polydispersity" in list(result_df.columns):
    #     plot_lineplot(session=session_label, data=result_df, x="time frame", y="cell count",
    #                   hue="cell radius polydispersity", style=None, show=show, dpi=dpi)
    #     plot_scatterplot(session=session_label, data=result_df, x="cell radius polydispersity", y="radius of gyration",
    #                      hue="time frame", style=None, show=show, dpi=dpi)
    #     result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
    #     plot_lineplot(session=session_label, data=result_df_last_time, x="cell radius polydispersity",
    #                   y="radius of gyration", hue=None, style=None, show=show, dpi=dpi)
    #
    # if "potential re factor" in list(result_df.columns):
    #     plot_lineplot(session=session_label, data=result_df, x="time frame", y="cell count", hue="potential re factor",
    #                   style=None, show=show, dpi=dpi)
    #     plot_scatterplot(session=session_label, data=result_df, x="potential re factor", y="radius of gyration",
    #                      hue="time frame", style=None, show=show, dpi=dpi)
    #     result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
    #     plot_lineplot(session=session_label, data=result_df_last_time, x="potential re factor", y="radius of gyration",
    #                   hue=None, style=None, show=show, dpi=dpi)
    #
    # if "cell division rate" in list(result_df.columns) and "propulsion alpha" in list(result_df.columns):
    #     plot_lineplot(session=session_label, data=result_df, x="time frame", y="cell count", hue="propulsion alpha",
    #                   style=None, show=show, dpi=dpi)
    #     plot_lineplot(session=session_label, data=result_df, x="time frame", y="cell count", hue="cell division rate",
    #                   style=None, show=show, dpi=dpi)
    #     print_log("Last time frame index: {}".format(max(result_df["time frame"])))
    #     result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="cell division rate",
    #                  columns="propulsion alpha", values="cell count", show=show, dpi=dpi)
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="cell division rate",
    #                  columns="propulsion alpha", values="radius of gyration", show=show, dpi=dpi)
    #
    # if "potential re factor" in list(result_df.columns) and "propulsion alpha" in list(result_df.columns):
    #     print_log("Last time frame index: {}".format(max(result_df["time frame"])))
    #     result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="potential re factor",
    #                  columns="propulsion alpha", values="cell count", show=show, dpi=dpi)
    #     plot_heatmap(session=session_label, data=result_df_last_time, rows="potential re factor",
    #                  columns="propulsion alpha", values="radius of gyration", show=show, dpi=dpi)
    #
    # if "potential re factor" in list(result_df.columns) and "cell division rate" in list(result_df.columns):
    #     print_log("Last time frame index: {}".format(max(result_df["time frame"])))
    #     result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
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
    # try:
    #     session_root = os.listdir(root)
    #     for session_folder in session_root:
    #         print_log(f"-- {session_folder} --")
    #         analyse_folder(root, session_folder, vars_select, result_folder, dpi)
    # except Exception as error:
    #     print("An error occured during analysis, e.g. folder not found!")
    #     print(type(error).__name__, "–", error)

    session_root = os.listdir(root)
    for session_folder in session_root:
        print_log(f"-- {session_folder} --")
        analyse_folder(root, session_folder, vars_select, result_folder, dpi)
