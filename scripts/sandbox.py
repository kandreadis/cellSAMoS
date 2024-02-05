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

log = np.logspace(np.log10(0.01), np.log10(1), 10)
plt.plot(log, "o-")
plt.yscale("log")
plt.show()