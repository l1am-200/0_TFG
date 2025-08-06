# TFG

'''
houses "universal" functions related to engineering (so not input validation things, for example)
(text needs work)
'''


# ITERATION LOOP

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


# THERMAL (???)

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
