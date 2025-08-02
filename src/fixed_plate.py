# TFG
# Script for UA and geometry calculations for fixed-plate heat exchangers

import numpy as np
from CoolProp.HumidAirProp import HAPropsSI
from CoolProp.CoolProp import PropsSI
import utils as ut
from dataclasses import dataclass

# Plate material dictionary:
plate_materials = {
    'Aluminum': 'Al',
    'Copper': 'Cu'
}

# Plate material dictionary key aliases:
material_aliases = {
    'aluminum': 'al',
    'aluminium': 'al',
    'al': 'al',
    'copper': 'cu',
    'cu': 'cu'
}

# Thermal conductivity of different metals:
K_metals = {
    'al': 238.5,
    'cu': 403
} #UNFINISHED UNFINISHED UNFINISHED UNFINISHED
# sourced from (formulario de la asignatura lol), interpolated to 300K

# Kumar's constants for single-phase heat transfer and pressure loss in fixed-plate heat exchangers (((MAY NOT BE VALID??? IDK CHECK)))
chevron_list = [30, 45, 50, 60, 65]
Re_array1 = [[10], [10, 100], [20, 300], [20, 400], [20, 500]]
C_h_array = [[0.718, 0.348], [0.718, 0.400, 0.300], [0.630, 0.291, 0.130], [0.562, 0.306, 0.108], [0.562, 0.331, 0.087]]
y_array = [[0.349, 0.663], [0.349, 0.598, 0.663], [0.333, 0.591, 0.732], [0.326, 0.529, 0.703], [0.326, 0.503, 0.718]]
Re_array2 = [[10, 100], [15, 300], [20, 300], [40, 400], [50, 500]]
k_p_array = [[50, 19.4, 2.99], [47, 18.29, 1.441], [34, 11.25, 0.772], [24, 3.24, 0.76], [24, 2.8, 0.639]]
z_array = [[1, 0.589, 0.183], [1, 0.652, 0.206], [1, 0.631, 0.161], [1, 0.457, 0.215], [1, 0.451, 0.213]]

# Function to update the wall temperature:
def temp_wall(T_avg_hot_K, T_avg_cold_K):
    """
    Calculates the temperature (average) at the plate surfaces inside the heat exchanger.

    Parameters
    ----------
    T_avg_hot_K : float
        Average temperature of the hot stream [K]
    T_avg_cold_K : float
        Average temperature of the cold stream [K]
    
    Returns
    -------
    T_wall_K : float
        Average temperature at the surface of the plates inside the heat exchanger [K]
    """
    T_wall_K = (T_avg_hot_K + T_avg_cold_K) / 2
    return T_wall_K

# Function to update parameters for iteration (description can be worked on):
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
        Mass flow rate of condensate [kg/s]. defaults to 0 if left unspecified.

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
    P_w = HAPropsSI('P_w', 'T', T_avg_K, 'P', P_ATM, 'W', W)
    P_d = P_ATM - P_w
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

def fixed_plate_inputs():
    """
    docstring
    """
    material = ut.input_validation("Available plate materials: ", "dict", dictionary=plate_materials, aliases=material_aliases) # plate material (chosen from list)
    K_plates = K_metals[material]
    N_p = ut.input_validation("Enter number of plates: ", "int")                                    # number of plates
    L_p = ut.input_validation("Enter plate effective length [m]: ", "float")                        # plate effective length [m]
    plate_width = ut.input_validation("Enter plate width [m]: ", "float")                           # plate width [m]
    plate_thickness = ut.input_validation("Enter plate thickness [m]: ", "float")                   # plate thickness [m]
    chevron_angle = ut.input_validation("Enter chevron angle [º]: ", "float")                       # chevron angle [º]
    corr_ampl = ut.input_validation("Enter corrugation amplitude [m]: ", "float")                   # corrugation amplitude [m]
    lambda_upper = 1.175                 # uppercase lambda, developed length / protracted length (see slide 46, tema 6 IC 22-23) (1.1-1.25) ####FORCING IT TO 1.175

    area = N_p * L_p * plate_width
    d_e = (4 * corr_ampl * plate_width) / (2 * (corr_ampl + (lambda_upper * plate_width)))          # equivalent hydraulic diameter (used to calculate Re)

    # thermal resistance calculations:
    Rprime_cond_1plate = plate_thickness / K_plates

    # return
    fixed_plate_dict = {
        "K_plates": K_plates,
        "N_p": N_p,
        "L_p": L_p,
        "plate_width": plate_width,
        "plate_thickness": plate_thickness,
        "chevron_angle": chevron_angle,
        "corr_ampl": corr_ampl,
        "lambda_upper": lambda_upper,
        "d_e": d_e,
        "area": area,
        "Rprime_cond_1plate": Rprime_cond_1plate,
    }

    return fixed_plate_dict

def thermal_resistance(param_update_dict, fixed_plate_dict):
    """
    Calculates the thermal resistance to convection of a single plate, and in total for one of the heat exchanger flows. To be applied to each flow.

    Parameters
    ----------
    cp : float
        Specific heat capacity (at constant pressure) for the specified flow [J/kg·K]
    K_air : float
        Thermal conductivity of the air for the specified flow [W/m·K]
    visc : float
        Viscosity of the air for the specified flow, evaluated at the average temperature for that flow [Pa·s]
    visc_wall : float
        Viscosity of the air, evaluated at wall temperature (average surface temperature of the plates in the heat exchanger), flow-independent [Pa·s]
    N_p : int
        Number of plates in the heat exchanger [-]
    plate_width : float
        Width of the plates [m]
    corr_ampl : float
        Corrugation amplitude [m]
    K_plates : float
        Thermal conductivity of the heat exchanger plates [W/m·K]
    d_e : float
        Equivalent hydraulic diameter [m]
    m_dot : float
        Mass flow rate for the specified flow [kg/s]
    
    Returns
    -------
    Rprime_conv_1plate : float
        Thermal resistance to convection (per unit area) for one plate, for the specified flow [K/W·m2]
    Rprime_conv : float
        Thermal resistance to convection (per unit area) for the whole heat exchanger, for the specified flow [K/W·m2]
    """
    # input extraction
    m_dot = param_update_dict["m_dot"]
    cp = param_update_dict["cp"]
    K_air = param_update_dict["K_air"]
    visc = param_update_dict["visc"]
    visc_wall = param_update_dict["visc_wall"]

    N_p = fixed_plate_dict["N_p"]
    L_p = fixed_plate_dict["L_p"]
    plate_width = fixed_plate_dict["plate_width"]
    chevron_angle = fixed_plate_dict["chevron_angle"]
    corr_ampl = fixed_plate_dict["corr_ampl"]
    d_e = fixed_plate_dict["d_e"]
    
    G_ch = m_dot / (corr_ampl * plate_width * (N_p / 2))
    Re = (G_ch * d_e) / visc

    # assigning Kumar's constants to calculate Nu correctly depending on the exchanger's geometry
    if chevron_angle <= chevron_list[0]:
        if Re <= Re_array1[0][0]:
            C_h = C_h_array[0][0]
            y = y_array[0][0]
        else:
            C_h = C_h_array[0][1]
            y = y_array[0][1]
    elif chevron_angle >= chevron_list[4]:
        if Re < Re_array1[4][0]:
            C_h = C_h_array[4][0]
            y = y_array[4][0]
        elif Re >= Re_array1[4][0] and Re <= Re_array1[4][1]:
            C_h = C_h_array[4][1]
            y = y_array[4][1]
        else:
            C_h = C_h_array[4][2]
            y = y_array[4][2]
    else:
        for i in range(len(chevron_list) - 2):
            if chevron_angle == chevron_list[i + 1]:
                if Re < Re_array1[i + 1][0]:
                    C_h = C_h_array[i + 1][0]
                    y = y_array[i + 1][0]
                elif Re > Re_array1[i + 1][1]:
                    C_h = C_h_array[i + 1][2]
                    y = y_array[i + 1][2]
                else:
                    C_h = C_h_array[i + 1][1]
                    y = y_array[i + 1][1]
    
    Pr = (visc * cp) / K_air
    
    Nu = C_h * (Re ** y) * (Pr ** (1/3)) * ((visc / visc_wall) ** 0.17)

    L_c = d_e                               # using the equivalent hydraulic diameter as the characteristic length (not using d_e directly for readability)
    h_coef = (Nu * K_air) / L_c
    
    Rprime_conv_1plate = 1 / h_coef

    return Rprime_conv_1plate                  #### does this need to be corrected? see slide 14, tema 6 IC 22-23

def fixed_plate_UA(fixed_plate_dict, hot_param_update_dict, cold_param_update_dict):
    """
    Calculates U and A for a fixed-plate heat exchanger, based on information about its geometrical configuration.

    Parameters
    ----------
    m_dot_hot : float
        Mass flow rate for the hot stream [kg/s]
    cp_hot : float
        Specific heat capacity for the hot stream [J/kg·K]
    K_air_hot : float
        Thermal conductivity of the hot stream [W/m·K]
    visc_hot : float
        Viscosity of the hot stream [Pa·s]
    visc_wall : float
        Viscosity evaluated at wall temperature (average surface temperature of the heat exchanger's plates) [Pa·s]
    m_dot_cold : float
        Mass flow rate for the cold stream [kg/s]
    cp_cold : float
        Specific heat capacity for the cold stream [J/kg·K]
    K_air_cold : float
        Thermal conductivity of the cold stream [W/m·K]
    visc_cold : float
        Viscosity of the cold stream [Pa·s]
    
    Returns
    -------
    U_total : float
        Global heat transfer coefficient for the whole heat exchanger [W/m2·K]
    area : float
        Total area used for heat transfer inside the heat exchanger [m2]
    """
    # input extraction
    area = fixed_plate_dict["area"]
    Rprime_cond_1plate = fixed_plate_dict["Rprime_cond_1plate"]

    # convective thermal resistance calculations
    Rprime_conv_1plate_hot = thermal_resistance(hot_param_update_dict, fixed_plate_dict)         # hot flow
    Rprime_conv_1plate_cold = thermal_resistance(cold_param_update_dict, fixed_plate_dict)      # cold flow

    Rprime_1plate = Rprime_cond_1plate + Rprime_conv_1plate_cold + Rprime_conv_1plate_hot

    U_total = 1 / Rprime_1plate                 # global heat transfer coefficient [W/m2·K] (is this correct?)

    return U_total, area

def counterflow_output(P_ATM, hot_inlet_dict, cold_inlet_dict, hot_param_update_dict, cold_param_update_dict, area, U_total):
    """
    Calculates NTU, epsilon, transferred heat and outlet temperatures for a fixed-plate counterflow heat exchanger.

    Parameters
    ----------
    P_ATM : float
        Atmospheric pressure [Pa]
    
    Returns
    -------
    q_real : float
        Exchanged heat
    T_hot_out_K : float
        Outlet temperature of the hot stream [K]
    """
    # input extraction
    T_hot_in_K = hot_inlet_dict["T_in_K"]
    T_cold_in_K = cold_inlet_dict["T_in_K"]
    W_hot_in = hot_inlet_dict["W_in"]
    W_cold_in = cold_inlet_dict["W_in"]
    T_dew_hot_K = hot_inlet_dict["T_dew_K"]

    m_dot_hot = hot_param_update_dict["m_dot"]
    m_dot_cold = cold_param_update_dict["m_dot"]
    cp_hot = hot_param_update_dict["cp"]
    cp_cold = cold_param_update_dict["cp"]

    C_max = max((cp_hot * m_dot_hot), (cp_cold * m_dot_cold))
    C_min = min((cp_hot * m_dot_hot), (cp_cold * m_dot_cold))
    print(f"C_min = {C_min:.2f} W/K")
    R_param = C_min / C_max
    NTU_param = (U_total * area) / C_min

    if abs(1 - R_param) < 0.02:
        epsilon_counterflow = NTU_param / (1 + NTU_param)
    else:
        epsilon_counterflow = (1 - np.exp(-1 * NTU_param * (1 - R_param))) / (1 - (R_param * np.exp(-1 * NTU_param * (1 - R_param))))

    q_real = epsilon_counterflow * C_min * (T_hot_in_K - T_cold_in_K) #T_hot_in & T_cold_in are known

    # cold stream outlet conditions
    h_cold_in = HAPropsSI('H', 'T', T_cold_in_K, 'P', P_ATM, 'W', W_cold_in)
    h_cold_out = h_cold_in + (q_real / m_dot_cold)
    T_cold_out_K = HAPropsSI('T', 'H', h_cold_out, 'P', P_ATM, 'W', W_cold_in) #since the cold stream heats up, condensation will not happen and W will remain constant
    W_cold_out = W_cold_in
    #humidity things !!!!!

    # hot stream outlet conditions
    h_hot_in = HAPropsSI('H', 'T', T_hot_in_K, 'P', P_ATM, 'W', W_hot_in)
    h_hot_out = h_hot_in - (q_real / m_dot_hot)
    T_hot_out_est = HAPropsSI('T', 'H', h_hot_out, 'P', P_ATM, 'W', W_hot_in)

    # condensation check and correction
    if T_hot_out_est > T_dew_hot_K:
        condensation = False
        m_dot_cond = 0
        T_hot_out_K = T_hot_out_est
        W_hot_out = W_hot_in
    else:
        condensation = True
        # air cools down until dew point is reached (sensible heat). then, condensation occurs (latent heat). q_total = q_sensible + q_latent
        h_T_dew_hot = HAPropsSI('H', 'T', T_dew_hot_K, 'P', P_ATM, 'W', W_hot_in)

        q_sens = m_dot_hot * (h_hot_in - h_T_dew_hot)
        q_lat_est = q_real - q_sens                         # latent heat estimate (used later)

        # h_fg is needed to determine the amount of condensate, which in turn is needed to determine W upon exit. h_fg is obtained via the air mixture's saturation pressure
        p_sat = HAPropsSI('P', 'T', T_dew_hot_K, 'Q', 0, 'water')
        h_fg = (HAPropsSI('H', 'P', p_sat, 'Q', 1, 'water')) - (HAPropsSI('H', 'P', p_sat, 'Q', 0, 'water'))
        q_lat_max = (W_hot_in * m_dot_hot) * h_fg           # maximum latent heat that the airstream can release
        if q_lat_est <= q_lat_max:
            q_lat = q_lat_est
            m_dot_cond = q_lat / h_fg
        else:                                               # maximum latent heat possible has been released, the stream continues to cool down via sensible heat transfer
            q_lat = q_lat_max
            m_dot_cond = q_lat / h_fg
            #####airstream continues to cool down, as well as the condensate. this is very difficult to model
            condensation = "maximum" ####temporary fix just to check if we ever get here or not

        W_hot_out = W_hot_in - (m_dot_cond / m_dot_hot)
        T_hot_out_K = HAPropsSI('T', 'H', h_hot_out, 'P', P_ATM, 'W', W_hot_out)

    output_dict = {
        "q_real": q_real,
        "T_hot_out_K": T_hot_out_K,
        "W_hot_out": W_hot_out,
        "T_cold_out_K": T_cold_out_K,
        "W_cold_out": W_cold_out,
        "condensation": condensation,
        "m_dot_cond": m_dot_cond
    }

    return output_dict

''' NOTES REGARDING THE CHANGE IN MASS FLOW RATE CAUSED BY CONDENSATION:

    - If condensation occurs in the heat exchanger, the mass flow rate of humid air sees a slight decrease. This would affect a series of parameters and variables that go into
    calculating the outlet conditions of the heat exchanger, meaning that in order to achieve the highest possible accuracy, this change in mass flow rate should be modelled.

    - However, condensation does not happen immediately upon the air's entry into the heat exchanger. What this means is that those parameters and variables that are affected
    by this change (such as Re), would only see changes in one part of the air's flow path. Modelling this correctly adds a lot of complexity, and simplifying the way of
    modelling this phenomenon introduces inaccuracies. Therefore, for now these changes in mass flow rate will not be modelled.
'''

def pressure_loss(visc, N_p, plate_width, corr_ampl, d_e, m_dot, chevron_angle):
    """
    docstring
    """
    G_ch = m_dot / (corr_ampl * plate_width * (N_p / 2))
    Re = (G_ch * d_e) / visc

    # assigning Kumar's constants
    if chevron_angle <= chevron_list[0]:
        if Re < Re_array2[0][0]:
            k_p = k_p_array[0][0]
            z = z_array[0][0]
        elif Re > Re_array2[0][1]:
            k_p = k_p_array[0][2]
            z = z_array[0][2]
        else:
            k_p = k_p_array[0][1]
            z = z_array[0][1]
    elif chevron_angle >= chevron_list[4]:
        if Re < Re_array2[4][0]:
            k_p = k_p_array[4][0]
            z = z_array[4][0]
        elif Re > Re_array1[4][1]:
            k_p = k_p_array[4][2]
            z = z_array[4][2]
        else:
            k_p = k_p_array[4][1]
            z = z_array[4][1]
    else:
        for i in range(len(chevron_list) - 2):
            if chevron_angle == chevron_list[i + 1]:
                if Re < Re_array2[i + 1][0]:
                    k_p = k_p_array[i + 1][0]
                    z = z_array[i + 1][0]
                elif Re > Re_array1[i + 1][1]:
                    k_p = k_p_array[i + 1][2]
                    z = z_array[i + 1][2]
                else:
                    k_p = k_p_array[i + 1][1]
                    z = z_array[i + 1][1]
    
    c_f = k_p / (Re ** z)
    ####UNFINISHED UNFINISHED UNFINISHED UNFINISHED UNFINISHED
