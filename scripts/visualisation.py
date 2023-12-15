"""
Collection of independent functions that visualise results.
Author: Konstantinos Andreadis
"""

import os
import seaborn as sns
import matplotlib.pyplot as plt

from paths_init import system_paths
from scripts.communication_handler import print_log

png_res_dpi = 300

def create_png_path(session_label, plot_label):
    root_dir = system_paths["output_figures_dir"]
    save_dir = os.path.join(root_dir, session_label)
    try:
        os.makedirs(save_dir)
    except:
        pass
    full_path = os.path.join(save_dir, f"{plot_label}.png")
    print_log(f"Saving {full_path}")
    return full_path


def plot_handler(session, dpi, label, show):
    plt.rc('font', size=10)  # legend fontsize
    plt.rc('axes', labelsize=16)  # fontsize of the x and y labels
    plt.rc('figure', titlesize=16)  # fontsize of the figure title
    plt.tight_layout()
    plt.savefig(create_png_path(session, label), dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def plot_boxplot(session, data, x, y, hue, show=True, dpi=png_res_dpi):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.boxplot(data, x=x, y=y, hue=hue)
    plot_handler(session, dpi, f"box_{y}_vs_{x}", show)


def plot_scatterplot(session, data, x, y, hue, style, show=True, dpi=png_res_dpi):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.scatterplot(data, x=x, y=y, hue=hue, style=style)
    plot_handler(session, dpi, f"scatter_{hue}_for_{y}_vs_{x}", show)


def plot_lineplot(session, data, x, y, hue, style, show=True, dpi=png_res_dpi):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.lineplot(data, x=x, y=y, hue=hue, style=style)
    plot_handler(session, dpi, f"line_{hue}_for_{y}_vs_{x}", show)


def plot_heatmap(session, data, rows, columns, values, show=True, cmap="coolwarm", dpi=png_res_dpi):
    plt.figure(figsize=(10, 10))
    plt.title(f"{values} for {rows} vs. {columns} \n {session}")
    pivot_result = data.pivot(index=rows, columns=columns, values=values)
    ax = sns.heatmap(pivot_result, linewidth=1, cmap=cmap)  # annot = True
    ax.invert_yaxis()
    plot_handler(session, dpi, f"heat_{values}_for_{rows}_vs_{columns}", show)
