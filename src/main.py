# TFG

''' WHAT'S LEFT TO DO:

        Variable sweep functionality:
    - yet to be implemented anywhere. determine which variables can be swept, implement logic to set up the sweeps.

        Results:
    - CHECK CALCULATIONS, STEP BY STEP. SOMETHING IS BEING CALCULATED WRONG.
    - create medatada dictionary or json or something
- should contain data about the simulation itself (iterations, idk what else)
- should contain info about the heat exchanger being tested and about the conditions
- should contain info about how the test was set up (which variable is being swept, values etc.)
    - store results in lists to allow for later plotting

        Plotting and analysis:
    - create new file (analysis.py or something like that) containing all necessary functions for plotting and analysis
    - these shall be called from main.py, and using the results lists and metadata they should be able to create plots and analyse the results
'''

''' NOTES ABOUT THE CURRENT STATE OF THE PROGRAM:

        Input validation:
    - y/n, numeric and dictionary validation implemented!
'''

from CoolProp.HumidAirProp import HAPropsSI
import utils as ut
import fixed_plate
from dataclasses import dataclass

def main():
    """
    docstring
    """
    
    # Function to obtain inlet conditions:
    def inlet_conditions(T_in_C, RH_in):
        """
        Obtains a series of parameters at the inlet of the specified flow for the given inlet conditions. To be applied to each flow.

        Parameters
        ----------
        T_in_C : float
            Inlet temperature of the specified flow [ºC]
        RH_in : float
            Relative humidity of the specified flow at the inlet [0-1]
        
        Returns
        -------
        T_in_K : float
            Inlet temperature of the specified flow [K]
        W_in : float
            Humidity ratio of the specified flow at the inlet [-]
        h_in : float
            Enthalpy of the specified flow at the inlet [J/kg]
        T_dew_K : float
            Dew point of the specified flow at the inlet [K]
        """
        T_in_K = T_in_C + 273.15                                            # K
        W_in = HAPropsSI('W', 'T', T_in_K, 'P', P_ATM, 'R', RH_in)          # -
        #h_in = HAPropsSI('H', 'T', T_in_K, 'P', P_ATM, 'W', W_in)           # J/Kg
        T_dew_K = HAPropsSI('D', 'T', T_in_K, 'P', P_ATM, 'W', W_in)        # K
        
        inlet_dict = {
            "T_in_K": T_in_K,
            "W_in": W_in,
            #"h_in": h_in,
            "T_dew_K": T_dew_K
        }

        return inlet_dict
    
    # Function to update the average temperature:
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


    # LOGIC:

    ''' SOME NOTES REGARDING THE DEVELOPMENT OF THE PROGRAM/SCRIPT:
    INPUTS:
        - currently working with temperatures and relative humidities. allow for other possibilites (like W, dew point, ...)?
        - using interior/exterior setup. allow for hot/cold inputs directly?
    FLUIDS:
        - allow for things other than air?
    GENERAL:
        - create different modes? for heat recovery ventilators (what i'm currently working with), other heat exchanger uses, etc.
    '''

    # User program interrupt
    try:

        # Program startup
        print("\n...\nCurrent functionalities:\n...")

        print("\nCurrent mode: HRV (heat recovery ventilator)\n")

        # Inputs
        P_ATM = 101325 #Pa --- is this ok or do we want more precision?

        T_ext = ut.input_validation("Enter exterior temperature [ºC]: ", "float")
        RH_ext = ut.input_validation("Enter exterior relative humidity [0-1]: ", "float", num_range=(0, 1))
        T_int = ut.input_validation("\nEnter interior temperature [ºC]: ", "float")
        RH_int = ut.input_validation("Enter interior relative humidity [0-1]: ", "float", num_range=(0, 1))

        v_dot = ut.input_validation("\nEnter volumetric flow rate [m3/s]: ", "float") #is this written correctly?

        # Inlet sorting
        if T_ext >= T_int:
            T_hot_in_C = T_ext
            RH_hot_in = RH_ext
            T_cold_in_C = T_int
            RH_cold_in = RH_int
            hvac_config = "cooling"
        else:
            T_hot_in_C = T_int
            RH_hot_in = RH_int
            T_cold_in_C = T_ext
            RH_cold_in = RH_ext
            hvac_config = "heating"
        
        # Inlet conditions
        hot_inlet_dict = inlet_conditions(T_hot_in_C, RH_hot_in)
        cold_inlet_dict = inlet_conditions(T_cold_in_C, RH_cold_in)

        # Temperature iterative loop variable initiation
        T_hot_in_K = hot_inlet_dict["T_in_K"]
        T_cold_in_K = cold_inlet_dict["T_in_K"]
        W_hot_in = hot_inlet_dict["W_in"]
        W_cold_in = cold_inlet_dict["W_in"]

        T_hot_out_K = T_hot_in_K
        T_hot_out_K_old = -273.15
        T_cold_out_K = T_cold_in_K
        T_cold_out_K_old = -273.15

        iteration_num = 0

        # Iteration loop:
        try:
            # Fixed-plate inputs
            fixed_plate_dict = fixed_plate.fixed_plate_inputs()

            while True:
                # Remaining inlet conditions and other parameters
                T_avg_hot_K = temp_avg(T_hot_in_K, T_hot_out_K)
                T_avg_cold_K = temp_avg(T_cold_in_K, T_cold_out_K)
                T_wall_K = fixed_plate.temp_wall(T_avg_hot_K, T_avg_cold_K)

                hot_param_update_dict = fixed_plate.param_update(P_ATM, T_avg_hot_K, T_wall_K, W_hot_in, v_dot)
                cold_param_update_dict = fixed_plate.param_update(P_ATM, T_avg_cold_K, T_wall_K, W_cold_in, v_dot)

                U_total, area = fixed_plate.fixed_plate_UA(fixed_plate_dict, hot_param_update_dict, cold_param_update_dict)
                #this function should be internally calling "thermal_resistance" and it shouldn't be causing any problems. make sure it's working properly!!

                output_dict = fixed_plate.counterflow_output(P_ATM, hot_inlet_dict, cold_inlet_dict, hot_param_update_dict, cold_param_update_dict, area, U_total)
                iteration_num += 1

                T_hot_out_K = output_dict["T_hot_out_K"]
                T_cold_out_K = output_dict["T_cold_out_K"]
                q_real = output_dict["q_real"]

                if abs(T_hot_out_K - T_hot_out_K_old) <= 0.05 and abs(T_cold_out_K - T_cold_out_K_old) <= 0.05:
                    print("T_hot_out_K: ", T_hot_out_K)
                    print("T_cold_out_K: ", T_cold_out_K)
                    print("q_real", q_real)
                    print(iteration_num)
                    break
                else:
                    T_hot_out_K_old = T_hot_out_K
                    T_cold_out_K_old = T_cold_out_K

        except KeyboardInterrupt:
            print("\nCalculations interrupted.") ####placeholder

        # Results:
        print("\nResults:") ####placeholder placeholder placeholder placeholder

    except KeyboardInterrupt:
        print("\nprogram interrupted\nexiting...")

    print("\nexiting...")

if __name__ == "__main__":
    main()