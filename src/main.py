# TFG

''' WHAT'S LEFT TO DO:
        Plotting and analysis:
    - create new file (analysis.py or something like that) containing all necessary functions for plotting and analysis
    - these shall be called from main.py, and using the results lists and metadata they should be able to create plots and analyse the results
'''

''' NOTES ABOUT THE CURRENT STATE OF THE PROGRAM:

        Input validation:
    - y/n, numeric and dictionary validation implemented!

        Results:
    - calculation problem seems to have been solved, although further inspection is required (everything converges after 3 iterations)
    - currently storing probably more than enough info, although the format needs to be cleaned up.

        Variable sweeps:
    - program currently requests all inputs, then overwrites the selected sweep variables. ideally, the user would select and set the swept variable first, and then input
    the rest of the variables. to be corrected in the future.
'''

import utils as ut
import variable_sweeps as vs
import hrv
import fixed_plate as fp

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
    def run_iteration(hrv_inlet_std, fixed_plate_dict):
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
            while True:
                # Remaining inlet conditions and other parameters
                T_avg_hot_K = temp_avg(T_hot_in_K, T_hot_out_K)
                T_avg_cold_K = temp_avg(T_cold_in_K, T_cold_out_K)
                T_wall_K = fp.temp_wall(T_avg_hot_K, T_avg_cold_K)

                hot_param_update_dict = fp.param_update(P_ATM, T_avg_hot_K, T_wall_K, W_hot_in, v_dot)
                cold_param_update_dict = fp.param_update(P_ATM, T_avg_cold_K, T_wall_K, W_cold_in, v_dot)

                U_total, area = fp.fixed_plate_UA(fixed_plate_dict, hot_param_update_dict, cold_param_update_dict)

                output_dict = fp.counterflow_output(P_ATM, hrv_inlet_std, hot_param_update_dict, cold_param_update_dict, area, U_total)
                iteration_num += 1

                T_hot_out_K = output_dict["T_hot_out_K"]
                T_cold_out_K = output_dict["T_cold_out_K"]
                q_real = output_dict["q_real"]

                if abs(T_hot_out_K - T_hot_out_K_old) <= 0.05 and abs(T_cold_out_K - T_cold_out_K_old) <= 0.05:
                    break
                else:
                    T_hot_out_K_old = T_hot_out_K
                    T_cold_out_K_old = T_cold_out_K

        except KeyboardInterrupt:
            print("\nCalculations interrupted.") ####placeholder
            
        results = {
            "q_real": q_real,
            "T_hot_out_K": T_hot_out_K,
            "T_cold_out_K": T_cold_out_K,
            "iteration_num": iteration_num
        }
            
        return results


    # LOGIC:

    try:
        # Program startup
        print("\n...\nCurrent functionalities:\n...")
        print("\nCurrent mode: HRV (Heat Recovery Ventilator)\nPress [ctrl]+[c] at any moment to exit the program\n")

        metadata = {
            "module": "hvac",
            "mode": "hrv",
            "heat_exchanger": "fixed_plate",
            "counterflow": "true"
        }
        results_list = []

        # Inputs:       (to be modified/moved in the future)
        hrv_input_dict = hrv.inlet_prompts()
        fixed_plate_dict = fp.fixed_plate_inputs()
        metadata["hrv_inputs"] = hrv_input_dict
        metadata["fixed_plate_inputs"] = fixed_plate_dict

        # Component lookup:
        component_lookup = {
            "hrv": hrv_input_dict,
            "fp": fixed_plate_dict
        }

        # Variable sweep prompt
        sweep_ok = ut.input_validation("Conduct variable sweep? [y/n]: ", "y/n")
        if sweep_ok == "y":
            # import sweep elements (variables and values)
            sweep_elements = vs.sweep_logic()

            if len(sweep_elements) == 4:
                # element extraction
                vals2 = sweep_elements[0]
                vals1 = sweep_elements[1]
                var2 = sweep_elements[2]
                var1 = sweep_elements[4]
                # metadata
                metadata["sweep_var1"] = {"variable": var1, "values": vals1}
                metadata["sweep_var2"] = {"variable": var2, "values": vals2}
                for val in vals2:
                    vs.highjack(component_lookup, var2, val)
                    for val in vals1:
                        vs.highjack(component_lookup, var1, val)
                        hrv_inlet_std = hrv.hrv_logic(P_ATM, hrv_input_dict)
                        results = run_iteration(hrv_inlet_std, fixed_plate_dict)
                        results_list.append(results)
            elif len(sweep_elements) == 2:
                # element extraction
                vals1 = sweep_elements[0]
                var1 = sweep_elements[1]
                # metadata
                metadata["sweep_var1"] = {"variable": var1, "values": vals1}
                metadata["sweep_var2"] = False
                for val in vals1:
                    vs.highjack(component_lookup, var1, val)
                    hrv_inlet_std = hrv.hrv_logic(P_ATM, hrv_input_dict)
                    results = run_iteration(hrv_inlet_std, fixed_plate_dict)
                    results_list.append(results)

            # magic
            '''
            for i in enumerate((len(sweep_elements)/2)-1):      # len(sweep_elements) is either 2 or 4, so (len(sweep_elements)/2)-1 is either 0 or 1
                for val in sweep_elements[i]:
                    vs.highjack((len(sweep_elements)/2), val)
                    if len(sweep_elements) == 4:
                        for val in sweep_elements[1]:
                            vs.highjack(sweep_elements[3], val)
                            hrv_inlet_std = hrv.hrv_logic(P_ATM, hrv_input_dict)
                            results = run_iteration(hrv_inlet_std, fixed_plate_dict)
                            results_list.append(results)
                    else:
                        hrv_inlet_std = hrv.hrv_logic(P_ATM, hrv_input_dict)
                        results = run_iteration(hrv_inlet_std, fixed_plate_dict)
            '''

        else:
            print("Single simulation mode selected")
            hrv_inlet_std = hrv.hrv_logic(P_ATM, hrv_input_dict)
            results = run_iteration(hrv_inlet_std, fixed_plate_dict)
            results_list.append(results)
            # metadata
            metadata["sweep_var1"] = False
            metadata["sweep_var2"] = False
            metadata["iteration_num"] = results["iteration_num"]

        # Results
        results = run_iteration(hrv_inlet_std, fixed_plate_dict)
        print("\nResults:")
        for key, item in results.items():
            print(key, "->", item)
    
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    
    # Exit message
    print("\n\nExiting...")

if __name__ == "__main__":
    main()