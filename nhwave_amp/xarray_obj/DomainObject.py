import numpy as np
import xarray as xr


'''
The DomainObject is the primary object storing everything to do with the 
computational grid in x-y-sigma, and all variables that live on such a grid. 
This includes:
    - DEPTH_FILE information
    - STATION_FILE information
    
It is based on the xarray object. Use of the DomainObject is REQUIRED to 
correctly set up the bathymetry, even if a DEPTH_FILE is not used. This is 
because the generation of the xarray for the outputs directly pull on the
DomainObject.
'''


class DomainObject(xr.Dataset):
    __slots__ = ()

    ## INITIALIZE =============================================================
    def __init__(self, DX=None,
                       DY=None,
                       Mglob=None,
                       Nglob=None,
                       Kglob=None):

        # Construct X and Y coordinates from input parameters
        x = DX * np.arange(0, Mglob)
        y = DY * np.arange(0, Nglob)

        # Construct sigma coordinate centers
        sig_c = (np.arange(Kglob) + 0.5) / Kglob
        # Construct sigma coordinate interfaces
        sig_f = np.linspace(0.0, 1.0, Kglob+1) 
        
        # Initialize the xarray Dataset with coordinates
        super().__init__(coords={
                                 'x': x, 
                                 'y': y,
                                 'sig_c': sig_c,
                                 'sig_f': sig_f
                                 }
                         )
        
        # Store important spatial parameters as attributes
        self.attrs['Mglob'] = Mglob
        self.attrs['Nglob'] = Nglob
        self.attrs['Kglob'] = Kglob
        self.attrs['DX'] = DX
        self.attrs['DY'] = DY
    ## [END] INITIALIZE =======================================================




    ## ADD BATHYMETRY =========================================================    

    
    # DEPTH_TYPE = FLAT 
    def z_from_FLAT(self,
                DEPTH_FLAT = None):
        '''
        Construct the bathymetry from the DEPTH_TYPE = FLAT Case. Note that this
        will automatically tile the 1D array constructed in the cross-shore to 
        whatever Nglob is set as.
        '''

        # Attributes
        Mglob = self.attrs['Mglob']
        Nglob = self.attrs['Nglob']
        # Create array
        z = [DEPTH_FLAT] * Mglob
        
        bathy_array = np.tile(z, (Nglob, 1)).T

        self['h'] = (('x', 'y'), bathy_array)  
        return
    
    
    # DEPTH_TYPE = DATA (1D) 
    def z_from_1D_array(self, bathy_array_1D):
        '''
        Construct the bathymetry from the DEPTH_TYPE = DATA Case. The input
        is a 1D array, that will be tiled along Nglob.
        '''

        # First, check that it is indeed 1D and Mglob-dimensional
        if np.reshape(bathy_array_1D, -1).shape[0] == self.attrs['Mglob']:
            # Tile the array along Y
            bathy_array = np.tile(bathy_array_1D, (self.attrs['Nglob'], 1)).T
            
            # Add to object as a data variable
            self['h'] = (('x', 'y'), bathy_array)  
            
        else:
            raise ValueError(f"Array dimensions {bathy_array_1D.shape} do not match expected "
                             f"dimension: ({self.attrs['Mglob']})")
        return
    
    # DEPTH_TYPE = DATA (2D) 
    def z_from_2D_array(self, bathy_array_2D):
        '''
        Construct the bathymetry from the DEPTH_TYPE = DATA Case. The input
        is a 2D array.
        '''

        self['h'] = (('x', 'y'), bathy_array_2D)  
            
        return
    ## [END] ADD BATHYMETRY ===================================================




    ## ADD STATIONS ===========================================================
    '''
    TODO
    '''
    def add_stations(self,
                     Mglob_pos=None,
                     Nglob_pos=None):
        """Add stations to a domain"""
        # Add GAGE_NUM as a new dimension
        self.coords['GAGE_NUM'] =  np.arange(len(Mglob_pos)) + 1

        # Add Mglob_pos and Nglob_pos as variables along GAGE_NUM
        self['Mglob_gage'] = (('GAGE_NUM'), Mglob_pos)
        self['Nglob_gage'] = (('GAGE_NUM'), Nglob_pos)
    ## [END] ADD STATIONS =====================================================
    
    
    


