"""
Collection of independent functions for data import, conversion, transport and export.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import pandas as pd
import numpy as np


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


def add_var(target, var_list, var_short, var_long, var_type=float):
    """
    Extract and format parameter values, and save them to a result dictionary.
    """
    for var in var_list:
        if var_short == var.split("-")[0]:
            if var_type == int:
                var_val = int(float(var.split("-")[-1]))
            else:
                var_val = float(var.split("-")[-1])
            add_result(target=target, tag=var_long, item=var_val)
