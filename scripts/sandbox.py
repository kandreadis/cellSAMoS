"""
A Python file to try out some new functions.
Author: Konstantinos Andreadis
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_handler import combine_datasets

input = "/data1/andreadis/analysis_results/processed_data/20240223_L-100.0_phi-1.0_v0-Dr_andreadis"

output = "/data1/andreadis/analysis_results/processed_data/andreadis_merged/merged"

combine_datasets(input, output)

# # # General phase diagram
# plot_phase_diagram(session=session_label, data=result_df, rows="Dr",
#                    columns="v0", values="average velocity", show=show, dpi=dpi)
# # Velocity fluctuations in steady state
# plot_lineplot(session=session_label, data=result_df, x="time", y="average velocity",
#               hue="v0", style="Dr", show=show, dpi=dpi)
# # Average velocity vs. v0 | Dr
# plot_lineplot(session=session_label, data=result_df, x="v0", y="average velocity",
#               hue="Dr", style=None, show=show, dpi=dpi)
# plot_lineplot(session=session_label, data=result_df, x="v0", y="average velocity",
#               hue="Dr", style=None, show=show, dpi=dpi, loglog=True,
#               extra_label="_loglog")
# # Average velocity vs. Dr | v0
# plot_lineplot(session=session_label, data=result_df, x="Dr", y="average velocity",
#               hue="v0", style=None, show=show, dpi=dpi, logx=True, extra_label="_logx")
# plot_lineplot(session=session_label, data=result_df, x="Dr", y="average velocity",
#               hue="v0", style=None, show=show, dpi=dpi, loglog=True, extra_label="_loglog")


# time_range = np.unique(result_df["lag time"])
# sample_range = 10.0**np.arange(-1, 7)
# for t in time_range:
#     if t in sample_range:
#         print(t)

# result_df = result_df[result_df["lag time"].isin(sample_range)]
