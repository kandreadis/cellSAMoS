"""
Contains all system paths to various folders or files defined by each user individually.
Author: Konstantinos Andreadis
"""

system_paths = {
    # Path of samos executable "..../samos"
    "samos_dir": "/home/andreadis/Documents/SAMoS-ABPactreact/build/samos",
    # Path where simulation results should be saved ".../samos_output"
    "output_samos_dir": "/data1/andreadis/samos_output",
    # Path of configuration file(s) ".../*.conf"
    "conf_file": "/data1/andreadis/CellSim/samos_init/spheroid.conf",
    "conf_file_trackers": "/data1/andreadis/CellSim/samos_init/spheroid_trackers.conf",
    "conf_file_plane": "/data1/andreadis/CellSim/samos_init/plane.conf",
    "conf_file_plane_abp": "/data1/andreadis/CellSim/samos_init/plane_ABP.conf",
    "conf_file_tumoroid_ecm": "/data1/andreadis/CellSim/samos_init/tumoroid_ECM.conf",
    # Path of particle initialisation file ".../*.py"
    "init_particles_file": "/data1/andreadis/CellSim/samos_init/initialise_cells.py",
    "init_tumoroid_ecm_file": "/data1/andreadis/CellSim/samos_init/initialise_tumoroid_ECM.py",
    # Path of terminal output logging file ".../*.log"
    "log_file": "/data1/andreadis/Dropbox/CELLSIM_PORT/cellsim.log",
    # Path of port status logging file ".../*.log"
    "port_status_file": "/data1/andreadis/Dropbox/CELLSIM_PORT/port_status.log",
    # Path of folder structure logging file(s) ".../*.log"
    "output_dirstatus_file": "/data1/andreadis/Dropbox/CELLSIM_PORT/samos-output_dir-tree.log",
    "analysis_dirstatus_file": "/data1/andreadis/Dropbox/CELLSIM_PORT/analysis-output_dir-tree.log",
    # Path where analysis results should be saved ".../figures"
    "output_analysis_dir": "/data1/andreadis/analysis_results/processed_data",
    "output_figures_dir": "/data1/andreadis/analysis_results/figures",
    "output_movie_dir": "/data1/andreadis/analysis_results/movies",
    # Path to listen to for new .sh bash commands ".../PORT"
    "listen_dir": "/data1/andreadis/Dropbox/CELLSIM_PORT",
    # Path where all completed tasks should be moved to ".../completed"
    "completed_tasks_dir": "/data1/andreadis/Dropbox/CELLSIM_PORT/completed_tasks"
}
