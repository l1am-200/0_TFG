# TFG
# Script housing a series of functions used throughout the program ((work on this))

# Main input validation function:
def input_validation(prompt, mode, **kwargs):
    """
    docstring
    
    Args:
        prompt (str): Displayed message to user
        mode (str): Input mode to validate
    
    Modes:
        - "y/n" (no additional arguments)
        - "int" (optional: num_range)
        - "float" (optional: num_range)
        - "dict" (needed: dictionary, aliases)
    
    Returns:
        input_valid : Validated input
    """
    if mode == "y/n":
        return validate_y_n(prompt)
    elif mode == "int" or mode == "float":
        return validate_num(prompt, mode, kwargs.get("num_range"))
    elif mode == "dict":
        return validate_dict(prompt, kwargs.get("display"), kwargs.get("aliases"))
    else:
        print("Validation function error.")

# [y]/[n] input validation function:
def validate_y_n(prompt):
    """
    Prompts for a [y]/[n] input and validates.
    """
    while True:
        user_input = input(prompt).strip().lower()
        if user_input == "y" or user_input == "n":
            return user_input
        else:
            print("Invalid input. Please enter [y] or [n].")

# Numeric input validation function:
def validate_num(prompt, mode, num_range=None):
    """
    Prompts for a numeric input. Optional range validation.
    """
    check = int if mode == "int" else float
    while True:
        user_input = input(prompt).strip()
        try:
            user_input = check(user_input)
            if num_range and not (num_range[0] <= user_input <= num_range[1]):
                print(f"Number must be between {num_range[0]} and {num_range[1]}")
                continue
            return user_input
        except ValueError:
            print("Invalid input. Please enter a", "n integer." if mode == "int" else " number.")

# Dictionary input validation function:
def validate_dict(prompt, display, aliases):
    """
    docstring
    Please note: prompts must be written in the following style: "Available [...]:". This function will automatically prompt the user for a choice.
    """
    while True:
        print(prompt)
        for key in display:
            print(f"{key}")
        user_input = input("Choice: ").strip().lower()
        if user_input in aliases:
            return aliases[user_input]
        else:
            print("Invalid input. Please enter one of the displayed options.")
