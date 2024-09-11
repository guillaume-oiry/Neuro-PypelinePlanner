# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

# Packages

import numpy as np

import _1_Preprocessing as _1_
import _2_Extract as _2_
import _3_Clean as _3_
import _4_Analyze as _4_
import _5_Plot as _5_
import _6_Transversal as _6_
import _7_Save as _7_


main_path = '/home/guillaume/Documents/GitHub/EEG_Pipeline'

## 1_PREPROCESSING

PREPROCESSING_CONDITIONS = {'RESPI' : lambda info : 'task-RESPI' in info['file_path']}

PREPROCESSING_PARAMETERS = {'EPICE' : {'EPICE_minimal_preprocessing' : {'LOW_FREQ' : 0.1,
                                                                        'HIGH_FREQ' : 40,
                                                                        'NOTCH_FILTER' : 50}},
                            'RESPI' : {'MW_RESPI_minimal_preprocessing' : {}}}


## 2_EXTRACTING

labels_dict = {'Go':'Go',
               'NoGo':'NoGo'}

EXTRACTING_CONDITIONS = {'default': lambda info : True}

EXTRACTING_PARAMETERS = {'default':{'get_raw_crops': {'TIMINGS_DICT' : None},
                                    'simple_epoching':{'TMIN':-20,'TMAX':0, 'PTP_THRESHOLD':None, 'REJECT_FLAT':False},
                                    'subset_epoching': {'TMIN':-20,'TMAX':0, 'PTP_THRESHOLD':None, 'REJECT_FLAT':False, 'LABELS': {'First_10' : list(range(10)),
                                                                                                                                   'Go' : 'Go',
                                                                                                                                   'NoGo' : 'NoGo'}}}}


## 3_CLEANING

ASR_training_raw_dict = {}

CLEANING_CONDITIONS = {'raw' : lambda info : 'raw' in info['extract'],
                       'epochs' : lambda info : 'epochs' in info['extract']}

CLEANING_PARAMETERS = {'raw' : {'apply_ASR' : {'CUTOFF' : [20],
                                               'WL' : [0.5],
                                               'TRAINING_RAW_DICT' : ASR_training_raw_dict,
                                               'LABELS' : labels_dict}},
                        'epochs' : {'apply_ASR' : {'CUTOFF' : [20,30],
                                                   'WL' : [0.5,1],
                                                   'TRAINING_RAW_DICT' : None,
                                                   'LABELS' : labels_dict},
                                    'apply_AUTOREJECT' : {'N_INTERPOLATES' : [np.array([1, 2, 3])],
                                                          'CONSENSUS_PERCS' : [np.linspace(0.1, 0.7, 7)]},
                                    'apply_DSS' : {'DSS_N_COMPONENTS' : [6],
                                                   'DSS_THRESHOLD' : [1e-2]},
                                    'ptp_threshold_to_epochs' : {'REJECT_PTP_THRESHOLD_LIST' : [250e-6, 350e-6, 450e-6],
                                                                 'FLAT_PTP_THRESHOLD_LIST' : [1e-6]},
                                    'apply_ASR_and_ptp_threshold_to_epochs' : {'apply_ASR' : {'CUTOFF' : [20],
                                                                                              'WL' : [0.5],
                                                                                              'TRAINING_RAW_DICT' : None,
                                                                                              'LABELS' : labels_dict},
                                                                               'ptp_threshold_to_epochs' : {'REJECT_PTP_THRESHOLD_LIST' : [250e-6, 350e-6, 450e-6],
                                                                                                            'FLAT_PTP_THRESHOLD_LIST' : [1e-6]}}}}


## 4_ANALYZE

ANALYZE_CONDITIONS = {'raw' : lambda info : 'raw' in info['extract'],
                      'epochs' : lambda info : 'epochs' in info['extract']}

ANALYZE_PARAMETERS = {'raw' : {'PSD_data' : {'BP' : True}},
                      'epochs' : {'PSD_data' : {'BP' : True},
                                  'ERP_data' : {}}}


## 5_PLOT

PLOT_CONDITIONS = {'raw' : lambda info : 'raw' in info['extract'],
                   'PSD' : lambda info : 'PSD' in info['analysis'],
                   'ERP' : lambda info : 'ERP' in info['analysis'],
                   'epochs' : lambda info : 'epochs' in info['extract']}

PLOT_PARAMETERS = {'raw' : {'spectrogram' : {'CH_PICK' : ['Pz']}},
                   'PSD' : {'PSD_plot' : {}},
                   'ERP' : {'ERP_plot' : {}},
                   'epochs' : {'epochs_single_channel' : {'CH_NAME':'Pz'}}}


## 6_TRANSVERSAL

TRANSVERSAL_PARAMETERS = {'PSD_plot_ch_comparison' : {'CH_NAME':['Pz'],
                                                      'CONDITION' : lambda info : 'epochs' in info['extract']},
                          'plot_evoked_comparison' : {'CH_NAME':['Pz'],
                                                      'CONDITION' : lambda info : 'epochs' in info['extract']},
                          'plot_evoked_Go_NoGo' : {'CH_PICK':['Pz'],
                                                   'CONDITION' : lambda info : True}}


# Functions

def main(file_path_list):
    
    main_dict = {}
    
    # HIERARCHICAL PROCESSING
    main_dict = _1_.dict_minimal_preprocessing(file_path_list, parameters = PREPROCESSING_PARAMETERS, conditions = PREPROCESSING_CONDITIONS)
    main_dict = _2_.dict_extracting(main_dict, parameters = EXTRACTING_PARAMETERS, conditions = EXTRACTING_CONDITIONS)
    main_dict = _3_.dict_cleaning(main_dict, parameters = CLEANING_PARAMETERS, conditions = CLEANING_CONDITIONS)
    main_dict = _4_.dict_analysis(main_dict, parameters = ANALYZE_PARAMETERS, conditions = ANALYZE_CONDITIONS)
    main_dict = _5_.dict_plotting(main_dict, parameters = PLOT_PARAMETERS, conditions = PLOT_CONDITIONS)
    
    # TRANSVERSAL PROCESSING
    processing_dict = _6_.transversal_processing(main_dict, parameters = TRANSVERSAL_PARAMETERS)
    
    # SAVE
    _7_.save_figs_to_report(main_dict, save_path = main_path, name = 'main')
    _7_.save_figs_to_report(processing_dict, save_path = main_path, name = 'processing')

    return main_dict

