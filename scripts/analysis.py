"""
Collection of independent functions that analyse (geometric) properties.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import numpy as np
from scipy.optimize import curve_fit


# from numba import njit

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


# @njit
def calc_msd(tnxyz, L, t, tau, freqdt, substract_CM=False, debug=False):
    """
    Calculates the mean squared displacement (MSD) as a function of time for a set of xyz
    coordinates given as numpy matrix txNx3
    """
    if substract_CM:
        tr = np.sqrt(np.sum(np.square(tnxyz), axis=2))
        txyz_cm = np.zeros_like(tnxyz)
        for t_i, xyz in enumerate(tnxyz):
            txyz_cm[t_i] = np.average(xyz, axis=0, weights=tr[t_i])
        tnxyz -= txyz_cm
    for t_i in range(1, tnxyz.shape[0]):
        nxyz_diff = tnxyz[t_i] - tnxyz[t_i - 1]
        tnxyz[t_i, nxyz_diff <= -L / 2] += L
        tnxyz[t_i, nxyz_diff >= L / 2] -= L

    # np.mean(np.square(np.linalg.norm(tnxyz - tnxyz[0], axis=2)), axis=1)

    delta_t = np.unique(np.round((np.logspace(0, round(np.log10(np.max(t))) - 1, endpoint=False))).astype(
        int) * freqdt)

    if freqdt > tau:
        tau = freqdt
    tau = 10**np.floor(np.log10(tau))
    t0 = np.arange(0, np.max(t) - np.max(delta_t) + 1, tau)
    if debug:
        print("tau:", tau)
        print("freq*dt:", freqdt)
        print("t:", t)
        print("delta_t:", delta_t)
        print("t_0:", t0)
    tmsd = []
    for delta_t_i, delta_t_val in enumerate(delta_t):
        msd_t0 = np.empty_like(t0)
        for t0_i, t0_val in enumerate(t0):
            t0_idx = np.isclose(t, t0_val).nonzero()[0]
            t0_delta_t_idx = np.isclose(t, t0_val + delta_t_val).nonzero()[0]
            msd_t0[t0_i] = np.mean(np.square(np.linalg.norm(tnxyz[t0_delta_t_idx] - tnxyz[t0_idx], axis=2)), axis=1)

        # print(delta_t_i, np.mean(msd_t0))
        tmsd.append(np.mean(msd_t0))
    tmsd = np.asarray(tmsd)
    return delta_t, tmsd


def calc_msd_fit(tmsd):
    """
    Fits a line through the mean squared displacement (MSD) given as numpy array with length t
    """
    log_time = np.log10(np.arange(0, len(tmsd)))[1:]
    log_msd = np.log10(tmsd)[1:]
    popt, pcov = curve_fit(linear_fit, log_time, log_msd)
    log_slope = popt[0]
    log_offset = popt[1]

    tmsd_fit = np.zeros_like(tmsd)
    tmsd_fit[1:] = 10 ** (log_time * log_slope + log_offset)
    return tmsd_fit, log_slope


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
    r_bins = np.arange(dr, r_max + dr, dr)
    shell_surface = 4 * np.pi * r_bins ** 2
    shell_volume = dr * shell_surface
    in_shell = (r_bins - dr / 2 <= r[:, np.newaxis]) & (r[:, np.newaxis] <= r_bins + dr / 2)
    particles_volume = np.einsum("ij, i->j", in_shell, (4 / 3) * np.pi * radius ** 3)
    phi = particles_volume / shell_volume
    dphidr = np.gradient(phi)
    r_core = np.argmin(dphidr)
    return r_bins, phi, dphidr, r_core


def calc_radius_fit(r):
    """
    Calculates the core, max and standard deviation (of) radii for a set of radii as numpy matrix N
    """
    r_core = np.median(r)
    r_max = np.max(r)
    r_std = np.std(r)
    return r_core, r_max, r_std
