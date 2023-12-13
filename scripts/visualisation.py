"""
Collection of independent functions that visualise results.
Author: Konstantinos Andreadis
"""

import os
import datetime
import seaborn as sns
import matplotlib.pyplot as plt


def save_path(session_label, plot_label):
    root_dir = os.getcwd()
    save_dir = os.path.join(root_dir, "analysis_results", "figures", datetime.datetime.now().strftime('%Y%m%d'),
                            session_label)
    try:
        os.makedirs(save_dir)
    except:
        pass
    full_path = os.path.join(save_dir, f"{plot_label}.png")
    print(f"Saving {full_path}")
    return full_path


def plot_handler(show):
    if show:
        plt.show()
    else:
        plt.close()


def plot_boxplot(session, data, x, y, hue, show=True, savedpi=300):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.boxplot(data, x=x, y=y, hue=hue)
    plt.savefig(save_path(session, f"box_{y}_vs_{x}"), dpi=savedpi)
    plot_handler(show)


def plot_scatterplot(session, data, x, y, hue, style, show=True, savedpi=300):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.scatterplot(data, x=x, y=y, hue=hue, style=style)
    plt.savefig(save_path(session, f"scatter_{hue}_for_{y}_vs_{x}"), dpi=savedpi)
    plot_handler(show)


def plot_lineplot(session, data, x, y, hue, style, show=True, savedpi=300):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.lineplot(data, x=x, y=y, hue=hue, style=style)
    plt.savefig(save_path(session, f"line_{hue}_for_{y}_vs_{x}"), dpi=savedpi)
    plot_handler(show)


def plot_heatmap(session, data, rows, columns, values, show=True, cmap="coolwarm", savedpi=300):
    plt.figure(figsize=(10, 10))
    plt.title(f"{values} for {rows} vs. {columns} \n {session}")
    pivot_result = data.pivot(index=rows, columns=columns, values=values)
    ax = sns.heatmap(pivot_result, linewidth=1, cmap=cmap)  # annot = True
    ax.invert_yaxis()
    plt.savefig(save_path(session, f"heat_{values}_for_{rows}_vs_{columns}"), dpi=savedpi)
    plot_handler(show)
