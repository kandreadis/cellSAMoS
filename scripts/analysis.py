"""
Collection of independent functions that analyse (geometric) properties.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import numpy as np
from scipy.optimize import curve_fit


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


def linear_fit(x, a, b):
    """
    Linear fitting function with slope a and offset b
    """
    return a * x + b


def calc_msd(txyz):
    """
    Calculates the mean squared displacement (MSD) as a function of time for a set of xyz
    coordinates given as numpy matrix txNx3
    """
    tr = np.sqrt(np.sum(np.square(txyz), axis=2))
    txyz_cm = np.zeros_like(txyz)
    for t_i, xyz in enumerate(txyz):
        txyz_cm[t_i] = np.average(xyz, axis=0, weights=tr[t_i])
    txyz -= txyz_cm
    tmsd = np.mean(np.square(np.linalg.norm(txyz - txyz[0], axis=2)), axis=1)
    log_time = np.log10(np.arange(0, len(tmsd)))[1:]
    log_msd = np.log10(tmsd)[1:]
    popt, pcov = curve_fit(linear_fit, log_time, log_msd)
    log_slope = popt[0]
    log_offset = popt[1]

    tmsd_fit = np.zeros_like(tmsd)
    tmsd_fit[1:] = 10 ** (log_time * log_slope + log_offset)
    return tmsd, tmsd_fit, log_slope


def calc_r(xyz):
    """
    Calculates the distances for a set of xyz coordinates given as numpy matrix Nx3 wrt. the COM
    """
    r = np.sqrt(np.sum(np.square(xyz), axis=1))
    xyz_cm = np.average(xyz, axis=0, weights=r)
    xyz -= xyz_cm
    return np.sqrt(np.sum(np.square(xyz), axis=1))


def calc_phi(r, radius):
    """
    Calculates the density profile for a set of distances (wrt. C.M.) and radii, both numpy matrices with length N
    """
    r_max = np.max(r)
    dr = 2 * np.average(radius)

    r_bins = np.arange(0, r_max + dr, dr)
    shell_surface = 4 * np.pi * r_bins ** 2
    shell_volume = dr * shell_surface
    in_shell = (r_bins - dr / 2 <= r[:, np.newaxis]) & (r[:, np.newaxis] <= r_bins + dr / 2)

    particles_volume = np.einsum("ij, i->j", in_shell, (4 / 3) * np.pi * radius ** 3)
    np.seterr(invalid='ignore', divide="ignore")
    phi = particles_volume / shell_volume
    return r_bins, phi


def calc_radius_fit(r):
    """
    Calculates the core, max and standard deviation (of) radii for a set of radii as numpy matrix N
    """
    r_core = np.median(r)
    r_max = np.max(r)
    r_std = np.std(r)
    return r_core, r_max, r_std
