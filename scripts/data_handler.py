"""
Collection of independent functions for data import, conversion, transport and export.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import pandas as pd
import numpy as np
import os, json
from scripts.communication_handler import print_log
import ast


def save_dict(params_dict, path):
    """
    Save Python dictionary as json file
    """
    try:
        with open(os.path.join(path, "params.json"), "w") as jsonfile:
            json.dump(params_dict, jsonfile, indent=4)
    except:
        print_log("Could not save dictionary...")


def read_params_dict(path):
    """
    Read Python dictionary from json file
    """
    try:
        with open(os.path.join(path, "params.json"), "r") as jsonfile:
            params = json.load(jsonfile)
    except:
        print_log("Could not open dictionary...")
        params = {}
    return params


def combine_datasets(input_dir, output_dir):
    """
    Combine panda dataframes into output dataframe.
    """
    pd_input = [pd.read_csv(os.path.join(input_dir, path, "measurements.csv")) for path in os.listdir(input_dir)]
    pd.concat(pd_input).to_csv(os.path.join(output_dir, "measurements.csv"))
    print_log(f"Combined {len(input_dir)} dataframes into one in {output_dir} !")


def read_dat(path):
    """
    Read a .dat file and shift its columns to properly import data as dataFrame.
    """
    data = pd.read_csv(path, header=0, sep='\s+')
    colshift = {}
    temp = data.columns
    for u in range(len(temp) - 1):
        colshift[temp[u]] = temp[u + 1]
    data.rename(columns={temp[len(temp) - 1]: 'none'}, inplace=True)
    data.rename(columns=colshift, inplace=True, errors="raise")
    return data


def read_xyz(data, group_index):
    """
    For a given cell group, retrieve all xyz cell positions.
    """
    data = data.groupby("type").get_group(group_index)
    xcoords = data["x"].to_numpy()
    ycoords = data["y"].to_numpy()
    zcoords = data["z"].to_numpy()
    return np.column_stack([xcoords, ycoords, zcoords])


def read_vel(data, group_index):
    """
    For a given cell group, retrieve all xyz velocity components.
    """
    data = data.groupby("type").get_group(group_index)
    velx = data["vx"].to_numpy()
    vely = data["vy"].to_numpy()
    velz = data["vz"].to_numpy()
    return np.column_stack([velx, vely, velz])


def read_radii(data, group_index):
    """
    For a given cell group, retrieve all xyz cell positions.
    """
    data = data.groupby("type").get_group(group_index)
    return data["radius"].to_numpy()


def add_result(target, tag, item):
    """
    Add a result to a target dictionary, and create the category if not yet pre-existing.
    """
    try:
        target[tag].append(item)
    except:
        target[tag] = []
        target[tag].append(item)


def add_vars(target, var_list, vars_select):
    """
    Extract and format parameter values, and save them to a result dictionary.
    """
    for varsel in vars_select:
        for varavail in var_list:
            if varsel == varavail.split("-")[0]:
                if vars_select[varsel][1] == int:
                    var_val = int(float(varavail.split("-")[-1]))
                else:
                    var_val = float(varavail.split("-")[-1])
                add_result(target=target, tag=varsel, item=var_val)


def import_resultdf(res_root_dir, name):
    """
    Import a result dataframe
    """
    try:
        result_df = pd.read_csv(os.path.join(res_root_dir, name))
    except:
        print_log("Not yet processed, run -analysis first!")
        return None

    for key in result_df.keys():
        try:
            if result_df[key][0][0] == "[":
                result_df[key] = result_df[key].apply(ast.literal_eval)
        except:
            pass
    return result_df


def read_dr_l(var_list):
    """
    Read Dr and L from a variable list
    """
    Dr = 0.1
    L = 100.0
    for var in var_list:
        if "Dr" in var:
            Dr = float(var.split("-")[1])
        if "L" in var:
            L = float(var.split("-")[1])
    return Dr, L


def dict2dataframe(measurement_dict):
    """
    Converts dictionary to a dataframe
    """
    df = pd.DataFrame.from_dict(measurement_dict, orient="columns")
    return df


def dataframe2csv(res_root_dir, df, csv_filename):
    """
    Converts dataframe to csv spreadsheet
    """
    try:
        os.makedirs(res_root_dir)
    except:
        pass

    df.to_csv(os.path.join(res_root_dir, csv_filename), index=False)
