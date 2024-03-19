"""
Executes SAMoS with initial (particle) configuration parameter ranges/values.
Author: Konstantinos Andreadis
"""
import argparse
from datetime import datetime as date
from scripts.communication_handler import print_log
from scripts.samos_handler import run_sweep

if __name__ == "__main__":
    print_log("=== Start ===")
    # Interpret arguments given by the user when this script is run
    parser = argparse.ArgumentParser()

    # Enable SAMoS execution. This is useful to first look at the result folder structure during debugging
    parser.add_argument("session", type=str, help="Session folder name?")
    # Debugging overwrites the previous folder
    parser.add_argument("-debug", action="store_true", help="Debug: Overwrite previous output?")

    # Enable tracker cells embedded within spheroid.
    parser.add_argument("-track", action="store_true", help="Add tracker cells to Spheroid?")
    parser.add_argument("-Ntrack", type=int, default=100, help="Number of tracker cells?")

    # Conf file global parameter to replace @VAR variables
    parser.add_argument("-Nframes", type=int, default=250000, help="Number of time steps")
    parser.add_argument("-Ncell", type=int, default=200, help="Number of initial cells")

    parser.add_argument("-freqDAT", type=int, default=1000, help="Frequency of .dat savings?")
    parser.add_argument("-freqVTP", type=int, default=1000, help="Frequency of .vtp savings?")
    parser.add_argument("-dt", type=float, default=0.01, help="Time step?")

    parser.add_argument("-v0", type=float, default=0.2, help="External propulsion factor")
    parser.add_argument("-Dr", type=float, default=0.1, help="Rotational Diffusion?")

    parser.add_argument("-rcell", type=float, default=1.0, help="Mean cell radius")
    parser.add_argument("-polycell", type=float, default=0.3, help="Polydispersity of cell radius")
    parser.add_argument("-recm", type=float, default=1.0, help="Mean ECM radius")
    parser.add_argument("-polyecm", type=float, default=0.3, help="Polydispersity of ECM radius")
    parser.add_argument("-phiecm", type=float, default=0.4, help="...")

    parser.add_argument("-kcc", type=float, default=1.0, help="..")
    parser.add_argument("-kce", type=float, default=0.6, help="..")
    parser.add_argument("-kee", type=float, default=0.2, help="..")

    parser.add_argument("-divcell", type=float, default=0.01, help="Division rate of a cell")
    parser.add_argument("-deathcell", type=float, default=0.0, help="Death rate of a cell")
    parser.add_argument("-divasymprob", type=float, default=0.5, help="Division asymmetry?")
    parser.add_argument("-L", type=float, default=40.0, help="Plane size L?")
    parser.add_argument("-re", type=float, default=1.15, help="Soft sphere attraction strength?")
    parser.add_argument("-ri", type=float, default=1.5, help="Pair activity potential factor?")

    # Enable SAMoS execution. This is useful to first look at the result folder structure during debugging
    parser.add_argument("-disable_samos", action="store_true", help="Disable SAMoS executable?")
    parser.add_argument("-digit_precision", type=int, default=5, help="Digits of precision for value ranges?")

    # First/only parameter to vary. v1 = None -> only global variables are used for a single run.
    parser.add_argument("-v1", type=str, default=None, help="Name of variable parameter 1?")
    parser.add_argument("-v1type", type=str, default="linear", help="Range type of variable parameter 1?")
    parser.add_argument("-v1start", type=float, default=0.01, help="Range start of variable parameter 1?")
    parser.add_argument("-v1end", type=float, default=0.1, help="Range end of variable parameter 1?")
    parser.add_argument("-v1num", type=int, default=5, help="Range number of points of variable parameter 1?")
    parser.add_argument("-v1custom", nargs="+", default=[], type=float, help="Custom values for variable parameter 1?")

    # Second parameter to vary. v2 = None -> only previous parameter is varied.
    parser.add_argument("-v2", type=str, default=None, help="Name of variable parameter 2?")
    parser.add_argument("-v2type", type=str, default="linear", help="Range type of variable parameter 2?")
    parser.add_argument("-v2start", type=float, default=0.01, help="Range start of variable parameter 2?")
    parser.add_argument("-v2end", type=float, default=0.1, help="Range end of variable parameter 2?")
    parser.add_argument("-v2num", type=int, default=5, help="Range number of points of variable parameter 2?")
    parser.add_argument("-v2custom", nargs="+", default=[], type=float, help="Custom values for variable parameter 2?")

    # Third parameter to vary. v3 = None -> only previous parameter(s) is varied.
    parser.add_argument("-v3", type=str, default=None, help="Name of variable parameter 3?")
    parser.add_argument("-v3type", type=str, default="linear", help="Range type of variable parameter 3?")
    parser.add_argument("-v3start", type=float, default=0.01, help="Range start of variable parameter 3?")
    parser.add_argument("-v3end", type=float, default=0.1, help="Range end of variable parameter 3?")
    parser.add_argument("-v3num", type=int, default=5, help="Range number of points of variable parameter 3?")
    parser.add_argument("-v3custom", nargs="+", default=[], type=float, help="Custom values for variable parameter 3?")

    # Enable tracker cells embedded within spheroid.
    parser.add_argument("-tumoroid_ecm", action="store_true", help="Create tumoroid and ECM?")
    parser.add_argument("-plane", action="store_true", help="Confine cells to 2D plane?")
    parser.add_argument("-plane_abp", action="store_true", help="Use Standard ABP model?")

    parser.add_argument("-phi", type=float, default=1.0, help="Packing fraction phi?")

    parser.add_argument("-Ncores", type=int, default=8, help="Number of cores to run on in parallel?")

    args = parser.parse_args()

    if args.v1custom != []:
        args.v1type = "custom"
    if args.v2custom != []:
        args.v2type = "custom"
    if args.v3custom != []:
        args.v3type = "custom"
    args.tumoroid_ecm = True
    if args.track:
        args.session += "_tracked"

    # User input processing logic
    global_parameters = {}
    parameter_1D_sweep = {}
    parameter_2D_sweep = {}
    parameter_3D_sweep = {}
    sweep_type = None

    if args.v1 is None and args.v2 is None and args.v3 is None:
        sweep_type = 0
    elif args.v1 is not None and args.v2 is None and args.v3 is None:
        sweep_type = 1
    elif args.v1 is not None and args.v2 is not None and args.v3 is None:
        sweep_type = 2
    elif args.v1 is not None and args.v2 is not None and args.v3 is not None:
        sweep_type = 3
    for var in args.__dict__.keys():
        if var[:2] not in ["v1", "v2", "v3"]:
            global_parameters[var] = args.__dict__[var]
        elif sweep_type == 1:
            parameter_1D_sweep[var] = args.__dict__[var]
        elif sweep_type == 2:
            parameter_2D_sweep[var] = args.__dict__[var]
        elif sweep_type == 3:
            parameter_3D_sweep[var] = args.__dict__[var]
    enable_samos_exec = not global_parameters["disable_samos"]
    group_folder = global_parameters["session"]
    debug = global_parameters["debug"]

    # Execution of main samos handling script(s).
    run_sweep(sweep_type=sweep_type, global_parameters=global_parameters, parameter_1D_sweep=parameter_1D_sweep,
              parameter_2D_sweep=parameter_2D_sweep, parameter_3D_sweep=parameter_3D_sweep,
              enable_samos_exec=enable_samos_exec, group_folder=group_folder,
              debug=debug, digit_precision=args.digit_precision, num_cores=args.Ncores)
    print_log("=== End ===")
