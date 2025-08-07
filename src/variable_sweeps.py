# TFG

'''
houses things that have to do with doing variable sweeps
'''

'''NOTES ABOUT VARIABLE SWEEPS:
Essentially, what I need to do is take the chosen variables and values, and replace the corresponding input with that. So, if I want to sweep T_ext, what I need to do is
take my list of values for T_ext and insert that into the iteration function somehow.'''

import utils as ut
import core.heatx as hx
import modules.hvac.hrv as hrv
import exchangers.fixed_plate as fp
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
    sweep_ok = ut.input_validation("Conduct variable sweep? [y/n]: ", "y/n")
    return sweep_ok

def select_sweep_mode():
    """
    docstring
    """
    print("Select variable sweep mode:")
    for i, mode in enumerate(sweep_modes):
        print(f"{i+1} : {mode}")
    sweep_mode = ut.input_validation("Enter mode number: ", "int", num_range=(1, len(sweep_modes)))
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
        target_dict[var] = val
        target_dict_list.append(target_dict)
    return target_dict_list

# Function to set up variable sweeps:
def sweep_setup(sweep_mode): ####not refactored, and missing module info: should not allow user to select a variable from a module different to the one running!
    """
    docstring
    """
    print("Variable sweep setup:")

    # main variable
    main_vars = sweep_type_filter("main")
    main_keys = list(main_vars.keys())

    print("Select main variable to sweep:")
    for i, var in enumerate(main_keys):
        print(f"{i+1} : {main_vars[var]["label"]}") ####can always change this to show the actual variable name
    
    main_idx = ut.input_validation("Enter variable number: ", "int", num_range=(1, len(main_keys))) - 1
    var1 = main_keys[main_idx]
    start1 = ut.input_validation("Sweep start value: ", "float") ####add num range somehow
    stop1 = ut.input_validation("Sweep stop value: ", "float") ####same here
    step1 = ut.input_validation("Step: ", "float") ####same here
    vals1 = np.arange(start1, stop1, step1)

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
        sec_vars = sweep_type_filter("sec")
        sec_keys = [key for key in sec_vars if key != var1]

        print("Select secondary variable to sweep:")
        for i, var in enumerate(sec_keys):
            print(f"{i+1} : {sec_vars[var]["label"]}") ####can always change this to show the actual variable name
        
        sec_idx = ut.input_validation("Enter variable number: ", "int", num_range=(1, len(sec_keys)))
        var2 = sec_keys[sec_idx]
        start2 = ut.input_validation("Sweep start value: ", "float") ####add num range somehow
        stop2 = ut.input_validation("Sweep stop value: ", "float") ####same here
        step2 = ut.input_validation("Step: ", "float") ####same here
        vals2 = np.arange(start2, stop2, step2)

        sweep_params = {
            "var1": var1,
            "vals1": vals1,
            "var2": var2,
            "vals2": vals2
        }
        return sweep_params


# Function that handles all sweep logic:
def dispatch(target_dict_var1, target_dict_var2):
    """
    docstring
    """
    # sweep setup
    sweep_mode = select_sweep_mode()
    sweep_params = sweep_setup(sweep_mode)

    # parameter extraction
    var1 = sweep_params["var1"]
    var2 = sweep_params["var2"]
    vals1 = sweep_params["vals1"]
    vals2 = sweep_params["vals2"]
    
    target_dict_list1 = highjack(target_dict_var1, var1, vals1)
    if var2 is not None:
        target_dict_list2 = highjack(target_dict_var2, var2, vals2)
    else:
        target_dict_list2 = target_dict_var2
    return target_dict_list1, target_dict_list2
