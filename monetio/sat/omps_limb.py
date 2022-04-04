def read_omps_limb(file):
    '''Method to read OMPS limb profiler Ozone level 2 hdf5 files from NASA repository
        (https://ozoneaq.gsfc.nasa.gov/data/omps/#)
    Parameters
    __________
    filename : string
        filename is the path to the file
    
    Returns
    _______
    xarray dataset
    
    '''
    
    import pandas as pd
    import numpy as np
    import xarray as xr
    import h5py
    
    f = h5py.File(file,'r')
    date = f['GeolocationFields']['Date'][()]
    temperature = f['AncillaryData']['Temperature'][:]
    pressure = f['AncillaryData']['Pressure'][:]
    lat = f['GeolocationFields']['Latitude'][:]
    lon = f['GeolocationFields']['Longitude'][:]
    alt = f['DataFields']['Altitude'][:]
    o3_vis = f['DataFields']['O3VisValue'][:]*1.38e-19*temperature/pressure/(10**(-6))

    o3_error = f['DataFields']['O3VisPrecision'][:]*1.38e-19*temperature/pressure/(10**(-6))
    obstime = pd.to_timedelta(f['GeolocationFields']['Time'][:],unit='s') #pd.to_timedelta(obstime,unit='s')
    o3_uv = f['DataFields']['O3UvValue'][:]*1.38e-19*temperature/pressure/(10**(-6))
    o3_uv_error = f['DataFields']['O3UvPrecision'][:]*1.38e-19*temperature/pressure/(10**(-6))
    # flags
    pmc_flag = f['DataFields']['ASI_PMCFlag'][:]
    cloud_height = f['DataFields']['CloudHeight'][:]
    vis_qual = f['DataFields']['O3VisQuality'][:]
    uv_qual = f['DataFields']['O3UvQuality'][:]
    qfg = f['GeolocationFields']['SwathLevelQualityFlags'][:]
    f.close()

    times = pd.to_datetime(date,format='%Y%m%d')+obstime
    p_ind = np.where(pmc_flag == 1)
    visqind = np.where(vis_qual != 1)
    uvqind = np.where(uv_qual != 1)
    o3_vis[p_ind] = -999.
    o3_uv[p_ind] = -999.
    o3_vis[visqind] = -999.
    o3_uv[uvqind] = -999.
    #print(alt)
    for i in range(len(lat)):
        if str(qfg[i])[2] != '0':
            o3_uv[i] = -999.
            o3_vis[i] = -999.
        a = (np.where(alt == cloud_height[i]))[0]
        #print(cloud_height[i])
        #print(a)
        if a.size != 0 and cloud_height[i] !=1:
            o3_vis[i][:a[0]+1] = -999.
            o3_uv[i][:a[0]+1] = -999.
    ds = xr.Dataset(
            {
            'O3_UV': (['x','z'],o3_uv),
            'O3_vis': (['x','z'],o3_vis),
            'precision_uv': (['x','z'],o3_uv_error),
            'precision_vis': (['x','z'],o3_error),
            },
            coords={
                'longitude':(['x'],lon),
                'latitude':(['x'],lat),
                'obs_time':(['x'],times),
                'altitude':(['z'],alt),
            },
            attrs={'missing_value':-999}
        )         
    return ds
