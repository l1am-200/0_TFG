# TFG

''' WHAT'S LEFT TO DO:

        Variable sweep functionality:
    - yet to be implemented anywhere. determine which variables can be swept, implement logic to set up the sweeps.

        Results:
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

        Results:
    - calculation problem seems to have been solved, although further inspection is required.
'''

from CoolProp.HumidAirProp import HAPropsSI
import utils as ut
import hrv
import fixed_plate
from dataclasses import dataclass

def main():
    """
    docstring
    """
    
    P_ATM = 101325      # pressure [Pa]             #### USER-INPUTTED PRESSURE?
    
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
        
    # Iteration loop function
    def run_iteration(hrv_inlet_std):
        """
        docstring
        """

        # Input extraction
        T_hot_in_K = hrv_inlet_std["T_hot_in_K"]
        T_cold_in_K = hrv_inlet_std["T_cold_in_K"]
        v_dot = hrv_inlet_std["v_dot"]
        W_hot_in = hrv_inlet_std["W_hot_in"]
        W_cold_in = hrv_inlet_std["W_cold_in"]

        # Temperature iterative loop variable initiation
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

                output_dict = fixed_plate.counterflow_output(P_ATM, hrv_inlet_std, hot_param_update_dict, cold_param_update_dict, area, U_total)
                iteration_num += 1

                T_hot_out_K = output_dict["T_hot_out_K"]
                T_cold_out_K = output_dict["T_cold_out_K"]
                q_real = output_dict["q_real"]

                if abs(T_hot_out_K - T_hot_out_K_old) <= 0.05 and abs(T_cold_out_K - T_cold_out_K_old) <= 0.05:
                    print(iteration_num)
                    break
                else:
                    T_hot_out_K_old = T_hot_out_K
                    T_cold_out_K_old = T_cold_out_K

        except KeyboardInterrupt:
            print("\nCalculations interrupted.") ####placeholder
            
        results = {
            "q_real": q_real,
            "T_hot_out_K": T_hot_out_K,
            "T_cold_out_K": T_cold_out_K
        }
            
        return results


    # LOGIC:

    try:
        # Program startup
        print("\n...\nCurrent functionalities:\n...")
        print("\nCurrent mode: HRV (heat recovery ventilator)\nPress [ctrl]+[c] at any moment to exit the program\n")

        # HRV general import (to be changed in the future)
        hrv_inlet_std = hrv.hrv_logic(P_ATM)

        # Results
        results = run_iteration(hrv_inlet_std)
        print("\nResults:")
        for key, item in results.items():
            print(key, "->", item)
    
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    
    # Exit message
    print("\n\nExiting...")

if __name__ == "__main__":
    main()