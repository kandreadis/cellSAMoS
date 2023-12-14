"""
Collection of functions that perform batch analysis of SAMoS simulation results.
Author: Konstantinos Andreadis
"""
import os
import numpy as np
import pandas as pd
from scripts.data_handler import read_dat, read_xyz, add_result, add_var
from scripts.visualisation import plot_heatmap, plot_scatterplot, plot_lineplot, plot_boxplot
from scripts.analyse_geometry import calc_radius_gyration
from scripts.communication_handler import print_log


def analyse_folder(root, path, vars_select):
    result_folder_path = os.path.join(root, path)
    analysis_result_dict = {}
    result_folder_subdirs = os.listdir(result_folder_path)
    result_folder_subdirs_num = len(result_folder_subdirs)
    print_log(f"Found {result_folder_subdirs_num} folders in {result_folder_path}")
    for idx, output_dir in enumerate(result_folder_subdirs):
        process_progress = round(100 * (idx + 1) / result_folder_subdirs_num)
        if process_progress in np.arange(0, 125, 25):
            print_log(f"Processing {process_progress}%...")
        folder_path = os.path.join(result_folder_path, output_dir)
        dat_files = [f for f in os.listdir(folder_path) if f.endswith(".dat")]
        if len(dat_files) == 0:
            break
        var_list = output_dir.split("_")

        for dat_dir in dat_files:
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            time_index = int(os.path.splitext(os.path.basename(dat_file_dir))[0].split("_")[-1])
            positions = read_xyz(data=dat_content, group_index=1)

            add_result(target=analysis_result_dict, tag="dir", item=output_dir)
            add_result(target=analysis_result_dict, tag=".data dir", item=dat_dir)
            add_result(target=analysis_result_dict, tag="cell count", item=len(positions))
            add_result(target=analysis_result_dict, tag="radius of gyration", item=calc_radius_gyration(positions))
            add_result(target=analysis_result_dict, tag="time frame", item=time_index)

            for item in vars_select.values():
                add_var(target=analysis_result_dict, var_list=var_list, var_short=item[0], var_long=item[1],
                        var_type=item[2])

    result_df = pd.DataFrame.from_dict(analysis_result_dict, orient="columns")
    print_log(f"Result dataframe shape:{result_df.shape}")
    print_log(list(result_df.columns))
    print_log("----")

    show = False
    plot_boxplot(session=path, data=result_df, x="time frame", y="cell count", hue=None, show=show)
    plot_lineplot(session=path, data=result_df, x="time frame", y="radius of gyration", hue=None, style=None, show=show)

    if "potential re factor" in list(result_df.columns):
        plot_lineplot(session=path, data=result_df, x="time frame", y="cell count", hue="potential re factor",
                      style=None, show=show)
        plot_scatterplot(session=path, data=result_df, x="potential re factor", y="radius of gyration",
                         hue="time frame", style=None, show=show)

    if "cell division rate" in list(result_df.columns) and "propulsion alpha" in list(result_df.columns):
        plot_lineplot(session=path, data=result_df, x="time frame", y="cell count", hue="propulsion alpha", style=None,
                      show=show)
        plot_lineplot(session=path, data=result_df, x="time frame", y="cell count", hue="cell division rate",
                      style=None, show=show)
        print_log("Last time frame index: {}".format(max(result_df["time frame"])))
        result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
        plot_heatmap(session=path, data=result_df_last_time, rows="cell division rate", columns="propulsion alpha",
                     values="cell count", show=show)
        plot_heatmap(session=path, data=result_df_last_time, rows="cell division rate", columns="propulsion alpha",
                     values="radius of gyration", show=show)
    if "potential re factor" in list(result_df.columns) and "propulsion alpha" in list(result_df.columns):
        print_log("Last time frame index: {}".format(max(result_df["time frame"])))
        result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
        plot_heatmap(session=path, data=result_df_last_time, rows="potential re factor", columns="propulsion alpha",
                     values="cell count", show=show)
        plot_heatmap(session=path, data=result_df_last_time, rows="potential re factor", columns="propulsion alpha",
                     values="radius of gyration", show=show)
    if "potential re factor" in list(result_df.columns) and "cell division rate" in list(result_df.columns):
        print_log("Last time frame index: {}".format(max(result_df["time frame"])))
        result_df_last_time = result_df.groupby("time frame").get_group(max(result_df["time frame"]))
        plot_heatmap(session=path, data=result_df_last_time, rows="potential re factor", columns="cell division rate",
                     values="cell count", show=show)
        plot_heatmap(session=path, data=result_df_last_time, rows="potential re factor", columns="cell division rate",
                     values="radius of gyration", show=show)


def analyse_root_subfolders(path, vars_select):
    print_log(f"|| {path} ||")
    result_sessions = os.listdir(path)
    for result_batch_root in result_sessions:
        print_log(f"-- {result_batch_root} --")
        analyse_folder(path, result_batch_root, vars_select)
