"""
Collection of independent functions that analyse geometrical properties.
Author: Konstantinos Andreadis
"""

import numpy as np


def calc_radius_gyration(xyz_coords):
    return np.sqrt(np.sum(np.square(xyz_coords)) / len(xyz_coords))
