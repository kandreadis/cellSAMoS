"""
3D rendering of SAMoS simulation results.
Author: Konstantinos Andreadis
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import cv2
import textwrap
from multiprocessing import Pool
from paths_init import system_paths
from scripts.communication_handler import print_log


def read_dat(path):
    """
    Read a .dat file and shift its columns to properly import data as DataFrame.
    """
    data = pd.read_csv(path, header=0, sep='\s+')
    colshift = {data.columns[u]: data.columns[u + 1] for u in range(len(data.columns) - 1)}
    data.rename(columns={data.columns[-1]: 'none'}, inplace=True)
    data.rename(columns=colshift, inplace=True, errors="raise")
    return data


def plot_particles(folder_path, movie_dir, args):
    """
    Plot all particles
    """
    L = args.L
    maxframes = args.maxframes
    lastframe = args.lastframe
    firstframe = args.firstframe
    onlycells = args.onlycells
    cut_z = args.cut_z
    folder_path = os.path.normpath(folder_path)
    movie_dir = os.path.normpath(movie_dir)
    folder_name = os.path.basename(folder_path)

    files = [f for f in os.listdir(folder_path) if f.endswith('.dat')]
    files.sort()
    images = []

    if lastframe:
        try:
            files = [files[-1]]
        except:
            print("No files present... Aborting!")
            return
    elif firstframe:
        try:
            files = [files[0]]
        except:
            print("No files present... Aborting!")
            return
    else:
        if maxframes is not None:
            files = files[:maxframes]
    print_log(f"-- Visualising {len(files)} in {folder_name}...")
    for file in files:
        # For each time step
        print(f"--- {file}")
        data = read_dat(os.path.join(folder_path, file))
        # Extract data
        particle_type = data["type"]
        radius = data["radius"]
        xyz_positions = data[["x", "y", "z"]]
        # Plot particles
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111, projection='3d')
        for i in range(len(data)):
            x, y, z = xyz_positions.iloc[i]
            if cut_z:
                if z > 0:
                    continue
            # For each particle
            if onlycells and particle_type[i] != 1:
                continue
            if particle_type[i] == 1:
                color = args.cell_color
                opacity = args.cell_alpha
            elif particle_type[i] == 2:
                color = args.ECM_color
                opacity = args.ECM_alpha
            ax.scatter(x, y, z, s=50 * radius[i], c=color, alpha=opacity)
        frame = int(os.path.splitext(os.path.basename(os.path.join(folder_path, file)))[0].split("_")[-1])
        folder_label = textwrap.fill(folder_name, 55)
        plt.title(folder_label + "\n" + f"FRAME={frame}")
        x, y, z = np.array([[-L / 2, 0, 0], [0, -L / 2, 0], [0, 0, -L / 2]])
        u, v, w = np.array([[L, 0, 0], [0, L, 0], [0, 0, L]])
        ax.quiver(x, y, z, u, v, w, arrow_length_ratio=0.1, color="black", alpha=0.2)
        ax.grid(False)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim(-L / 2, L / 2)
        ax.set_ylim(-L / 2, L / 2)
        ax.set_zlim(-L / 2, L / 2)
        # Save as image
        image_path = os.path.join(folder_path, f"{file}.png")
        fig.tight_layout()
        plt.savefig(image_path, dpi=100)
        images.append(image_path)
        plt.close()

    if lastframe:
        print("-- Saving snapshot...")
        img = cv2.imread(images[-1])
        height, width, _ = img.shape
        if cut_z:
            img_file = os.path.join(movie_dir, f"{folder_name}_cut-z_lastframe.png")
        else:
            img_file = os.path.join(movie_dir, f"{folder_name}_lastframe.png")

        cv2.imwrite(img_file, img)
        print_log(f"-- Saving image {img_file}...")
    elif firstframe:
        print("-- Saving snapshot...")
        img = cv2.imread(images[-1])
        height, width, _ = img.shape
        if cut_z:
            img_file = os.path.join(movie_dir, f"{folder_name}_cut-z_firstframe.png")
        else:
            img_file = os.path.join(movie_dir, f"{folder_name}_firstframe.png")

        cv2.imwrite(img_file, img)
        print_log(f"-- Saving image {img_file}...")
    else:
        print("-- Saving movie...")
        height, width, _ = cv2.imread(images[0]).shape
        movie_file = os.path.join(movie_dir, f"{folder_name}.avi")
        video = cv2.VideoWriter(movie_file, cv2.VideoWriter_fourcc(*'MJPG'), 10, (width, height))

        for image_path in images:
            video.write(cv2.imread(image_path))
        video.release()
        cv2.destroyAllWindows()
        print_log(f"-- Saving movie {movie_file}...")

    print("-- Removing cache images...")
    # Remove individual image files
    for image_path in images:
        os.remove(image_path)


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Visualize particles in 3D')
    parser.add_argument('session_folders', type=str, help='Path to the session folder(s)?', nargs='*')
    parser.add_argument('-Ncores', type=int, default=8, help='Number of cores')
    parser.add_argument('-L', type=float, default=40.0, help='L')
    parser.add_argument('-cell_color', type=str, default="blue", help='cell color')
    parser.add_argument('-cell_alpha', type=float, default=0.5, help='cell transparency')
    parser.add_argument('-ECM_color', type=str, default="k", help='ECM color')
    parser.add_argument('-ECM_alpha', type=float, default=0.1, help='ECM transparency')
    parser.add_argument("-maxframes", type=int, default=None, help="Max # frames to visualise?")

    parser.add_argument("-cut_z", action="store_true", help="Cut z > 0?")

    parser.add_argument("-firstframe", action="store_true", help="Visualise only first frame?")
    parser.add_argument("-lastframe", action="store_true", help="Visualise only last frame?")
    parser.add_argument("-onlycells", action="store_true", help="Visualise only cells?")
    args = parser.parse_args()
    movie_dir = system_paths["output_movie_dir"]

    processes = []
    pool = Pool(processes=args.Ncores)

    for session in args.session_folders:
        print(f"- Session {session}")
        folder_paths = [f for f in os.listdir(os.path.join(system_paths["output_samos_dir"], session)) if
                        os.path.isdir(os.path.join(os.path.join(system_paths["output_samos_dir"], session, f)))]
        folder_paths.sort()

        for folder_path in folder_paths:
            print(f"- Sweep {folder_path}")
            samos_run_path = [f for f in
                              os.listdir(os.path.join(system_paths["output_samos_dir"], session, folder_path)) if
                              os.path.isdir(os.path.join(
                                  os.path.join(system_paths["output_samos_dir"], session, folder_path, f)))]
            movie_path = os.path.join(movie_dir, session, folder_path)
            try:
                os.makedirs(movie_path)
            except:
                pass
            for run in samos_run_path:
                processes.append(pool.apply_async(func=plot_particles, args=(
                    os.path.join(system_paths["output_samos_dir"], session, folder_path, run), movie_path, args)))

    for p in processes:
        p.get()
    pool.close()
    pool.join()


if __name__ == "__main__":
    print_log("=== Start ===")
    main()
    print_log("=== End ===")
