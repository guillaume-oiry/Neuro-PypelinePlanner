# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

# Packages

import os
import sys
import mne

import _b_event_editing as _b_


# Modules

def EPICE_minimal_preprocessing(file_path, parameters, info):
    
    # Scrap parameters
    low_freq = parameters['LOW_FREQ']
    high_freq = parameters['HIGH_FREQ']
    notch_filter = parameters['NOTCH_FILTER']
    
    raw = mne.io.read_raw(file_path, preload=True)
    
    sub = extract_sub(raw)
    
    raw = mapping(raw)
    raw = rereferencing(raw)
    raw = min_filtering(raw, l_freq = low_freq, h_freq = high_freq, notch_f = notch_filter)
    
    if 'task-sart' in sub:
        eeg_index = file_path.find('_eeg.')
        behav_path = file_path[:eeg_index]
        behav_path += '_behav.csv'
        raw = _b_.sart_simplify_events(raw, behav_file_path=behav_path)
    
    if 'task-class' in sub:
        eeg_index = file_path.find('_eeg.')
        behav_path = file_path[:eeg_index]
        behav_path += '_behav.csv'
        raw = _b_.sart_simplify_events(raw, behav_file_path=behav_path)
    
    if 'task-work' in sub:
        eeg_index = file_path.find('_eeg.')
        behav_path = file_path[:eeg_index]
        behav_path += '_behav.csv'
        raw = _b_.sart_simplify_events(raw, behav_file_path=behav_path)
    
    if 'task-lm' in sub:
        eeg_index = file_path.find('_eeg.')
        behav_path = file_path[:eeg_index]
        behav_path += '_behav.csv'
        raw = _b_.sart_simplify_events(raw, behav_file_path=behav_path)
    
    raw_dict = {sub : {'raw' : {'no_cleaning' : {'no_analysis' : {'data': raw}}}}}
    
    return raw_dict

def MW_RESPI_minimal_preprocessing(file_path, parameters, info):
    
    config_dict = {
      "file_format": "FIF",
      "load_and_preprocess": {
        "referencing" : "average",
        "montage": "standard_1020",
        "l_freq": 0.1,
        "h_freq": 40,
        "notch_freq": [50,100],
        "f_resample" : 250,
        "channel_types" : {
            'VEOG' : 'eog', 'HEOG' : 'eog', 'ECG' : 'ecg', 'RESP' : 'resp'
            },
        "n_jobs" : -1
      },
      "channel_interpolation": {
        "method": "automatic"
      },
      "ica": {
        "n_components": 15,
        "l_freq": 1.0,
      }
    }

    eeg_channels = ['Fp1', 'Fz', 'F3', 'F7', 'FT9', 'FC5', 'FC1', 'C3', 'T7', 'TP9',
        'CP5', 'CP1', 'Pz', 'P3', 'P7', 'O1', 'Oz', 'O2', 'P4', 'P8',
        'TP10', 'CP6', 'CP2', 'Cz', 'C4', 'T8', 'FT10', 'FC6', 'FC2', 'F4',
        'F8', 'Fp2', 'AF7', 'AF3', 'AFz', 'F1', 'F5', 'FT7', 'FC3', 'C1',
        'C5', 'TP7', 'CP3', 'P1', 'P5', 'PO7', 'PO3', 'POz', 'PO4', 'PO8',
        'P6', 'P2', 'CPz', 'CP4', 'TP8', 'C6', 'C2', 'FC4', 'FT8', 'F6',
        'AF8', 'AF4', 'F2', 'Iz']

    incomplete_subjects = ["HS_001", "HS_004"]
    
    # Load configuration
    
    file_format = config_dict['file_format']
    settings = config_dict['load_and_preprocess']
    supported_formats = ['BrainVision', 'EDF', 'FIF']
    channel_types = settings["channel_types"]
    
    # Ensure the file format is supported
    assert file_format in supported_formats, f"File format {file_format} not supported."

    # Load the raw data based on the file format
    if file_format == "BrainVision":
        raw = mne.io.read_raw_brainvision(file_path, preload=True)
    elif file_format == "EDF":
        raw = mne.io.read_raw_edf(file_path, preload=True)
    elif file_format == "FIF":
        raw = mne.io.read_raw_fif(file_path, preload=True)
    
    # Apply preprocessing steps
    raw.set_channel_types(channel_types)
    mne.set_eeg_reference(raw, ['TP9', 'TP10'], copy = False)
    raw.set_montage(
        mne.channels.make_standard_montage(settings['montage']), 
        on_missing='ignore'
        )
    
    to_drop = ['F3','F7','FT9','FC5','FC1','C3','T7','TP9','CP5','CP1','P3','P7','Oz',
               'P4','P8','TP10','CP6','CP2','C4','T8','FT10','FC6','FC2','F4','F8',
               'AF7','AF3','AFz','F1','F5','FT7','FC3','C1','C5','TP7','CP3','P1','P5',
               'PO7','PO3','POz','PO4','PO8','P6','P2','CPz','CP4','TP8','C6','C2','FC4',
               'FT8','F6','AF8','AF4','F2','Iz','VEOG','HEOG','ECG','RESP']
    raw.drop_channels(to_drop)
    
    raw.filter(
        settings['l_freq'], 
        settings['h_freq'], 
        fir_design='firwin',
        picks = ["eeg", "eog"],
        n_jobs = settings["n_jobs"]
        )
    raw.notch_filter(
        settings['notch_freq'], 
        filter_length='auto', 
        phase='zero', 
        n_jobs = settings["n_jobs"]
        )
    raw.resample(settings['f_resample'])
    
    sub = extract_sub(raw)
    raw_dict = {sub : {'raw' : {'no_cleaning' : {'no_analysis' : {'data': raw}}}}}
    
    return raw_dict


## Side functions

def extract_sub(raw):
    file_name = os.path.basename(raw.filenames[0])
    sub = os.path.splitext(file_name)[0]
    return sub

def extract_info(raw):
    file_name = os.path.basename(raw.filenames[0])
    dot_split = os.path.splitext(file_name)
    parts = dot_split[0].split('_')

    if len(parts) == 4:
        # Create the dictionary with the required elements
        file_info = {
            'sub': parts[0].split('-')[1],
            'ses': parts[1].split('-')[1],
            'task': parts[2].split('-')[1],
            'suffix': parts[3],
            'extension' : dot_split[1]
        }
        print(file_info)
    else:
        print("Unexpected filename format. Please check the input.")
        sys.exit()
    
    return file_info

def mapping(raw, new_ch_names = ['Fp1','Fp2','Fz','Cz','Pz','O1','O2','M2']):

    if 'TimeStamp' in raw.info['ch_names'] :
        raw.drop_channels(['TimeStamp'])

    old_ch_names = raw.info['ch_names']

    if len(old_ch_names) == 8:
        mapping = dict(zip(old_ch_names, new_ch_names))
    
    raw.rename_channels(mapping)
    raw.set_montage('standard_1020')
    return raw

def rereferencing(raw):
    raw._data[:6, :] = raw._data[:6,:] - raw._data[7, :]/2
    raw.drop_channels('M2')
    return raw

def min_filtering(raw, l_freq = 0.1, h_freq = 40, notch_f = 50):
    raw.filter(l_freq, h_freq)
    raw.notch_filter(notch_f)
    return raw

