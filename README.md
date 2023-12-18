# CellSim

Multi Cell Simulation & Analysis using the SAMoS simulation framework.

SAMoS, or Soft Active Matter on Surfaces is an extensive simulation package by
Rastko Sknepnek et al.

## Before installing cellSAMoS....

Follow the **README** of [SAMoS GitHub](https://github.com/sknepneklab/SAMoS) to properly configure
and build the C++ SAMoS simulation software on your local machine. The **build** folder containing the
**executable "samos"** is necessary for cellSAMoS to function properly.

Please ensure it is working by testing the following command below. _SAMOS_EXEC_PATH_ should be
the path to your samos executable (e.g. "/.../build/samos") and _EXAMPLE_CONF_PATH_ the path to a
test configuration .conf file (e.g. "/.../cellSAMoS/samos_test/example.conf".

```bash
SAMOS_EXEC_PATH PATH_TO_CELLSAMOS_EXAMPLE_CONF
```

## Requirements

Before you continue, ensure you have met the following requirements:

1. You have a functioning SAMoS executable.
2. You have installed the latest version (> 3) of Python .
3. You have sufficient storage space and memory for the simulations.

## Installation

Use a package manager to install the necessary Python packages listed in **requirements.txt**.
Below you can find an example for using pip by simply replacing PACKAGE with the name of the library,
e.g. "numpy".

```bash
pip install PACKAGE
```

## Usage

Small notes:

- _**PATH_TO_CLONE** is the path to your clone of cellSAMoS._
- _Replace **python** with the path to your python interpreter._

There are two ways of executing cellSAMoS:

1. Execute **command_listener.py**, and this will continiously listen to
   any added bash scripts in paths_init.py/system_paths["listen_dir"]. Upon execution, results are synced live.

```bash
python PATH_TO_CLONE/run_samos.py
```

2. Or, execute **run_samos.py** with any parameter (range(s)) you prefer.

```bash
python PATH_TO/run_samos.py
```

2. The same applies to the analysis performed by **analyse_results.py**, where a folder to be processed can be given.

```bash
python PATH_TO/analyse_results.py
```

## Project Folder Structure

Documentation in progress...

## How to contribute

Clone this repository using your Git client. Any issues can be added to the issue tracker in GitHub,
and push requests are granted if a valid added benefit is shown.

## Acknowledgements

Silke Henkes (main supervisor of this thesis), Thomas Schmidt (second supervisor and
PI of experimental group for this collaboration) and the team behind the SAMoS simulation framework.

## Contact Information

Konstantinos Andreadis (andreadis@lorentz.leidenuniv.nl)

## License

MIT License
Copyright (c) 2023-2024 Konstantinos Andreadis