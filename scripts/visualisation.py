"""
Collection of independent functions that visualise results.
!! This cannot be run independently, it is a helper script.
Author: Konstantinos Andreadis
"""

import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from paths_init import system_paths
from scripts.communication_handler import print_log
import textwrap

# If no dpi is specified by the user when running the visualisation scripts, this resolution variable overwrites.
png_res_dpi = 300


def create_png_path(session_label, plot_label):
    """
    Figure saving path creation.
    """
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
    """
    Resizes font, changes layout and saves figure. If show is True, it also displays the plot.
    """
    plt.rc('font', size=10)  # legend fontsize
    plt.rc('axes', labelsize=14)  # fontsize of the x and y labels
    plt.rc('figure', titlesize=14)  # fontsize of the figure title
    plt.tight_layout()
    plt.savefig(create_png_path(session, label), dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def plot_boxplot(session, data, x, y, hue, show=True, dpi=png_res_dpi):
    """
    Boxplot visualisation
    """
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.boxplot(data, x=x, y=y, hue=hue)
    plot_handler(session, dpi, f"box_{y}_vs_{x}", show)


def plot_scatterplot(session, data, x, y, hue, style, show=True, dpi=png_res_dpi):
    """
    Scatterplot visualisation
    """
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.scatterplot(data, x=x, y=y, hue=hue, style=style)
    plot_handler(session, dpi, f"scatter_{hue}_for_{y}_vs_{x}", show)


def plot_lineplot(session, data, x, y, hue, style, show=True, dpi=png_res_dpi, loglog=False, logx=False, logy=False):
    """
    Line plot visualisation
    """
    plt.figure()
    title = f"{y} vs. {x} {session}"
    plt.title(textwrap.shorten(title, width=60))
    if type(y) == list:
        for y_ in y:
            if y_ == "msd":
                sns.lineplot(data, x=x, y=y_, hue=None, style=style)
            elif y_ == "msd fit":
                sns.lineplot(data, x=x, y=y_, hue=hue, style=style, linestyle="--")#, palette=['r', 'g'])
            else:
                sns.lineplot(data, x=x, y=y_, hue=hue, style=style)
    else:
        if x != "time":
            sns.lineplot(data, x=x, y=y, hue=hue, style=style, marker="o")
        else:
            sns.lineplot(data, x=x, y=y, hue=hue, style=style)
    if loglog:
        plt.loglog()
        plt.grid(which="both", axis="both")
        plt.gca().set_aspect("equal")
    if logx:
        plt.xscale("log")
        plt.grid(which="both", axis="x")
        # plt.gca().set_aspect("equal")
    if logy:
        plt.yscale("log")
        plt.grid(which="both", axis="y")
        # plt.gca().set_aspect("equal")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plot_handler(session, dpi, f"line_{hue}_{style}_for_{y}_vs_{x}", show)


def plot_profile(session, data, x, y, hue, show=True, dpi=png_res_dpi, loglog=False):
    """
    Profile plot visualisation
    """
    plt.figure()
    title = f"{y} vs. {x} [c={hue} \n {session}]"
    plt.title(textwrap.shorten(title, width=60))
    t_range = data[hue].to_numpy()
    for t_i, t in enumerate(t_range):
        color_float = (t_i + 1) / len(t_range)
        plt.plot(data[x][t_i][0], data[y][t_i][0], label=t, c=cm.rainbow(color_float), marker="o", markersize=2,
                 alpha=0.8)
    plt.xlabel(x)
    plt.ylabel(y)
    # plt.legend()
    if loglog:
        plt.loglog()
    plot_handler(session, dpi, f"line_{hue}_for_{y}_vs_{x}", show)


def plot_heatmap(session, data, rows, columns, values, show=True, cmap="coolwarm", dpi=png_res_dpi):
    """
    Heatmap visualisation
    """
    plt.figure(figsize=(10, 10))
    plt.title(f"{values} for {rows} vs. {columns} \n {session}")
    pivot_result = data.pivot(index=rows, columns=columns, values=values)
    ax = sns.heatmap(pivot_result, linewidth=1, cmap=cmap)  # annot = True
    ax.invert_yaxis()
    plot_handler(session, dpi, f"heat_{values}_for_{rows}_vs_{columns}", show)

def plot_phase_diagram(session, data, rows, columns, values, show=True, cmap="coolwarm", dpi=png_res_dpi):
    """
    Phase diagram visualisation
    """
    title = f"{values} for {rows} vs. {columns} \n {session}"
    print("Averaging plot over time...")
    avg_data = data.groupby([rows, columns])[values].mean().unstack()
    plt.figure(figsize=(5, 5))
    plt.title(title)
    ax = sns.heatmap(avg_data, linewidth=1, cmap=cmap)
    ax.invert_yaxis()


    # sns.scatterplot(data=data, x=columns, y=rows, hue=values, palette=cmap, marker="s",legend=False,s=1000).set(title=title)
    # plt.yscale("log")
    # # import matplotlib as mpl
    # # norm = plt.colors.LogNorm(data[values].min(), data[values].max())
    # norm = plt.Normalize(data[values].min(), data[values].max())
    # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    # sm.set_array([])
    # plt.colorbar(sm, label=values,ax=plt.gca())

    plot_handler(session, dpi, f"phase_{values}_for_{rows}_vs_{columns}", show)