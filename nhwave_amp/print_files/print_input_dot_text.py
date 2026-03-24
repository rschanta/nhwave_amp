import copy
import numpy as np
import nhwave_amp as nha
'''
This file prints the required input.txt file needed to start any NHWAVE 
simulation. All this really does is loop through a dictionary and print
everything line by line in the format PARAMETER = VALUE. 

'''
def print_input_dot_text(var_dict,strict=False):
    print('\nPRINTING input.txt...')
    print('\tStarted printing input file...')

    # Obtain all key paths for this folder
    ptr = nha.get_key_dirs(tri_num=var_dict['ITER'])
    # Obtain the input.txt file path for this folder
    in_path = ptr['INPUTS']
    
    # Copy the dictionary
    var_dict_copy = copy.deepcopy(var_dict)
    # Ensure all required parameters are actually present
    var_dict_validated = nha.validate_nhwave_params(var_dict_copy,strict=strict)
    
    # Loop to write
    with open(in_path, 'w') as f:
        for var_name, value in var_dict_validated.items():
            # Allow only strings and numeric scalars
            if isinstance(value, (str, int, float, np.integer, np.floating)):
                # Skip NaN values (for floats/NumPy floats only)
                if isinstance(value, (float, np.floating)) and np.isnan(value):
                    continue
                # Otherwise write the variable
                f.write(f"{var_name} = {value}\n")
    
    print(f"\tinput.txt file successfully saved to: {ptr['INPUTS']}", flush=True)
    return