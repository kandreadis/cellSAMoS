"""
Visualisation and Analysis of SAMoS simulation results.
Author: Konstantinos Andreadis
"""

import os, sys
import numpy as np
import pandas as pd
from scripts.data_handler import read_dat, read_xyz, add_result, add_var
from scripts.visualisation import plot_heatmap, plot_scatterplot, plot_lineplot, plot_boxplot
from scripts.analyse_geometry import calc_radius_gyration

from scripts.communication_handler import Logger
sys.stdout = Logger()

print("=== Start ===")

def analyse_folder(root, path):
    result_folder_path = os.path.join(root, path)
    analysis_result_dict = {}
    result_folder_subdirs = os.listdir(result_folder_path)
    result_folder_subdirs_num = len(result_folder_subdirs)
    print(f"Found {result_folder_subdirs_num} folders in {result_folder_path}")
    for idx, output_dir in enumerate(result_folder_subdirs):
        process_progress = round(100*(idx+1)/result_folder_subdirs_num)
        if process_progress in np.arange(0,125,25):
            print(f"Processing {process_progress}%...")
        folder_path = os.path.join(result_folder_path, output_dir)
        dat_files = [f for f in os.listdir(folder_path) if f.endswith(".dat")]
        if len(dat_files) == 0:
            break
        vars = output_dir.split("_")
        
        for dat_dir in dat_files:
            dat_file_dir = os.path.join(result_folder_path, output_dir, dat_dir)
            dat_content = read_dat(path=dat_file_dir)
            time_index = int(os.path.splitext(os.path.basename(dat_file_dir))[0].split("_")[-1])
            positions = read_xyz(data=dat_content, group_index=1)

            add_result(target=analysis_result_dict,tag="dir",item=output_dir)
            add_result(target=analysis_result_dict,tag=".data dir",item=dat_dir)
            add_result(target=analysis_result_dict,tag="cell count",item=len(positions))
            add_result(target=analysis_result_dict,tag="radius of gyration",item=calc_radius_gyration(positions))
            add_result(target=analysis_result_dict,tag="time frame",item=time_index)
            
            for item in vars_select.values():
                add_var(target=analysis_result_dict, vars=vars, var_short=item[0], var_long=item[1], var_type=item[2])

    result_df = pd.DataFrame.from_dict(analysis_result_dict,orient="columns")
    print("Result dataframe shape:",result_df.shape)
    print(list(result_df.columns))
    print("----")

    show = False
    plot_boxplot(session=path, data=result_df, x="time frame", y="cell count", hue=None, show=show)
    plot_lineplot(session=path, data=result_df, x="time frame", y="radius of gyration", hue=None, style=None, show=show)

    if "potential re factor" in list(result_df.columns):
        plot_lineplot(session=path, data=result_df, x="time frame", y="cell count", hue="potential re factor", style=None, show=show)
        plot_scatterplot(session=path,data=result_df,x="potential re factor", y="radius of gyration", hue="time frame", style=None, show=show)

    if "cell division rate" in list(result_df.columns) and "propulsion alpha" in list(result_df.columns):
        plot_lineplot(session=path, data=result_df, x="time frame", y="cell count", hue="propulsion alpha", style=None, show=show)
        plot_lineplot(session=path, data=result_df, x="time frame", y="cell count", hue="cell division rate", style=None, show=show)
        result_df_last_time = result_df.groupby("time frame").get_group(30000)
        plot_heatmap(session=path,data=result_df_last_time,rows="cell division rate", columns="propulsion alpha",values="cell count", show=show)
        plot_heatmap(session=path,data=result_df_last_time,rows="cell division rate", columns="propulsion alpha", values="radius of gyration", show=show)

def analyse_root_subfolders(path):
    print(f"|| {path} ||")
    result_sessions = os.listdir(path)
    for result_batch_root in result_sessions:
        print(f"-- {result_batch_root} --")
        analyse_folder(path, result_batch_root)

vars_select = {
    0:["N", "initial cell count", int],
    1:["t", "# time steps", int],
    2:["div", "cell division rate", float],
    3:["alpha", "propulsion alpha", float],
    4:["re", "potential re factor", float],
}

result_root = "/data1/andreadis/samos_output/20231208"
analyse_root_subfolders(result_root)

result_root = "/data1/andreadis/samos_output/20231211"
analyse_root_subfolders(result_root)

result_root = "/data1/andreadis/samos_output/20231212"
analyse_root_subfolders(result_root)

print("=== End ===")