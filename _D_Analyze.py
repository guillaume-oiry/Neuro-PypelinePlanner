# Packages

import numpy as np
import pandas as pd

import copy


# Modules

def PSD_data(data, parameters, info):
    
    analysis = {}
    
    #Scrap parameters
    bp = parameters['BP'] = True
        
    data_copy = copy.deepcopy(data)
    
    print(f'data : {data_copy}')
    
    try :
        psd = data_copy.compute_psd(
            method = 'welch',
            fmin = 0.5, 
            fmax = 40,
            n_fft = 500,
            n_overlap = 250,
            n_per_seg = 500,
            window = 'hamming',
            )
        
        psd_data = psd.get_data()

        analysis[f'PSD'] = {'data': psd_data}
        if bp :
            analysis[f'BP'] = {'data': BP_data(psd_data)}
    
    except :
        pass
    
    return analysis

def ERP_data(data, parameters, info):
    
    analysis = {}
    
    try : 
        data_copy = copy.deepcopy(data)
        
        evoked = data_copy.average()
        
        analysis[f'ERP'] = {'data': evoked}
    
    except :
        pass
    
    return analysis


## Side functions

def BP_data(psd_data, freq_bands = {'Delta': (.5, 4), 'Theta': (4, 8), 'Alpha': (8, 12), 'Beta': (12, 30), 'Gamma': (30, 40)}):
    
    data = psd_data.copy() # NECESSARY ?

    ndim = data.ndim
    if ndim == 3:
        data_std = np.std(data, axis=0)
        data = np.mean(data, axis=0)
    
    # Define frequency bands
    freqs = np.linspace(0.5, 40, 80)
    
    abs_bandpower_ch = {
         f"abs_{band}": np.nanmean(data[:,
                 np.logical_and(freqs >= borders[0], freqs <= borders[1])
                 ], axis = 1)
         for band, borders in freq_bands.items()}
    
    abs_bandpower = [np.nanmean(data[:,
                 np.logical_and(freqs >= borders[0], freqs <= borders[1])
                 ], axis = (0,1))
         for band, borders in freq_bands.items()]
    
    total_power = np.sum(abs_bandpower)
    
    rel_bandpower_ch = {
        f"rel_{band}" : abs_bandpower_ch[f"abs_{band}"] / total_power
        for band in freq_bands.keys()
        }
    
    bandpower_ch = abs_bandpower_ch | rel_bandpower_ch
    
    df_bp = pd.DataFrame(bandpower_ch)

    df_bp.index = ['Fp1','Fp2','Fz','Cz','Pz','O1','O2']

    df_bp.loc['Frontal'] = np.nanmean(df_bp.loc[['Fp1','Fp2','Fz']].values, axis=0)
    df_bp.loc['Central'] = np.nanmean(df_bp.loc[['Cz','Pz']].values, axis=0)
    df_bp.loc['Occipital'] = np.nanmean(df_bp.loc[['O1','O2']].values, axis=0)
    df_bp.loc['All'] = np.nanmean(df_bp.loc[['Fp1','Fp2','Fz','Cz','Pz','O1','O2']].values, axis=0)
    
    #df_bp.to_csv(f'{bandpower_path}/{prefix}_BP_matrix.csv')

    return df_bp

