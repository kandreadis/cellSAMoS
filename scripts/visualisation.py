"""
Collection of independent functions that visualise results.
Author: Konstantinos Andreadis
"""

import seaborn as sns
import datetime, os
import matplotlib.pyplot as plt


def plot_scatterplot(session, data, x,y,hue,style, show=True, savedpi=300):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.scatterplot(data, x=x, y=y, hue=hue,style=style)
    root_dir=os.getcwd()
    save_dir = os.path.join(root_dir, "results", "sweep_analysis",session)
    try:
        os.makedirs(save_dir)
    except:
        print("Saving directory already exists, overwriting...")
    plt.savefig(os.path.join(save_dir, f"scatter_{hue}.png"), dpi=savedpi)
    if show:
        plt.show()
    else:
        plt.close()
def plot_boxplot(session, data, x,y,hue, show=True, savedpi=300):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.boxplot(data, x=x, y=y, hue=hue)
    root_dir=os.getcwd()
    save_dir = os.path.join(root_dir, "results", "sweep_analysis",session)
    try:
        os.makedirs(save_dir)
    except:
        print("Saving directory already exists, overwriting...")
    plt.savefig(os.path.join(save_dir, f"box_{hue}.png"), dpi=savedpi)
    if show:
        plt.show()
    else:
        plt.close()

def plot_lineplot(session, data, x,y,hue,style, show=True, savedpi=300):
    plt.figure()
    plt.title(f"{y} vs. {x} \n {session}")
    sns.lineplot(data, x=x, y=y, hue=hue,style=style)
    root_dir=os.getcwd()
    save_dir = os.path.join(root_dir, "results", "sweep_analysis",session)
    try:
        os.makedirs(save_dir)
    except:
        print("Saving directory already exists, overwriting...")
    plt.savefig(os.path.join(save_dir, f"line_{hue}.png"), dpi=savedpi)
    if show:
        plt.show()
    else:
        plt.close()

def plot_heatmap(session, data, rows, columns,values,show=True,cmap="coolwarm",savedpi=300):
    
    plt.figure(figsize=(10,10))
    plt.title(f"{values} for {rows} vs. {columns} \n {session}")
    pivot_result = data.pivot(index=rows, columns=columns, values=values)
    ax = sns.heatmap(pivot_result, linewidth = 1, cmap="coolwarm") # annot = True
    ax.invert_yaxis()
    root_dir=os.getcwd()
    save_dir = os.path.join(root_dir, "results", "sweep_analysis", session)
    try:
        os.makedirs(save_dir)
    except:
        print("Saving directory already exists, overwriting...")
    plt.savefig(os.path.join(save_dir, f"heat_{values}.png"), dpi=savedpi)
    if show:
        plt.show()
    else:
        plt.close()