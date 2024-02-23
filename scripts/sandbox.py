"""
A Python file to try out some new functions.
Author: Konstantinos Andreadis
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scripts import data_handler
input = ["/data1/andreadis/analysis_results/analysis/20240214_L-100.0_phi-1.0_re-1.15_freq-10/v0_log_0.01-0.2_#20_vs_Dr_log_0.01-1.0_#3",
"/data1/andreadis/analysis_results/analysis/20240214_L-100.0_phi-1.0_re-1.15_freq-10_Dr-0.01_lowv/v0_log_0.001-0.01_#19_vs_Dr_log_0.01-0.01_#1",
"/data1/andreadis/analysis_results/analysis/20240214_L-100.0_phi-1.0_re-1.15_freq-1000_Dr-0.01/v0_log_0.01-0.2_#20_vs_Dr_log_0.01-0.01_#1",
"/data1/andreadis/analysis_results/analysis/20240214_L-100.0_phi-1.0_re-1.15_freq-1000_Dr-0.01_lowv/v0_log_0.001-0.01_#19_vs_Dr_log_0.01-0.01_#1"]

output = "/data1/andreadis/analysis_results/analysis/20240219_merged/Dr-0.01"

data_handler.combine_datasets(input,output)

# # from samos_init import initialise_cells
# # collective = initialise_cells.Plane(L=100, phi=1.0, cell_radius=1.0, poly=0.3).cells
# # initialise_cells.save_initial_cells(collective, "test.txt")
#
# from analysis import calc_msd
#
# total_time = 100
# freq = 100
# dt = 0.01
# time_steps = np.arange(total_time/(freq * dt))
#
# tnxyztest = np.ones((len(time_steps), 10, 3))
# # tnxyztest += np.random.uniform(0,1,size=(3)) * time_steps[:, np.newaxis, np.newaxis]
# t = time_steps * dt*freq
# delta_t, tmsd = calc_msd(tnxyz=tnxyztest, L=100.0, t=t, tau=1 / 0.1, freqdt=freq * dt, substract_CM=False)
# tmsd_standard = np.mean(np.square(np.linalg.norm(tnxyztest - tnxyztest[0], axis=2)), axis=1)
# print(delta_t)
# plt.figure()
# plt.plot(delta_t, tmsd, label="averaged")
# # plt.plot(np.log10(t), np.log10(tmsd_standard), label="simplified")
# plt.loglog()
# plt.legend()
# plt.grid(which="both")
# plt.show()
# # log = np.logspace(np.log10(0.01), np.log10(1), 10)
# # plt.plot(log, "o-")
# # plt.yscale("log")
# # plt.show()
# # test = pd.read_csv("test.txt", header=0, sep='\s+')
# # plt.figure()
# # plt.title("Initial particle configuration")
# # plt.scatter(test["x"].values, test["y"].values, c=test["z"].values, cmap="Dark2")
# # plt.colorbar()
# # plt.grid()
# # plt.axhline(0, linestyle="--", c="k")
# # plt.axvline(0, linestyle="--", c="k")
# # plt.xticks(np.linspace(min(test["x"]), max(test["x"]), 6))
# # plt.yticks(np.linspace(min(test["y"]), max(test["y"]), 6))
# # plt.gca().set_aspect("equal")
# # plt.show()
