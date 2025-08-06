# TFG

'''
houses things specific to Heat Recovery Ventilators (HRVs)
'''

import utils as ut
import core.engineering_logic as enl
import exchangers.fixed_plate as fp
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI

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

# Additional inlet data:
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

# HRV-related parameter update function:
def param_update(P_ATM, T_avg_K, T_wall_K, W, v_dot, m_dot_cond=0):
    """
    Updates parameters/variables used for later calculations based on the inputs. To be used inside an iteration loop and to be applied to each flow.

    Parameters
    ----------
    P_ATM : float
        Atmospheric pressure [Pa]
    T_avg_K : float
        Average temperature of the specified flow [K]
    T_wall_K : float
        Average temperature at the surface of the heat exchanger's plates (independent of specified flow) [K]
    W : float
        Humidity ratio of the specified flow [-]
    v_dot : float
        Volumetric flow rate of the specified flow [m3/s]
    m_dot_cond : float
        [OPTIONAL] Mass flow rate of condensate [kg/s]. defaults to 0 if left unspecified.

    Returns
    -------
    m_dot : float
        Updated mass flow rate for the specified flow [kg/s]
    cp : float
        Updated specific heat capacity at constant pressure for the specified flow [J/kg·K]
    K_air : float
        Updated thermal conductivity of the air for the specified flow [W/m·K]
    visc : float
        Updated viscosity of the air for the specified flow, evaluated at the average temperature for that flow [Pa·s]
    visc_wall : float
        Updated viscosity of the air, evaluated at wall temperature (average surface temperature of the plates in the heat exchanger), flow-independent [Pa·s]
    m_dot_min : float
        Updated mass flow rate of the specified flow, obtained by subtracting the condensate mass flow rate [kg/s]
    """
    # partial pressures
    P_w = HAPropsSI('P_w', 'T', T_avg_K, 'P', P_ATM, 'W', W)
    P_d = P_ATM - P_w

    # densities
    rho_dry = PropsSI('D', 'T', T_avg_K, 'P', P_d, 'Air')
    rho_vap = PropsSI('D', 'T', T_avg_K, 'P', P_w, 'Water')
    rho = rho_dry + (W * rho_vap)                                                               # density [Kg/m3]
    
    m_dot = rho * v_dot                                                                         # mass flow rate [Kg/s]
    cp = HAPropsSI('C', 'T', T_avg_K, 'P', P_ATM, 'W', W)                                       # specific heat [J/Kg·K]
    K_air = HAPropsSI('K', 'T', T_avg_K, 'P', P_ATM, 'W', W)                                    # conductivity [W/m·K]
    visc = PropsSI('VISCOSITY', 'T', T_avg_K, 'P', P_ATM, 'Air') * (1 + 0.0026 * W)             # viscosity [Pa·s]
    visc_wall = PropsSI('VISCOSITY', 'T', T_wall_K, 'P', P_ATM, 'Air') * (1 + 0.0026 * W)       # viscosity at wall [Pa·s]

    m_dot_min = m_dot - m_dot_cond

    param_update_dict = {
        "m_dot": m_dot,
        "cp": cp,
        "K_air": K_air,
        "visc": visc,
        "visc_wall": visc_wall,
        "m_dot_min": m_dot_min
    }

    return param_update_dict


# LOGIC:

# Creation of standardized HRV inlet dictionary:
def inlet_standard(P_ATM, hrv_input_dict):
    """
    docstring
    """
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

# Execution of HRV-specific calculations:
def hrv_interation(hrv_inlet_std):
    """
    docstring
    """
    T_hot_in_K = hrv_inlet_std["T_hot_in_K"]
    T_cold_in_K = hrv_inlet_std["T_cold_in_K"]
    v_dot = hrv_inlet_std["v_dot"]
    W_hot_in = hrv_inlet_std["W_hot_in"]
    W_cold_in = hrv_inlet_std["W_cold_in"]

    T_hot_out_K, T_hot_out_K_old, T_cold_out_K, T_cold_out_K_old = enl.temp_init(T_hot_in_K, T_cold_in_K)
