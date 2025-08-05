# TFG

'''
houses things specific to Heat Recovery Ventilators (HRVs)
'''

import utils as ut
from CoolProp.HumidAirProp import HAPropsSI

# HRV inlet prompts:
def inlet_prompts():
    """
    docstring
    """
    T_ext_C = ut.input_validation("Enter exterior temperature [ºC]: ", "float")
    RH_ext = ut.input_validation("Enter exterior relative humidity [0-1]: ", "float", num_range=(0, 1))
    T_int_C = ut.input_validation("\nEnter interior temperature [ºC]: ", "float")
    RH_int = ut.input_validation("Enter interior relative humidity [0-1]: ", "float", num_range=(0, 1))
    v_dot = ut.input_validation("\nEnter volumetric flow rate [m3/s]: ", "float")

    hrv_input_dict = {
        'T_ext': T_ext_C,
        'RH_ext': RH_ext,
        'T_int': T_int_C,
        'RH_int': RH_int,
        'v_dot': v_dot
    }

    return hrv_input_dict

# Base inlet conditions sorting:
def inlet_sorting(hrv_input_dict):
    """
    docstring
    """
    T_ext_C = hrv_input_dict["T_ext"]
    RH_ext = hrv_input_dict["RH_ext"]
    T_int_C = hrv_input_dict["T_int"]
    RH_int = hrv_input_dict["RH_int"]

    if T_ext_C >= T_int_C:
        T_hot_in_C = T_ext_C
        RH_hot_in = RH_ext
        T_cold_in_C = T_int_C
        RH_cold_in = RH_int
        hvac_config = "cooling"
    else:
        T_hot_in_C = T_int_C
        RH_hot_in = RH_int
        T_cold_in_C = T_ext_C
        RH_cold_in = RH_ext
        hvac_config = "heating"
    
    inlet_sort_dict = {
        "T_hot_in_C": T_hot_in_C,
        "RH_hot_in": RH_hot_in,
        "T_cold_in_C": T_cold_in_C,
        "RH_cold_in": RH_cold_in,
        "hvac_config": hvac_config
    }

    return inlet_sort_dict

def inlet_extras(P_ATM, T_in_K, RH_in):
    """
    Obtains a series of parameters at the inlet of the specified flow for the given inlet conditions. To be applied to each flow.

        Parameters
        ----------
        P_ATM : float
            Atmospheric pressue [Pa]
        T_in_K : float
            Inlet temperature of the specified flow [K]
        RH_in : float
            Relative humidity of the specified flow at the inlet [0-1]
        
        Returns
        -------
        W_in : float
            Humidity ratio of the specified flow at the inlet [-]
        T_dew_K : float
            Dew point of the specified flow at the inlet [K]
    """
    W_in = HAPropsSI('W', 'T', T_in_K, 'P', P_ATM, 'R', RH_in)      # [-]
    T_dew_K = HAPropsSI('D', 'T', T_in_K, 'P', P_ATM, 'W', W_in)    # [K]
    return W_in, T_dew_K


# LOGIC:

def hrv_logic(P_ATM, hrv_input_dict):
    """
    docstring
    """
    # current operating mode: HRV (Heat Recovery Ventilator)
    v_dot = hrv_input_dict["v_dot"]

    inlet_sort_dict = inlet_sorting(hrv_input_dict)

    T_hot_in_C = inlet_sort_dict["T_hot_in_C"]
    RH_hot_in = inlet_sort_dict["RH_hot_in"]
    T_cold_in_C = inlet_sort_dict["T_cold_in_C"]
    RH_cold_in = inlet_sort_dict["RH_cold_in"]

    T_hot_in_K = T_hot_in_C + 273.15
    T_cold_in_K = T_cold_in_C + 273.15

    W_hot_in, T_dew_hot_K = inlet_extras(P_ATM, T_hot_in_K, RH_hot_in)      # hot stream
    W_cold_in, T_dew_cold_K = inlet_extras(P_ATM, T_cold_in_K, RH_cold_in)  # cold stream

    hrv_inlet_std = {
        "T_hot_in_K": T_hot_in_K,
        "T_cold_in_K": T_cold_in_K,
        "RH_hot_in": RH_hot_in,
        "RH_cold_in": RH_cold_in,
        "v_dot": v_dot,
        "W_hot_in": W_hot_in,
        "W_cold_in": W_cold_in,
        "T_dew_hot_K": T_dew_hot_K,
        "T_dew_cold_K": T_dew_cold_K
    }

    return hrv_inlet_std
