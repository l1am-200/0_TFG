# TFG

''' WHAT'S LEFT TO DO:

        Input validation:
    - directory input validation.

        Plotting and analysis:
    - create new file (analysis.py or something like that) containing all necessary functions for plotting and analysis
    - these shall be called from main.py, and using the results lists and metadata they should be able to create plots and analyse the results

        Results:
    - numbers should be rounded to 3 or 4 decimals.
    - humidity-related outlet data is currently not included and should be added.

        Saving results (and plots):
    - implement option to save files containing test data and the plots used for analysis.

        Final review:
    - review all files, complete docstrings, resolve and remove any annotations left behind.
    - fixed_plate.py: enhance material library, specify source for material properties.
    - units: make sure everything is in the expected units
'''

''' NOTES ABOUT THE CURRENT STATE OF THE PROGRAM (AND FUTURE IMPROVEMENTS):

        "core" folder:
    - split heatx.py into two files, one for general software things and one for general math/physics things.

        aesthetic changes:
    - make sure console print-outs are easy to read.

        Heat exchangers:
    - non-counterflow-type heat exchanger functionality (F-factor).

        Results:
    - calculation problem seems to have been solved, although further inspection is required (everything converges after 3 iterations)

        Variable sweeps:
    - program currently requests all inputs, then overwrites the selected sweep variables. ideally, the user would select and set the swept variable first, and then input
    the rest of the variables. to be corrected in the future.

        Input/Output refactor:
    - all user inputs should be handled via a separate module.

        More specific:
    - chevron angle input in fixed_plate.py accepts any integer, but the calculation process will throw an error if the entered value is not one of the values that work for
    Kumar's 1984 correlation and values. basically, this input needs to only allow certain values (30, 45, 60, ...)
'''

import json
import utils as ut
import variable_sweeps as vs
import core.metadata_mgmt as md
import core.heatx as hx
import modules.hvac.hrv as hrv
import analysis.plots as plots
import exchangers.fixed_plate as fp

def main():
    """
    docstring
    """
    
    md.metadata_clear()

    from core.config import P_ATM
    md.metadata_set("pressure_inlet", P_ATM)


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

        # Metadata update:
        metadata_general = {
            "module": module,
            "mode": mode,
            "heat_ex_type": heat_ex_type,
            "heat_ex_subtype": heat_ex_subtype
        }
        md.metadata_update(metadata_general)

        # Variable sweep prompt:
        print("\n\nVariable sweep:")
        sweep_ok = vs.conduct_sweep()

        # Calculation dispatch block:
        if mode == "hrv":
            calc_results_list = hrv.dispatch(P_ATM, module, mode, sweep_ok, heat_ex_type)
            print("\nHRV calculations conducted successfully.")
        
        # Result plotting:
        end_metadata = md.metadata_fetch()
        if sweep_ok == "y":
            plots.plot_dispatch(calc_results_list, end_metadata)
        else:
            print("\n\nResults:")
            print(calc_results_list) #temporary
            print("\nMetadata:")
            print(end_metadata) #temporary
    
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    
    # Exit message
    print("\n\nExiting...")

if __name__ == "__main__":
    main()