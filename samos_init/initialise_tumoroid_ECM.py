"""
Initialisation of cells for SAMoS.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis.
"""
from datetime import *

import matplotlib.pyplot as plt
import numpy as np
import argparse

def save_initial_cells(cells_data, outfile):
    """
    Writes a .txt file containing the initial particle configuration.
    """
    gentime = datetime.now()
    out = open(outfile, 'w')
    out.write('# Total of %s cells\n' % str(len(cells_data)))
    out.write('# Generated on : %s\n' % str(gentime))
    out.write('# id  type radius  x   y   z   vx   vy   vz   nx   ny   nz\n')
    for cell in cells_data:
        x, y, z = cell.position
        vx, vy, vz = cell.velocity
        nx, ny, nz = cell.direction
        out.write(
            '%d  %d  %f %f  %f  %f  %f  %f  %f  %f  %f  %f\n' % (
                cell.idx, cell.type_idx, cell.radius, x, y, z, vx, vy, vz, nx, ny, nz))
    out.close()
    print(f"=> Saved {len(cells_data)} particle(s) to {outfile}!")


class Cell:
    """
    A single cell is created.
    """

    def __init__(self, idx=0, type_idx=1, radius=1.0):
        self.idx = idx
        self.type_idx = type_idx
        self.radius = radius
        self.position = [0.0, 0.0, 0.0]
        self.velocity = [0.0, 0.0, 0.0]
        self.direction = [0.0, 0.0, 0.0]


class Spheroid:
    """
    A spheroid is initialised using a population(collective) of cells.
    """

    def __init__(self, cell_N, cell_radius, cell_poly, ecm_phi, ecm_radius, ecm_poly, ecm_size):
        # Initialise tumoroid cells
        self.cell_N = int(cell_N)
        self.cell_poly = cell_poly
        self.cell_radius = cell_radius
        self.spheroid_radius = (self.cell_N / 0.74) ** (1 / 3) * self.cell_radius

        self.cells = [Cell(idx=i, type_idx=1) for i in range(int(self.cell_N))]
        
        # Initialise ECM
        self.ecm_radius = ecm_radius
        self.ecm_poly = ecm_poly
        self.ecm_phi = ecm_phi
        size_box = ecm_size
        self.ecm_lx = size_box
        self.ecm_ly = size_box
        self.ecm_lz = size_box
        self.ecm_volume = self.ecm_lx * self.ecm_ly * self.ecm_lz

        self.ecm_N = int(self.ecm_phi * self.ecm_volume / ((4/3) * np.pi * self.ecm_radius ** 3))
        self.cells.extend(Cell(idx=j, type_idx=2) for j in range(self.cell_N, self.cell_N + self.ecm_N))

        def un(a, b):
            """
            Uniform distribution draw between a and b.
            """
            return np.random.uniform(a, b)

        invalid_ecm = []
        for index, cell in enumerate(self.cells):
            # Position
            if cell.type_idx == 2:
                x = self.ecm_lx * un(-0.5, 0.5)
                y = self.ecm_ly * un(-0.5, 0.5)
                z = self.ecm_lz * un(-0.5, 0.5)
                if x**2+y**2+z**2 <= self.spheroid_radius**2:
                    invalid_ecm.append(index)
            else:
                phi = un(0, 2 * np.pi)
                costheta = un(-1, 1)
                theta = np.arccos(costheta)
                r = self.spheroid_radius * un(0, 1) ** (1. / 3.)
                x = r * np.sin(theta) * np.cos(phi)
                y = r * np.sin(theta) * np.sin(phi)
                z = r * np.cos(theta)
            # Velocity
            vx, vy, vz = 0, 0, 0
            phi = un(0, 2 * np.pi)
            costheta = un(-1, 1)
            nx = np.cos(phi) * np.sin(np.arccos(costheta))
            ny = np.sin(phi) * np.sin(np.arccos(costheta))
            nz = costheta
            # Radius
            if cell.type_idx == 2:
                cell.radius = self.ecm_radius * un(1 - 0.5 * self.ecm_poly, 1 + 0.5 * self.ecm_poly)
            else:
                cell.radius = self.cell_radius * un(1 - 0.5 * self.cell_poly, 1 + 0.5 * self.cell_poly)
            
            cell.position = [x, y, z]
            cell.velocity = [vx, vy, vz]
            cell.direction = [nx, ny, nz]
        if len(invalid_ecm) != 0:
            invalid_ecm.sort(reverse=True)
            for invalid_ecm_idx in invalid_ecm:
                del self.cells[invalid_ecm_idx]
            for idx, cell in enumerate(self.cells):
                cell.idx = idx
            print(f"- ECM: Deleted {len(invalid_ecm)}, {self.ecm_N-len(invalid_ecm)} left!")
def plot_initial_cells(particles_list):
    """
    Basic 3D visualisation of initial cell configuration for debugging purposes.
    """
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(111, projection='3d')
    for particle in particles_list:
        if particle.type_idx == 2:
            c = "r"
        else:
            c = "b"
        ax.scatter(*particle.position, c=c, s=50, alpha=0.6)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument("-N_cell", type=int, default=200, help="Cell count?")
parser.add_argument("-r_cell", type=float, default=1.0, help="Cell radius?")
parser.add_argument("-poly_cell", type=float, default=0.3, help="Cell radius poly?")

parser.add_argument("-phi_ecm", type=float, default=0.0, help="ECM packing fraction?")
parser.add_argument("-ecm_size", type=float, default=10, help="ECM packing fraction?")
parser.add_argument("-r_ecm", type=float, default=1.0, help="ECM radius?")
parser.add_argument("-poly_ecm", type=float, default=0.3, help="ECM radius poly?")
parser.add_argument("-plot", action="store_true", help="Plot configuration?")


if __name__ == "__main__":
    args = parser.parse_args()

    all_particles = Spheroid(cell_N=args.N_cell, cell_radius=args.r_cell, cell_poly=args.poly_cell, 
                            ecm_phi=args.phi_ecm, ecm_radius=args.r_ecm, ecm_poly=args.poly_ecm, ecm_size=args.ecm_size).cells

    save_initial_cells(cells_data=all_particles,outfile="particles.txt")
    if args.plot:
        plot_initial_cells(all_particles)