"""
Collection of independent functions for data import, conversion, transport and export.
Author: Konstantinos Andreadis
"""

import pandas as pd
import numpy as np


def read_dat(path):
    data = pd.read_csv(path, header=0, sep='\s+')
    colshift = {}
    temp = data.columns
    for u in range(len(temp) - 1):
        colshift[temp[u]] = temp[u + 1]
    data.rename(columns={temp[len(temp) - 1]: 'none'}, inplace=True)
    data.rename(columns=colshift, inplace=True, errors="raise")
    return data


def read_xyz(data, group_index):
    data = data.groupby("type").get_group(group_index)
    xcoords = data["x"].to_numpy()
    ycoords = data["y"].to_numpy()
    zcoords = data["z"].to_numpy()
    return np.column_stack([xcoords, ycoords, zcoords])


def add_result(target, tag, item):
    try:
        target[tag].append(item)
    except:
        target[tag] = []
        target[tag].append(item)


def add_var(target, var_list, var_short, var_long, var_type=float):
    for var in var_list:
        if var_short in var:
            if var_type == int:
                var_val = int(float(var.split("-")[-1]))
            else:
                var_val = float(var.split("-")[-1])
            add_result(target=target, tag=var_long, item=var_val)
