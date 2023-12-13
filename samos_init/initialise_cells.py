"""
Initialisation of spheroid cells for SAMoS.
Author: Konstantinos Andreadis.
"""
import argparse
from datetime import *

import matplotlib.pyplot as plt
import numpy as np
from scripts.communication_handler import print_log


def parse_user_input():
    """
    Parse user input parameters when running this script using bash commands (terminal).
    :return: Default/chosen run parameters
    :rtype: Parser arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-N", "--cell_count", type=int, default=500, help="number of cells")
    parser.add_argument("-R", "--spheroid_radius", type=float, default=8.735, help="sphere radius")
    parser.add_argument("-r", "--cell_radius", type=float, default=1.0, help="cell radius")
    parser.add_argument("-o", "--output_file", type=str, default='out.txt', help="output file")
    parser.add_argument("-plot", "--plotconfig", action='store_true', default=False, help="plot configuration?")
    return parser.parse_args()


def save_initial_cells(cells_data, outfile):
    """
    This function writes a .txt file containing the initial particle configuration.
    :param cells_data: Initial cell configuration
    :type cells_data: See custom format in class Cell
    :param outfile: Path
    :type outfile: String
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

    def __init__(self, spheroid_radius, cell_count, cell_radius, poly):
        self.R = spheroid_radius
        self.N = cell_count
        self.poly = poly

        self.cells = [Cell(cell_idx=i, group_idx=1) for i in range(int(cell_count))]

        def un(a, b):
            return np.random.uniform(a, b)

        for cell in self.cells:
            phi = un(0, 2 * np.pi)
            costheta = un(-1, 1)
            theta = np.arccos(costheta)
            r = spheroid_radius * un(0, 1) ** (1. / 3.)
            x = r * np.sin(theta) * np.cos(phi)
            y = r * np.sin(theta) * np.sin(phi)
            z = r * np.cos(theta)

            vx, vy, vz = 0, 0, 0
            phi = un(0, 2 * np.pi)
            costheta = un(-1, 1)
            nx = np.cos(phi) * np.sin(np.arccos(costheta))
            ny = np.sin(phi) * np.sin(np.arccos(costheta))
            nz = costheta
            cell.cell_radius = cell_radius * un(1 - 0.5 * self.poly, 1 + 0.5 * self.poly)
            cell.cell_position = [x, y, z]
            cell.cell_velocity = [vx, vy, vz]
            cell.cell_direction = [nx, ny, nz]


def plot_initial_cells(particles_list):
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection='3d')
    for particle in particles_list:
        ax.scatter(*particle.cell_position, c=particle.group_idx, s=100, alpha=0.6)
    plt.show()


if __name__ == "__main__":
    args = parse_user_input()
    collective = Spheroid(spheroid_radius=args.spheroid_radius, cell_radius=args.cell_radius,
                          cell_count=args.cell_count, poly=0.3)
    particles = collective.cells
    save_initial_cells(particles, args.output_file)
