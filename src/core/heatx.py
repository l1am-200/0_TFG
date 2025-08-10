# TFG

'''
houses "universal" technical functions related to the program (so not input validation things, for example)
(text needs work)
'''

import utils as ut


# PROGRAM:

# Module and mode dictionary:
module_dict = {
    "hvac": {
        "name": "HVAC",
        "modes": {
            "hrv": "HRV (Heat Recovery Ventilator)"
        }
    }
}

# Heat exchanger dictionary:
heat_ex_dict = {
    "fixed_plate": {
        "name": "Fixed-Plate",
        "subtypes": {
            "counterflow": "Counterflow"
        }
    }
}

# Module and mode selection function:
def module_select(module_dict):
    """
    docstring
    """
    print("\nSelect program module:")
    for i, element in enumerate(module_dict):
        print(f"{i+1} : {module_dict[element]["name"]}")
    
    user_num = ut.input_validation("Enter module number: ", "int", num_range=(1, len(module_dict)))
    for i, element in enumerate(module_dict):
        if user_num == i+1:
            module = element
    
    if module_dict[module]["modes"] is not None:
        print("\n Select mode:")
        for i, element in enumerate(module_dict[module]["modes"]):
            print(f"{i+1} : {module_dict[module]["modes"][element]}")

        user_num = ut.input_validation("Enter mode number: ", "int", num_range=(1, len(module_dict[module]["modes"])))
        for i, element in enumerate(module_dict[module]["modes"]):
            if user_num == i+1:
                mode = element
        return module, mode
    else:
        return module, None

# Heat exchanger selection function:
def heat_ex_select(heat_ex_dict):
    """
    docstring
    """
    print("\nSelect heat exchanger type:")
    for i, element in enumerate(heat_ex_dict):
        print(f"{i+1} : {heat_ex_dict[element]["name"]}")
    
    user_num = ut.input_validation("Enter type number: ", "int", num_range=(1, len(heat_ex_dict)))
    for i , element in enumerate(heat_ex_dict):
        if user_num == i+1:
            heat_ex_type = element
    
    if heat_ex_dict[heat_ex_type]["subtypes"] is not None:
        print("\nSelect heat exchanger subtype:")
        for i, element in enumerate(heat_ex_dict[heat_ex_type]["subtypes"]):
            print(f"{i+1} : {heat_ex_dict[heat_ex_type]["subtypes"][element]}")
    
        user_num = ut.input_validation("Enter subtype number: ", "int", num_range=(1, len(heat_ex_dict[heat_ex_type]["subtypes"])))
        for i, element in enumerate(heat_ex_dict[heat_ex_type]["subtypes"]):
            if user_num == i+1:
                heat_ex_subtype = element
        return heat_ex_type, heat_ex_subtype
    else:
        return heat_ex_type, None

# Heat exchanger import prefix:
def exchanger_prefix(heat_ex_type):
    heat_ex_prefix = ut.file_management[heat_ex_type]
    return heat_ex_prefix


# SAVING FILES:




# ITERATION LOOP:

# Iterative loop temperature initialization function:
def temp_init(T_hot_in_K, T_cold_in_K):
    """
    docstring
    """
    T_hot_out_K = T_hot_in_K
    T_hot_out_K_old = -273.15
    T_cold_out_K = T_cold_in_K
    T_cold_out_K_old = -273.15
    return T_hot_out_K, T_hot_out_K_old, T_cold_out_K, T_cold_out_K_old


# OTHER:

# Average temperature function:
def temp_avg(T_in_K, T_out_K):
    """
    Calculates the average temperature for the specified heat exchanger flow. To be applied to each flow.

    Parameters
    ----------
    T_in_K : float
        Inlet temperature [K]
    T_out_K : float
        Outlet temperature [K]
        
    Returns
    -------
    T_avg_K : float
        Average stream temperature [K]
    """
    T_avg_K = (T_in_K + T_out_K) / 2
    return T_avg_K
