# Packages

import mne

import _1_Preprocessing as _1_

import _B_Extract as _B_


# Constants

PREPROCESSING_CONDITIONS = {'default' : lambda info : True}

bad_channels = {'sub-arthur_ses-240305_task-work_eeg': [],
 'sub-ines_ses-240424_task-sart_eeg': [],
 'sub-nico_ses-240412_task-sart_eeg': [],
 'sub-marie_ses-240524_task-sart_eeg': [],
 'sub-ines_ses-240308_task-work_eeg': [],
 'sub-nico_ses-240528_task-lm_eeg': [],
 'sub-ruben_ses-240514_task-sart_eeg': [],
 'sub-ilona_ses-240423_task-lm_eeg': ['Fz', 'Cz'],
 'sub-pierre_ses-240305_task-work_eeg': [],
 'sub-guillaume_ses-240328_task-work_eeg': [],
 'sub-imane_ses-240521_task-lm_eeg': ['Fz', 'Cz'],
 'sub-lea_ses-240506_task-class_eeg': ['Fp1',
  'Fp2',
  'Fz',
  'Cz',
  'Pz',
  'O1',
  'O2'],
 'sub-yannis_ses-240529_task-sart_eeg': [],
 'sub-yannis_ses-240423_task-lm_eeg': ['Fz', 'Pz'],
 'sub-alessia_ses-240329_task-work_eeg': ['Cz', 'Pz'],
 'sub-justine_ses-240331_task-work_eeg': ['Fp1', 'Fp2', 'O1', 'O2'],
 'sub-arthur_ses-240331_task-work_eeg': [],
 'sub-adrianna_ses-240321_task-work_eeg': ['Fp1', 'Fp2'],
 'sub-pierre_ses-240315_task-work_eeg': [],
 'sub-jade_ses-2403182_task-work_eeg': ['O1', 'O2'],
 'sub-bastien_ses-240426_task-class_eeg': [],
 'sub-nico_ses-2403202_task-work_eeg': [],
 'sub-tomasz_ses-240516_task-work_eeg': [],
 'sub-justine_ses-240401_task-work_eeg': ['Fp1', 'Fp2', 'O1', 'O2'],
 'sub-elsa_ses-240426_task-class_eeg': [],
 'sub-ilona_ses-240423_task-sart_eeg': [],
 'sub-pierre_ses-240415_task-sart_eeg': ['Cz'],
 'sub-tomasz_ses-240521_task-lm_eeg': ['Cz', 'Pz'],
 'sub-jade_ses-2403181_task-work_eeg': ['O1', 'O2'],
 'sub-thomas_ses-240517_task-sart_eeg': ['Cz'],
 'sub-arthur_ses-240419_task-sart_eeg': [],
 'sub-bastien_ses-240517_task-class_eeg': [],
 'sub-jade_ses-240411_task-sart_eeg': [],
 'sub-lea_ses-240429_task-class_eeg': ['Fp1',
  'Fp2',
  'Fz',
  'Cz',
  'Pz',
  'O1',
  'O2'],
 'sub-guillaume_ses-240307_task-work_eeg': [],
 'sub-clara_ses-240429_task-class_eeg': ['Cz']}

PREPROCESSING_PARAMETERS = {'default' : {'EPICE_minimal_preprocessing' : {'LOW_FREQ' : 0.1,
                                                                          'HIGH_FREQ' : 40,
                                                                          'NOTCH_FILTER' : 50,
                                                                         'BAD_CHANNELS' : bad_channels}}}

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
