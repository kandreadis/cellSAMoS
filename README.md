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

## Project Folder Structure

## How to contribute

## Acknowledgements

## Contact Information

## License