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
import core.heatx as hx
import variable_sweeps as vs
import modules.hvac.hrv as hrv
import exchangers.fixed_plate as fp

def main():
    """
    docstring
    """
    
    P_ATM = 101325      # pressure [Pa]             #### USER-INPUTTED PRESSURE?


    # LOGIC:

    try:
        # Program startup:
        print("\nPROGRAM STARTUP\n")

        # Module and selection:
        module, mode = hx.module_select(hx.module_dict)

        # Heat exchanger selection:
        heat_ex_type, heat_ex_subtype = hx.heat_ex_select(hx.heat_ex_dict)

        print(f"\nModule : {hx.module_dict[module]["name"]}\n  Mode : {hx.module_dict[module]["modes"][mode]}") if mode is not None else print(f"\nModule : {hx.module_dict[module]["name"]}")
        print(f"\nHeat exchanger : {hx.heat_ex_dict[heat_ex_type]["name"]}") ####missing subtype print

        metadata = {
            "module": module,
            "mode": mode,
            "heat_ex_type": heat_ex_type,
            "heat_ex_subtype": heat_ex_subtype
        }

        results_list = []

        print("\nVariable sweep:")
        sweep_ok = vs.conduct_sweep()

        if mode == "hrv":
            calc_results_list = hrv.dispatch(P_ATM, sweep_ok, heat_ex_type)
    
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    
    # Exit message
    print("\n\nExiting...")

if __name__ == "__main__":
    main()