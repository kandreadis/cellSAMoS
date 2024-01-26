"""
Collection of independent functions that analyse (geometric) properties.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import numpy as np
import matplotlib.pyplot as plt


def calc_radius_gyration(xyz):
    """
    Calculates radius of gyration for a set of xyz coordinates given as numpy matrix Nx3
    """
    return np.sqrt(np.sum(np.square(xyz)) / len(xyz))


def calc_cell_count(xyz):
    """
    Calculates number of cells for a set of xyz coordinates given as numpy matrix Nx3
    """
    return len(xyz)


def calc_msd(txyz):
    """
    Calculates the mean squared displacement (MSD) as a function of time for a set of xyz
    coordinates given as numpy matrix txNx3
    """
    return np.mean(np.square(np.linalg.norm(txyz - txyz[0], axis=2)), axis=1)


def calc_r(xyz):
    """
    Calculates the distances for a set of xyz coordinates given as numpy matrix Nx3 wrt. the COM
    """
    r = np.sqrt(np.sum(np.square(xyz), axis=1))
    xyz_cm = np.average(xyz, axis=0, weights=r)
    return np.sqrt(np.sum(np.square(xyz - xyz_cm), axis=1))


def calc_phi(r, radius):
    """
    Calculates the density profile for a set of distances (wrt. C.M.) and radii, both numpy matrices with length N
    """
    r_max = np.max(r)
    dr = 2 * np.average(radius)
    r_bins = np.arange(dr / 2, r_max, dr)
    phi = np.zeros_like(r_bins)
    for i, r_i in enumerate(r_bins):
        shell_volume = dr * 4 * np.pi * r_i ** 2
        in_shell = (r_i - dr / 2 <= r) & (r <= r_i + dr / 2)
        particles_volume = np.sum((4 / 3) * np.pi * radius[in_shell] ** 3)
        phi[i] = particles_volume / shell_volume
    return r_bins, phi


def calc_radius_fit(r):
    """
    Calculates the core, max and standard deviation (of) radii for a set of radii as numpy matrix N
    """
    r_core = np.median(r)
    r_max = np.max(r)
    r_std = np.std(r)
    return r_core, r_max, r_std
