# TFG

'''
houses all plotting and analysis functionalities
'''

import utils as ut
import variable_sweeps as vs
import core.heatx as hx

import matplotlib.pyplot as plt
import numpy as np

# Result dictionary (y-axis):
y_axis_dict = {
    "q_real": "Exchanged Heat [W]",
    "T_hot_out_K": "Hot flow outlet temperature [K]",
    "T_cold_out_K": "Cold flow outlet temperature [K]"
}

# Function to select y-axis variable:
def plot_select():
    """
    docstring
    """
    print("\nSelect variable to plot:")
    for i, name in enumerate(y_axis_dict.values()):
        print(f"{i+1} : {name}")
    
    idx = ut.input_validation("Enter variable number: ", "int", num_range=(1, len(y_axis_dict))) - 1
    y_var = list(y_axis_dict.keys())[idx]
    return y_var

# Function to plot 1d sweeps:
def plot_1d(calc_results_list, metadata, y_var):
    """
    docstring
    """
    # create list of points for the y-axis:
    y_array = []
    for results in calc_results_list:
        y_val = results[y_var]
        y_array.append(y_val)
    
    # create list of points for the x-axis:
    x_var = metadata["sweep_var1"]
    x_array = metadata["sweep_vals1"]

    # plot:
    plt.figure()
    plt.scatter(x_array, y_array, label=f"{hx.heat_ex_dict[metadata["heat_ex_type"]]["name"]} heat exchanger")
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.xlabel(f"{vs.sweep_variables[x_var]["label"]}")
    plt.ylabel(f"{y_axis_dict[y_var]}")
    plt.title(f"Module: {hx.module_dict[metadata["module"]]["name"]}; Mode: {hx.module_dict[metadata["module"]]["modes"][metadata["mode"]]}; 1D Sweep Results")
    plt.minorticks_on()
    plt.grid(True)
    plt.legend()
    plt.show()

# Function to plot 2d sweeps:
def plot_2d(calc_results_list, metadata, y_var):
    """
    docstring
    """
    # find main and secondary swept variables and their values:
    x_var = metadata["sweep_var1"]
    x_array = metadata["sweep_vals1"]
    series_var = metadata["sweep_var2"]
    series_vals = metadata["sweep_vals2"]

    # create a list of lists of points for the y-axis:
    y_array = []
    for i, thing in enumerate(series_vals):
        y_extract = []
        start_idx = i * len(x_array)
        for y_val_idx in range(len(x_array)):
            dictionary = calc_results_list[y_val_idx + start_idx]
            y_val = dictionary[y_var]
            y_extract.append(y_val)
        y_array.append(y_extract)
    
    # plot:
    plt.figure()
    for i, val in enumerate(series_vals):
        plt.scatter(x_array, y_array[i], label=f" = {float(np.round(val, 3))}")
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.xlabel(f"{vs.sweep_variables[x_var]["label"]}")
    plt.ylabel(f"{y_axis_dict[y_var]}")
    plt.title(f"Module: {hx.module_dict[metadata["module"]]["name"]}; Mode: {hx.module_dict[metadata["module"]]["modes"][metadata["mode"]]}; 2D Sweep Results")
    plt.minorticks_on()
    plt.grid(True)
    plt.legend(title=f"{vs.sweep_variables[series_var]["label"]}")
    plt.show()

# Function to coordinate and dispatch plotting:
def plot_dispatch(calc_results_list, metadata):
    """
    docstring
    """
    y_var = plot_select()

    if metadata.get("sweep_var1") is not None and metadata.get("sweep_var2") is None:
        plot_1d(calc_results_list, metadata, y_var)
    elif metadata.get("sweep_var2") is not None:
        plot_2d(calc_results_list, metadata, y_var)
    else:
        print("\nPlotting error")
