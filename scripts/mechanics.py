"""
Collection of independent functions that analyse (geometric) properties.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
*****************************************************************************
*
*  New analysis code that calculates force, stress, traction and pressure
*  for each particle i and its neighbours j per SAMoS simulation time step
*  based on equations and SAMoSA from Silke.
* 
*****************************************************************************
"""

import numpy as np


def find_neighbours(particle_i, all_particles, params):
    """
    For a particle i inside all particles this function finds all neighbouring particles j
    given the dict params.
    """
    particle_j = None
    return particle_j


def calc_drvec(particle_i, particle_j, params):
    """
    Calculates the vector between particles i and j
    """
    drvec_ij = np.array([0.0, 0.0, 0.0])
    drmag_ij = np.linalg.norm(drvec_ij)
    return drvec_ij, drmag_ij


def calc_forcevec(particle_i, particle_j, params):
    """
    Calculates the passive and active force between particles i and j given dict params
    """
    drvec_ij = calc_drvec(particle_i=particle_i, particle_j=particle_j, params=params)
    drmag_ij = np.linalg.norm(drvec_ij)
    # Passive force
    passive_forcevec_ij = 0.0

    # scale=radi+radj
    # diff=scale-dr
    # dscaled=diff/scale
    # rep = [index for index, value in enumerate(dscaled) if value > -self.fact]
    # #print "Before upshot ones: " + str(len(rep))
    # att = [index for index, value in enumerate(dscaled) if value <= -self.fact]
    # #print "Attractive after upshot ones: " + str(len(att))
    # factor=np.empty((len(neighbours),))
    # # repulsive ones
    # factor[rep] = self.k*diff[rep]
    # # attractive ones
    # factor[att]=-self.k*(self.rmax*scale[att]-dr[att])
    # Fvec=((factor/dr).transpose()*(drvec).transpose()).transpose()

    # Active force
    active_forcevec_ij = 0.0
    return passive_forcevec_ij, active_forcevec_ij


def calc_stress(particle_i, drvec_ij, forcevec_ij):
    """
    Calculates the passive and active stress on particle i
    """
    # Passive Stress
    passive_stress_i = 0.0
    # Active Stress
    active_stress_i = 0.0
    return passive_stress_i, active_stress_i


def calc_traction(particle_i, passive_stress_i, active_stress_i):
    """
    Calculates the passive and active traction on particle i 
    """
    surface_normalvec_i = None
    # Passive Traction
    passive_traction_i = 0.0
    # Active Traction
    active_traction_i = 0.0
    return passive_traction_i, active_traction_i


def calc_pressure(particle_i, passive_stress_i, active_stress_i):
    """
    Calculates the passive and active pressure on particle i 
    """
    # Passive Pressure
    passive_pressure_i = np.trace(passive_stress_i)
    # Active Pressure
    active_pressure_i = np.trace(active_stress_i)
    return passive_pressure_i, active_pressure_i


def analyse_mechanics(particle_i, params, all_particles):
    """
    For each particle i analyse its mechanics.
    """
    all_particle_j = find_neighbours(particle_i=particle_i, all_particles=all_particles, params=params)
    for particle_j in all_particle_j:
        drvec_ij, drmag_ij = calc_drvec(particle_i=particle_i, particle_j=particle_j, params=params)
        # Calculate the force
        # Calculate the stress
        # Calculate the traction
        # Calculate the pressure
