"""
A Python file to try out some new functions.
Author: Konstantinos Andreadis
"""
import numpy as np
import pandas as pd

x = np.random.uniform(0, 1, 10)
y = np.random.uniform(0, 1, 10)
z = np.random.uniform(0, 1, 10)

xyz = np.column_stack([x, y, z])
result_folder_subdirs_num = 400
r = np.sqrt(np.sum(np.square(xyz), axis=1))
xyz_cm = np.average(xyz, axis=0, weights=r)
print(xyz-xyz_cm)
