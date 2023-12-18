"""
Initialisation of spheroid cells for SAMoS.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis.
"""
from datetime import *

import matplotlib.pyplot as plt
import numpy as np
from scripts.communication_handler import print_log


def save_initial_cells(cells_data, outfile):
    """
    Writes a .txt file containing the initial particle configuration.
    """
    gentime = datetime.now()
    out = open(outfile, 'w')
    out.write('# Total of %s cells\n' % str(len(cells_data)))
    out.write('# Generated on : %s\n' % str(gentime))
    out.write('# id  type radius  x   y   z   vx   vy   vz   nx   ny   nz\n')
    for p in cells_data:
        x, y, z = p.cell_position
        vx, vy, vz = p.cell_velocity
        nx, ny, nz = p.cell_direction
        out.write(
            '%d  %d  %f %f  %f  %f  %f  %f  %f  %f  %f  %f\n' % (
                p.cell_idx, p.group_idx, p.cell_radius, x, y, z, vx, vy, vz, nx, ny, nz))
    out.close()
    print_log(f"Saved cells to {outfile}!")


class Cell:
    """
    A single cell is created.
    """

    def __init__(self, cell_idx=0, group_idx=1, cell_radius=1.0):
        self.cell_idx = cell_idx
        self.group_idx = group_idx
        self.cell_radius = cell_radius
        self.cell_position = [0.0, 0.0, 0.0]
        self.cell_velocity = [0.0, 0.0, 0.0]
        self.cell_direction = [0.0, 0.0, 0.0]


class Spheroid:
    """
    A spheroid is initialised using a population(collective) of cells.
    """

    def __init__(self, cell_count, cell_radius, poly, add_tracker_cells, tracker_cell_count):
        self.N = cell_count
        self.poly = poly
        self.add_tracker_cells = add_tracker_cells
        self.Ntracker = tracker_cell_count
        self.cell_radius = cell_radius
        if self.add_tracker_cells:
            self.R = ((self.N + self.Ntracker) / 0.74) ** (1 / 3) * self.cell_radius
            self.cells = [Cell(cell_idx=i, group_idx=1) for i in range(int(self.N))]
            self.cells.extend(Cell(cell_idx=j, group_idx=2) for j in range(int(self.Ntracker)))
        else:
            self.R = (self.N / 0.74) ** (1 / 3) * self.cell_radius
            self.cells = [Cell(cell_idx=i, group_idx=1) for i in range(int(self.N))]

        def un(a, b):
            """
            Uniform distribution draw between a and b.
            """
            return np.random.uniform(a, b)

        for cell in self.cells:
            phi = un(0, 2 * np.pi)
            costheta = un(-1, 1)
            theta = np.arccos(costheta)
            r = self.R * un(0, 1) ** (1. / 3.)
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)

            vx, vy, vz = 0, 0, 0
            phi = un(0, 2 * np.pi)
            costheta = un(-1, 1)
            nx = np.cos(phi) * np.sin(np.arccos(costheta))
            ny = np.sin(phi) * np.sin(np.arccos(costheta))
            nz = costheta
            if cell.group_idx == 2:
                cell.cell_radius = self.cell_radius
            else:
                cell.cell_radius = self.cell_radius * un(1 - 0.5 * self.poly, 1 + 0.5 * self.poly)
            cell.cell_position = [x, y, z]
            cell.cell_velocity = [vx, vy, vz]
            cell.cell_direction = [nx, ny, nz]


def plot_initial_cells(particles_list):
    """
    Basic 3D visualisation of initial cell configuration for debugging purposes.
    """
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection='3d')
    for particle in particles_list:
        ax.scatter(*particle.cell_position, c=particle.group_idx, s=100, alpha=0.6)
    plt.show()
