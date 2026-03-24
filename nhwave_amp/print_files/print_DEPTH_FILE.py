import numpy as np
import nhwave_amp as nha


"""
Code to print out the DEPTH_FILE for FUNWAVE-TVD
"""

def print_DEPTH_FILE(vars):
    print('\t\tStarted printing bathymetry file (DEPTH_FILE)...')

    # Unpack variables
    bathy_array = vars['DOM']['h'].values.T
    ITER = int(vars['ITER'])

    # Get path for bathymetry file- this is DEPTH_FILE
    ptr = nha.get_key_dirs(tri_num = ITER)
    bathy_path = ptr['BATHY_IN']

    # Print
    np.savetxt(bathy_path, bathy_array, delimiter=' ', fmt='%f')
    
    print(f'\t\tDEPTH_FILE file successfully saved to: {bathy_path}')
    return {'DEPTH_FILE': bathy_path}