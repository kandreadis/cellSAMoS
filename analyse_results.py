"""
Visualisation and Analysis of SAMoS simulation results.
Author: Konstantinos Andreadis
"""
from scripts.communication_handler import print_log
from scripts.batch_analysis import analyse_root_subfolders

print_log("=== Start ===")
vars_select = {  # folder short version of variable, label for plotting, type (float/int)
    0: ["N", "initial cell count", int],
    1: ["t", "# time steps", int],
    2: ["div", "cell division rate", float],
    3: ["alpha", "propulsion alpha", float],
    4: ["re", "potential re factor", float],
}

result_root = "/data1/andreadis/samos_output/20231213"
analyse_root_subfolders(result_root, vars_select)

print_log("=== End ===")
