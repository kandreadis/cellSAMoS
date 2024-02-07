"""
A Python file to try out some new functions.
Author: Konstantinos Andreadis
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from samos_init import initialise_cells
# collective = initialise_cells.Plane(L=100, phi=1.0, cell_radius=1.0, poly=0.3).cells
# initialise_cells.save_initial_cells(collective, "test.txt")

# log = np.logspace(np.log10(0.01), np.log10(1), 10)
# plt.plot(log, "o-")
# plt.yscale("log")
# plt.show()
test = pd.read_csv("test.txt", header=0, sep='\s+')
plt.figure()
plt.title("Initial particle configuration")
plt.scatter(test["x"].values, test["y"].values, c=test["z"].values, cmap="Dark2")
plt.colorbar()
plt.grid()
plt.axhline(0, linestyle="--", c="k")
plt.axvline(0, linestyle="--", c="k")
plt.xticks(np.linspace(min(test["x"]), max(test["x"]), 6))
plt.yticks(np.linspace(min(test["y"]), max(test["y"]), 6))
plt.gca().set_aspect("equal")
plt.show()