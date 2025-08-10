# TFG

'''
houses things that have to do with doing variable sweeps
'''

'''NOTES ABOUT VARIABLE SWEEPS:
Essentially, what I need to do is take the chosen variables and values, and replace the corresponding input with that. So, if I want to sweep T_ext, what I need to do is
take my list of values for T_ext and insert that into the iteration function somehow.'''

import utils as ut
import core.metadata_mgmt as md

import copy
import numpy as np

# Sweep modes:
sweep_modes = [
    "Single variable sweep",
    "Multi-variable sweep"
]

#sweep dictionary FIX FIX FIX FIX THIS ADD THINGS AND ALL THAT
sweep_variables = {
    "T_ext": {
        "label": "Exterior temperature [ºC]",
        "component": "hrv",
        "sweep_type": "main"
    },
    "T_int": {
        "label": "Interior temperature [ºC]",
        "component": "hrv",
        "sweep_type": "main"
    },
    "RH_ext": {
        "label": "Exterior relative humidity [0-1]",
        "component": "hrv",
        "sweep_type": "main"
    },
    "RH_int": {
        "label": "Interior relative humidity [0-1]",
        "component": "hrv",
        "sweep_type": "main"
    },
    "v_dot": {
        "label": "Volumetric airflow rate [m3/s]",
        "component": "hrv",
        "sweep_type": "both"
    },
    "N_p": {
        "label": "Number of plates",
        "component": "fixed_plate",
        "sweep_type": "sec"
    },
    "L_p": {
        "label": "Effective plate length [m]",
        "component": "fixed_plate",
        "sweep_type": "sec"
    },
    "plate_width": {
        "label": "Plate width [m]",
        "component": "fixed_plate",
        "sweep_type": "sec"
    },
    "plate_thickness": {
        "label": "Plate thickness [m]",
        "component": "fixed_plate",
        "sweep_type": "sec"
    },
    "chevron_angle": {
        "label": "Chevron angle [º]",
        "component": "fixed_plate",
        "sweep_type": "sec"
    },
    "corr_ampl": {
        "label": "Corrugation amplitude [m]",
        "component": "fixed_plate",
        "sweep_type": "sec"
    }
}
'''VARIABLES TO ADD TO sweep_variables:
"T_hot_in_K": {
        "label": "Hot inlet temperature [K]",
        "component": "global",
        "sweep_type": "main"
    },
    "T_cold_in_K": {
        "label": "Cold inlet temperature [K]",
        "component": "global",
        "sweep_type": "main"
    },
"m_dot_hot": {
        "label": "Hot stream mass flow rate [kg/s]",
        "component": "global",
        "sweep_type": "main"
    },
    "m_dot_cold": {
        "label": "Cold stream mass flow rate [kg/s]",
        "component": "global",
        "sweep_type": "main"
    },
'''


# Variable sweep prompts:
def conduct_sweep():
    sweep_ok = ut.input_validation("\nConduct variable sweep? [y/n]: ", "y/n")
    return sweep_ok

def select_sweep_mode():
    """
    docstring
    """
    print("\n\nSelect variable sweep mode:")
    for i, mode in enumerate(sweep_modes):
        print(f"{i+1} : {mode}")
    sweep_mode = ut.input_validation("Enter mode number: ", "int", num_range=(1, len(sweep_modes)))
    md.metadata_set("sweep_mode", sweep_mode)
    return sweep_mode

# Function to filter by sweep type:
def sweep_type_filter(sweep_type):
    """
    docstring
    """
    return {key: var for key, var in sweep_variables.items() if var["sweep_type"] == sweep_type or var["sweep_type"] == "both"}

# Function to highjack inputs:
def highjack(target_dict, var, vals):
    """
    docstring
    """
    target_dict_list = []
    for val in vals:
        new_dict = target_dict.copy()
        new_dict[var] = val
        target_dict_list.append(new_dict)
    return target_dict_list

# Function to set up variable sweeps:
def var_setup(input_dict, module, mode, heat_ex_type):
    """
    docstring
    """
    filtered_dict = {}

    for key in input_dict:
        if input_dict[key]["component"] in (module, mode, heat_ex_type):
            filtered_dict[key] = input_dict[key]
    var_list = list(filtered_dict.keys())

    print(f"\nSelect variable to sweep:")
    for i, var in enumerate(var_list):
        print(f"{i+1} : {var} -> {filtered_dict[var]["label"]}")
    
    idx = ut.input_validation("Enter variable number: ", "int", num_range=(1, len(filtered_dict))) - 1
    var = var_list[idx]
    start = ut.input_validation("Sweep start value: ", "float")
    stop = ut.input_validation("Sweep stop value: ", "float", num_range=(start, np.inf))
    step = ut.input_validation("Step: ", "float", num_range=(0.001, stop))

    num_points = int(round((stop - start) / step)) + 1
    vals = np.linspace(start, stop, num_points)

    return var, vals

# Function to wrap variable sweeps:
def sweep_setup(sweep_mode, module, mode, heat_ex_type):
    """
    docstring
    """
    print("\nVariable sweep setup:")

    # main variable
    main_var_dict = sweep_type_filter("main")
    var1, vals1 = var_setup(main_var_dict, module, mode, heat_ex_type)

    if sweep_mode == 1:
        sweep_params = {
            "var1": var1,
            "vals1": vals1,
            "var2": None,
            "vals2": None
        }
        return sweep_params
    else:
        # secondary variable
        sweep_variables_copy = copy.deepcopy(sweep_variables)
        sweep_variables_copy.pop(var1)
        sec_var_dict = sweep_variables_copy
        var2, vals2 = var_setup(sec_var_dict, module, mode, heat_ex_type)

        sweep_params = {
            "var1": var1,
            "vals1": vals1,
            "var2": var2,
            "vals2": vals2
        }
        return sweep_params


# Function that handles all sweep logic:
def dispatch(module, mode, heat_ex_type, highjack_targets):
    """
    docstring
    """
    # sweep setup
    sweep_mode = select_sweep_mode()
    sweep_params = sweep_setup(sweep_mode, module, mode, heat_ex_type)

    # parameter extraction
    var1 = sweep_params["var1"]
    var2 = sweep_params["var2"]
    vals1 = sweep_params["vals1"]
    vals2 = sweep_params["vals2"]

    # metadata update (redundant?)
    md.metadata_set("sweep_var1", var1)
    md.metadata_set("sweep_vals1", vals1)
    md.metadata_set("sweep_var2", var2)
    md.metadata_set("sweep_vals2", vals2)

    # target dictionary identification
    component1 = sweep_variables[var1]["component"]
    target_dict_var1 = highjack_targets[component1]    

    if var2 is not None:
        # target dictionary identification
        component2 = sweep_variables[var2]["component"]
        target_dict_var2 = highjack_targets[component2]

        if component1 == component2:
            list_of_lists = []
            target_dict_list2 = highjack(target_dict_var2, var2, vals2)
            for target_dict in target_dict_list2:
                target_dict_list1 = highjack(target_dict, var1, vals1)
                list_of_lists.extend(target_dict_list1)
            target_dict_list = list_of_lists
        else:
            target_dict_list2 = highjack(target_dict_var2, var2, vals2)
            target_dict_list1 = highjack(target_dict_var1, var1, vals1)
            target_dict_list = None

    else:
        target_dict_list1 = highjack(target_dict_var1, var1, vals1)
        target_dict_list2 = None
        target_dict_list = None
        component2 = None
    
    highjacked = {
        "target_dict_list1": {
            "list": target_dict_list1,
            "component": component1
        },
        "target_dict_list2": {
            "list": target_dict_list2,
            "component": component2
        },
        "target_dict_list": {
            "list": target_dict_list,
            "component": component1 #abitrary, as target_dict_list is not None when component1 == component2
        }
    }

    return highjacked
