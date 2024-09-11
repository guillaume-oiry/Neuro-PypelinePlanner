# Packages

import mne

import _1_Preprocessing as _1_

import _B_Extract as _B_


# Constants

PREPROCESSING_CONDITIONS = {'RESPI' : lambda info : 'task-respi' in info['file_path']}

PREPROCESSING_PARAMETERS = {'MW_RESPI_minimal_preprocessing' : {}}

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

def extract_training_raws(raw_path_list, training_folder_path, prefix, sart_mode = False):
    
    for raw_path in raw_path_list :
        raw_dict = _1_.minimal_preprocessing(raw_path,
                                             parameters = PREPROCESSING_PARAMETERS,
                                             info = {'file_path' : raw_path})
        raw = raw_dict[prefix]['raw']['no_cleaning']['no_analysis']['data']
        if sart_mode == True :
            raw.plot(block=True)
            raw.set_annotations(mne.Annotations(onset=[], duration=[], description=[]))
        raw.plot(block=True)
        intervals = get_clean_intervals()
        training_raw = concatenate_clean_intervals(raw, intervals)
        training_raw.plot(block=True)
        training_raw.save(f'{training_folder_path}/{prefix}_training_raw.fif')

def extract_epochs_indices(raw_path_list):
    
    for raw_path in raw_path_list :
        raw = _1_.dict_minimal_preprocessing(raw_path,
                                             parameters = PREPROCESSING_PARAMETERS,
                                             conditions = PREPROCESSING_CONDITIONS)
        _B_.display_annotations(raw)
        print(raw)
        raw.plot(block=True)
