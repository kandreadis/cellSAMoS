"""
Collection of independent functions that analyse (geometric) properties.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import numpy as np


def calc_radius_gyration(xyz_coords):
    """
    Calculates radius of gyration for a set of xyz coordinates given as numpy matrix Nx3
    """
    return np.sqrt(np.sum(np.square(xyz_coords)) / len(xyz_coords))

def calc_cell_count(xyz_coords):
    """
    Calculates number of cells for a set of xyz coordinates given as numpy matrix Nx3
    """
    return len(xyz_coords)