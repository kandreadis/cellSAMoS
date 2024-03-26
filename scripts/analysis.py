"""
Collection of independent functions that analyse (geometric) properties.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import numpy as np


# from numba import njit

def calc_radius_gyration(xyz):
    """
    Calculates radius of gyration for a set of xyz coordinates given as numpy matrix Nx3
    """
    return np.sqrt(np.sum(np.square(xyz)) / len(xyz))


def cm_removal(tnxyz):
    """
    Removes the center of mass for a set of xyz coordinates given as numpy matrix txNx3
    """
    tr = np.sqrt(np.sum(np.square(tnxyz), axis=2))
    txyz_cm = np.zeros_like(tnxyz)
    for t_i, xyz in enumerate(tnxyz):
        txyz_cm[t_i] = np.average(xyz, axis=0, weights=tr[t_i])
    tnxyz -= txyz_cm
    return tnxyz


def periodic_unwrap(tnxyz, L):
    """
    According to box size and periodicity (L), this function "unwraps" a set of xyz coordinates
    given as numpy matrix txNx3
    """
    for t_i in range(1, tnxyz.shape[0]):
        nxyz_diff = tnxyz[t_i] - tnxyz[t_i - 1]
        tnxyz[t_i, nxyz_diff <= -L / 2] += L
        tnxyz[t_i, nxyz_diff >= L / 2] -= L
    return tnxyz


def calc_msd(tnxyz, L, t, tau, freqdt, substract_CM=False, debug=False):
    """
    Calculates the mean squared displacement (MSD) as a function of time for a set of xyz
    coordinates given as numpy matrix txNx3
    """
    if substract_CM:
        tnxyz = cm_removal(tnxyz)
    tnxyz = periodic_unwrap(tnxyz=tnxyz, L=L)

    if tau > freqdt > 1:
        delta_t_sep = tau
    else:
        delta_t_sep = freqdt

    delta_t = np.arange(freqdt, np.max(t), delta_t_sep)

    if debug:
        print("tau:", tau)
        print("freq*dt:", freqdt)
        print("t:", t)
        print("delta_t:", delta_t)
    tmsd = []
    tmsderr = []
    for delta_t_i, delta_t_val in enumerate(delta_t):
        if debug:
            print("Delta t:", delta_t_val)
        msd_delta_t = []
        for t_val in t:
            if t_val + delta_t_val <= np.max(t):
                t_val_index = t_val / freqdt
                delta_t_val_index = delta_t_val / freqdt
                displacement = np.linalg.norm(tnxyz[int(t_val_index + delta_t_val_index)] - tnxyz[int(t_val_index)],
                                              axis=1)
                msd_delta_t.append(np.mean(np.square(displacement)))
        msd_delta_t = np.asarray(msd_delta_t)
        tmsd.append(np.mean(msd_delta_t))
        tmsderr.append(np.std(msd_delta_t) / np.sqrt(len(msd_delta_t)))

    if debug:
        print("tmsd:", tmsd)

    # delta_t = np.unique(np.round((np.logspace(0, round(np.log10(np.max(t))) - 1, endpoint=False))).astype(
    #     int) * freqdt)
    #
    # if freqdt > tau:
    #     tau = freqdt
    # tau = 10 ** np.floor(np.log10(tau))
    # t0 = np.arange(0, np.max(t) - np.max(delta_t) + 1, tau)
    #
    # tmsd = []
    # for delta_t_i, delta_t_val in enumerate(delta_t):
    #     msd_t0 = np.empty_like(t0)
    #     for t0_i, t0_val in enumerate(t0):
    #         t0_idx = np.isclose(t, t0_val).nonzero()[0]
    #         t0_delta_t_idx = np.isclose(t, t0_val + delta_t_val).nonzero()[0]
    #         msd_t0[t0_i] = np.mean(np.square(np.linalg.norm(tnxyz[t0_delta_t_idx] - tnxyz[t0_idx], axis=2)), axis=1)
    #
    #     # print(delta_t_i, np.mean(msd_t0))
    #     tmsd.append(np.mean(msd_t0))
    # tmsd = np.asarray(tmsd)

    # tmsd = np.mean(np.square(np.linalg.norm(tnxyz - tnxyz[0], axis=2)), axis=1)
    # delta_t = t

    return delta_t, tmsd, tmsderr


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
    if len(r) == 1:
        return np.array([]), np.array([]), None, None
    else:
        r_max = np.max(r)
        dr = 2 * np.average(radius)
        r_bins = np.arange(dr, r_max + dr, dr)
        shell_surface = 4 * np.pi * r_bins ** 2
        shell_volume = dr * shell_surface
        in_shell = (r_bins - dr / 2 <= r[:, np.newaxis]) & (r[:, np.newaxis] <= r_bins + dr / 2)
        particles_volume = np.einsum("ij, i->j", in_shell, (4 / 3) * np.pi * radius ** 3)
        phi = particles_volume / shell_volume
        phi /= np.max(phi)
        try:
            r_core = min(r_bins[phi <= 1 / np.e])
        except:
            r_core = None
        r_invasion = r_max
        return r_bins, phi, r_core, r_invasion
