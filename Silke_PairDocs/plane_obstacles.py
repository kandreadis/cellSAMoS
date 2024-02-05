# random sphere new python script

import numpy as np
import argparse


class Plane:

    # random plane with random obstacles in frac of particles
    def __init__(self, L, phi, rad, poly):
        self.L = L
        self.rad = rad
        self.poly = poly

        area = L ** 2
        self.N = int(phi * area / (np.pi * rad ** 2))
        print("Creating new plane of length " + str(self.L) + " with " + str(self.N) + " particles!")

        # make a plain sheet of array for the input file
        # id type radius x y z vx vy vz nx ny nz
        self.data = np.zeros((self.N, 12))

    def makeObstacle(self, mode, frac):
        Nobs = int(frac * self.N)
        if mode == 'random':
            for k in range(Nobs):
                # type
                self.data[k, 1] = 2  # type 2 is fixed
        else:
            print("Unimplemented obstacle type, doing nothing!")

    def makePosVel(self):
        for k in range(self.N):
            # id
            self.data[k, 0] = k
            # type
            self.data[k, 1] = 1  # just type one for now ...
            # radius
            self.data[k, 2] = self.rad * np.random.uniform(1 - 0.5 * self.poly, 1 + 0.5 * self.poly)
            # positions
            self.data[k, 3] = self.L * np.random.uniform(-0.5, 0.5)
            self.data[k, 4] = self.L * np.random.uniform(-0.5, 0.5)
            self.data[k, 5] = 0.0

            # velocity: start at zero, eff it
            self.data[k, 6:9] = 0

            # director: random unit vector in xy
            alpha = np.random.uniform(0, 2 * np.pi)
            self.data[k, 9] = np.cos(alpha)
            self.data[k, 10] = np.sin(alpha)
            self.data[k, 11] = 0.0

    def writeInifile(self, filename):
        out = open(filename, 'w')
        out.write('# Total of %s particles\n' % str(self.N))
        out.write('# id  type radius  x   y   z   vx   vy   vz   nx   ny   nz\n')
        for k in range(self.N):
            out.write('%d  %d  %f %f  %f  %f  %f  %f  %f  %f  %f  %f\n' % tuple(self.data[k, :]))
        out.close()


parser = argparse.ArgumentParser()
parser.add_argument("-L", "--length", type=float, default=100, help="box length")
parser.add_argument("-f", "--phi", type=float, default=1.0, help="packing fraction")
parser.add_argument("-p", "--poly", type=float, default=0.0, help="polydispersity fraction")
parser.add_argument("-m", "--mode", type=str, default='random', help="obstacle fraction")
parser.add_argument("-n", "--frac", type=float, default=0.1, help="obstacle fraction fraction")
parser.add_argument("-a", "--rpart", type=float, default=1.0, help="particle radius")
parser.add_argument("-o", "--output", type=str, default='out.dat', help="output file")
args = parser.parse_args()

P = Plane(args.length, args.phi, args.rpart, args.poly)
P.makePosVel()
P.makeObstacle(args.mode, args.frac)
P.writeInifile(args.output)
