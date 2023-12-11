"""
Executes SAMoS with initial (particle) configuration parameter ranges/values.
Author: Konstantinos Andreadis
"""
import os, re, datetime, argparse
from datetime import datetime as date
import initialise_cells as init_cells
import numpy as np

# Specify the path to the samos executable
samos_dir="/home/andreadis/Documents/samos_build/build/samos"

# Uses root directory to find the Python and configuration script inside "CellSim"
root_dir=os.getcwd()
configuration_file = os.path.join(root_dir, "CellSim", "spheroid.conf")
intialisation_file = os.path.join(root_dir, "CellSim", "initialise_cells.py")
progress_msg_file = os.path.join(root_dir,"Dropbox","progress.txt")

def print_save_message(message):
    with open(progress_msg_file, "a") as progress_file:
        progress_file.write("["+datetime.datetime.now().strftime('%Y/%m/%d %H:%M')+"] "+message+"\n")
    print(message)

print_save_message("=== Start ===")

def run_simulation(parameters,session, naming_conv, run_samos=True):
    parameters["cell_count"] = int(parameters["cell_count"])
    # The result path is initialised with a datestamp inside "results"
    result_dir=os.path.join(root_dir,"results",date.today().strftime("%Y%m%d"),session, naming_conv)
    try:
        os.makedirs(result_dir)
    except:
        print_save_message("Result directory already exists, overwriting...")

    # Creates path for copied configuration file
    new_configuration_dir = os.path.join(result_dir,"configuration.conf")
    # Creates path for copied initialisation script
    new_initialisation_dir = os.path.join(result_dir,"initialisation.py")
    # Creates path for copied initial particle group(s)
    new_particles_dir = os.path.join(result_dir,"particles.txt")
    try:
        # Copies configuration file to results folder.
        os.system(f"cp {configuration_file} {new_configuration_dir}")
        # Copies initialisation Python script to results folder.
        os.system(f"cp {intialisation_file} {new_initialisation_dir}")
    except:
        print_save_message("Could not copy file to result directory...")

    with open(new_configuration_dir, "r+") as conf_file:
        configuration = conf_file.read()
        configuration = re.sub("@DIVRATE", str(parameters["cell_division_rate"]), configuration)
        configuration = re.sub("@ALPHA", str(parameters["propulsion_alpha"]), configuration)
        configuration = re.sub("@NUMTIMESTEPS", str(parameters["num_time_steps"]), configuration)
        configuration = re.sub("@REFACT", str(parameters["re_fact"]), configuration)
        conf_file.seek(0)
        conf_file.write(configuration)
        conf_file.truncate()
    

    # Executes Python script to initialise particles and save to the result folder
    collective = init_cells.Spheroid(spheroid_radius=parameters["spheroid_radius"], cell_radius=parameters["cell_radius"],
                          cell_count=parameters["cell_count"], poly=parameters["cell_radius_poly"])
    init_cells.save_initial_cells(collective.cells, new_particles_dir)
    
    # Finally, moves to the result folder and executes SAMoS using the configuration file.
    try:
        os.chdir(result_dir)
    except:
        print_save_message("Could not move to result directory...")

    if run_samos:
        try:
            print_save_message("Executing SAMoS...")
            os.system(f"{samos_dir} {new_configuration_dir}")
        except:
            print_save_message("Could not locate SAMoS executable...")
    print_save_message(f"Finished! Location of results: {result_dir}")

# Start of multi-parameter SAMoS execution

parameters = {
    "num_time_steps":20000,
    "cell_count":500,
    "spheroid_radius":8.735,
    "cell_radius":1.0,
    "cell_radius_poly":0.3,

    "cell_division_rate":0.1,
    "propulsion_alpha":0.1,
    "re_fact":1.15,
    "plot_config":False
}

parser = argparse.ArgumentParser()
parser.add_argument("-dim", "--dimension", type=str, default="2D", help="dimensionality of parameter sweep")
args = parser.parse_args()

sweep_type = args.dimension

parameter_1D_sweep = {
    "var_1":"re_fact",
    "var_1_short":"re",
    "var_1_type":"linear", #"log"
    "var_1_start":1,
    "var_1_end":1.2,
    "var_1_num":10,
}
parameter_2D_sweep_old = {
    "var_1":"cell_division_rate",
    "var_1_short":"div",
    "var_1_type":"linear", #"linear"
    "var_1_start":0.01,
    "var_1_end":1,
    "var_1_num":2,

    "var_2":"propulsion_alpha",
    "var_2_short":"alpha",
    "var_2_type":"linear", #"log"
    "var_2_start":0.1,
    "var_2_end":0.3,
    "var_2_num":10
}

parameter_2D_sweep = {
    "var_1":"re_fact",
    "var_1_short":"div",
    "var_1_type":"linear", #"linear"
    "var_1_start":0.01,
    "var_1_end":1,
    "var_1_num":2,

    "var_2":"propulsion_alpha",
    "var_2_short":"alpha",
    "var_2_type":"linear", #"log"
    "var_2_start":0.1,
    "var_2_end":0.3,
    "var_2_num":2
}

if sweep_type == "1D":
    session_label = "{}_{}_{}-{}_#{}".format(parameter_1D_sweep["var_1_short"],parameter_1D_sweep["var_1_type"],parameter_1D_sweep["var_1_start"],parameter_1D_sweep["var_1_end"],parameter_1D_sweep["var_1_num"])
    if parameter_1D_sweep["var_1_type"] == "log": 
        var_1_range = np.logspace(np.log10(parameter_1D_sweep["var_1_start"]),np.log(parameter_1D_sweep["var_1_end"]),parameter_1D_sweep["var_1_num"])
    if parameter_1D_sweep["var_1_type"] == "linear": 
        var_1_range = np.linspace(parameter_1D_sweep["var_1_start"], parameter_1D_sweep["var_1_end"], parameter_1D_sweep["var_1_num"])
    var_1_range = np.round(var_1_range,5)
    print(f"!! Starting 1D parameter sweep for a total of {len(var_1_range)} parameter values...")
    iter = 0
    for div_idx, var1 in enumerate(var_1_range):
        iter += 1
        progress = f"{round(100*iter/(len(var_1_range)))} %"
        status = "{} {}".format(parameter_1D_sweep["var_1"],var1)
        progress_msg = f"[{progress}] --- {status} ---"
        print_save_message(progress_msg)
        parameters[parameter_1D_sweep["var_1"]] = var1
        param_pair_label = "t-{}_N-{}_{}-{}".format(parameters["num_time_steps"], parameters["cell_count"],parameter_1D_sweep["var_1_short"],var1)
        run_simulation(parameters=parameters,naming_conv=param_pair_label,session=session_label,run_samos=True)

if sweep_type == "2D":
    session_label = "{}_{}_{}-{}_#{}_vs_{}_{}_{}-{}_#{}".format(parameter_2D_sweep["var_1_short"],parameter_2D_sweep["var_1_type"],parameter_2D_sweep["var_1_start"],
                                                                parameter_2D_sweep["var_1_end"],parameter_2D_sweep["var_1_num"], parameter_2D_sweep["var_2_short"],
                                                                parameter_2D_sweep["var_2_type"],parameter_2D_sweep["var_2_start"],
                                                                parameter_2D_sweep["var_2_end"],parameter_2D_sweep["var_2_num"])

    if parameter_2D_sweep["var_1_type"] == "log": 
        var_1_range = np.logspace(np.log10(parameter_2D_sweep["var_1_start"]),np.log(parameter_2D_sweep["var_1_end"]),parameter_2D_sweep["var_1_num"])
    if parameter_2D_sweep["var_1_type"] == "linear": 
        var_1_range = np.linspace(parameter_2D_sweep["var_1_start"], parameter_2D_sweep["var_1_end"], parameter_2D_sweep["var_1_num"])
    if parameter_2D_sweep["var_2_type"] == "log": 
        var_2_range = np.logspace(np.log10(parameter_2D_sweep["var_2_start"]),np.log(parameter_2D_sweep["var_2_end"]),parameter_2D_sweep["var_2_num"])
    if parameter_2D_sweep["var_2_type"] == "linear": 
        var_2_range = np.linspace(parameter_2D_sweep["var_2_start"], parameter_2D_sweep["var_2_end"], parameter_2D_sweep["var_2_num"])
    var_1_range = np.round(var_1_range,5)
    var_2_range = np.round(var_2_range,5)
    print(f"!! Starting 2D parameter sweep for a total of {len(var_1_range)*len(var_2_range)} parameter pairs...")
    iter = 0
    for div_idx, var1 in enumerate(var_1_range):
        for alpha_idx, var2 in enumerate(var_2_range):
            iter += 1
            progress = f"{round(100*iter/(len(var_1_range)*len(var_2_range)))} %"
            status = "{} {} {} {}".format(parameter_2D_sweep["var_1"],var1, parameter_2D_sweep["var_2"],var2)
            progress_msg = f"[{progress}] --- {status} ---"
            print_save_message(progress_msg)
            parameters[parameter_2D_sweep["var_1"]] = var1
            parameters[parameter_2D_sweep["var_2"]] = var2
            param_pair_label = "t-{}_N-{}_{}-{}_{}-{}".format(parameters["num_time_steps"], parameters["cell_count"],parameter_2D_sweep["var_1_short"],var1,parameter_2D_sweep["var_2_short"], var2)
            run_simulation(parameters=parameters,naming_conv=param_pair_label,session=session_label,run_samos=True)
print_save_message("=== End ===")