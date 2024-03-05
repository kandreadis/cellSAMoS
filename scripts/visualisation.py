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
import numpy as np

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
    plot_label = plot_label.replace("/", "div")
    full_path = os.path.join(save_dir, f"{plot_label}.png")
    print_log(f"-- Saving {plot_label}")
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


def plot_msd(session, data, x, y, hue, show=True, dpi=png_res_dpi,
             extra_label="", cmap="tab20b", log_offsets=[1, 2], log_slopes=[1, 2], t_offset=10, error=None):
    """
    MSD visualisation
    """
    plt.figure(figsize=(10, 8))
    title = f"{y} vs. {x} {extra_label}"
    plt.title(textwrap.shorten(title, width=50))
    sns.lineplot(data=data, x=x, y=y, hue=hue, markersize=4, marker="s", legend="brief", palette=cmap,
                 markeredgecolor="none")
    if error is not None:
        # plt.errorbar(x=data[x],y=data[y],ls="none",yerr=data[error])
        for hueval in np.unique(data[hue].values):
            hueval_df = data[data[hue] == hueval]
            plt.errorbar(hueval_df[x], hueval_df[y], color="k", linestyle="None", yerr=hueval_df[error], capsize=2,
                         elinewidth=1, alpha=0.5)
    lag_time = np.logspace(np.log10(min(data[x])), np.log10(max(data[x])))

    for i, log_offset in enumerate(log_offsets):
        plt.plot(lag_time, 10 ** log_offset * (lag_time / t_offset) ** log_slopes[i], linestyle="--",
                 c=str(i / len(log_offsets)), label=f"slope {log_slopes[i]}")
    plt.legend(title=hue)
    plt.loglog()
    plt.grid(which="both", axis="both")
    sns.move_legend(plt.gca(), "upper left", bbox_to_anchor=(1, 1))
    # plt.gca().set_aspect("equal")
    # plt.gca().set_ylim(bottom=1e-2)
    plot_handler(session, dpi, f"line_{hue}_for_{y}_vs_{x}{extra_label}", show)


def plot_lineplot(session, data, x, y, hue, style, show=True, dpi=png_res_dpi, loglog=False, logx=False, logy=False,
                  extra_label="", equal_aspect=False, cmap="rainbow"):
    """
    Line plot visualisation
    """
    plt.figure(figsize=(7, 5))
    title = f"{y} vs. {x} {extra_label}"
    plt.title(textwrap.shorten(title, width=50))
    if type(y) == list:
        for y_ in y:
            sns.lineplot(data, x=x, y=y_, hue=hue, style=style, legend="full", palette=cmap)
    else:
        if x != "time":
            sns.lineplot(data, x=x, y=y, hue=hue, style=style, legend="full", palette=cmap)
        else:
            sns.lineplot(data, x=x, y=y, hue=hue, style=style, marker="o", legend="full", palette=cmap)

    if logx:
        plt.xscale("log")
        plt.grid(which="both", axis="x")
    if logy:
        plt.yscale("log")
        plt.grid(which="both", axis="y")
    if loglog:
        plt.loglog()
        plt.grid(which="both", axis="both")
    if equal_aspect:
        plt.gca().set_aspect("equal")
    sns.move_legend(plt.gca(), "upper left", bbox_to_anchor=(1, 1))
    plot_handler(session, dpi, f"line_{hue}_{style}_for_{y}_vs_{x}{extra_label}", show)


def plot_profile(varlabels, session, data, x, y, hue, show=True, dpi=png_res_dpi, loglog=False, extra_label=""):
    """
    Profile plot visualisation
    """
    plt.figure(figsize=(6, 5))
    title = f"{y} vs. {x} [c={hue}] \n {extra_label} \n {session[:len(session) // 2]}..."
    plt.title(title)
    for hueval in np.unique(data[hue].values):
        data_time = data.groupby(hue).get_group(hueval)
        color_float = hueval / max(data[hue].values)
        plt.plot(data_time[x].values[0], data_time[y].values[0], label=hueval, c=cm.rainbow(color_float), marker="o",
                 markersize=2, alpha=0.8)
    # plt.legend(title=hue)
    plt.axhline(1 / np.e, linestyle="--", label="1/e", c="k")
    plt.xlabel(x)
    plt.ylabel(y)
    if loglog:
        plt.loglog()
    plot_handler(session, dpi, f"line_{hue}_for_{y}_vs_{x}{extra_label}", show)


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
