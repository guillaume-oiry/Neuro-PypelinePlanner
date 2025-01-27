# Packages

import mne

import _1_Preprocessing as _1_

import _B_Extract as _B_


# Constants

PREPROCESSING_CONDITIONS = {'default' : lambda info : True}

PREPROCESSING_PARAMETERS = {'default' : {'EPICE_minimal_preprocessing' : {'LOW_FREQ' : 0.1,
                                                                          'HIGH_FREQ' : 40,
                                                                          'NOTCH_FILTER' : 50,
                                                                         'BAD_CHANNELS' : {}}}

# Functions

def get_clean_intervals():
    intervals = []
    while True:
        start = input("Enter the start time of the clean interval (in seconds, or 'q' to quit): ")
        if start.lower() == 'q':
            break
        end = input("Enter the end time of the clean interval (in seconds): ")
        intervals.append((float(start), float(end)))
    return intervals

def concatenate_clean_intervals(raw, intervals):
    clean_data = []
    for start, end in intervals:
        start_sample = int(start * raw.info['sfreq'])
        end_sample = int(end * raw.info['sfreq'])
        clean_data.append(raw[:, start_sample:end_sample][0])
    concatenated_data = mne.concatenate_raws([mne.io.RawArray(data, raw.info) for data in clean_data])
    return concatenated_data

def extract_training_raws(sample_dict, training_folder_path):
    
    for path, name in sample_dict.items() :
        raw_dict = _1_.minimal_preprocessing(path,
                                             parameters = PREPROCESSING_PARAMETERS['default'],
                                             info = {'file_path' : path})
        raw = raw_dict[name]['raw']['no_cleaning']['no_analysis']['data']
        if 'task-sart' in name :
            raw.plot(block=True)
            raw.set_annotations(mne.Annotations(onset=[], duration=[], description=[]))
        raw.plot(scalings = dict(eeg=100e-6), duration = 60, block=True)
        intervals = get_clean_intervals()
        training_raw = concatenate_clean_intervals(raw, intervals)
        training_raw.plot(scalings = dict(eeg=100e-6), block=True)
        training_raw.save(f'{training_folder_path}/{name}_training_raw.fif')

def extract_epochs_indices(raw_path_list):
    
    for raw_path in raw_path_list :
        raw = _1_.dict_minimal_preprocessing(raw_path,
                                             parameters = PREPROCESSING_PARAMETERS,
                                             conditions = PREPROCESSING_CONDITIONS)
        _B_.display_annotations(raw)
        print(raw)
        raw.plot(block=True)
