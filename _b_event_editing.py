# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

import mne
import numpy as np
import pandas as pd

from datetime import date, datetime, timezone, timedelta


# SART

def modify_sart_event_ids(events, sampling_rate=250):
    events = events[:-1]
    processed_events = []
    i = 0
    while i < len(events):
        current_event = events[i]
        count = 1
        while (i + count < len(events)):
            time_diff = (events[i + count][0] - events[i + count - 1][0]) / sampling_rate
            if 0.08 <= time_diff <= 0.15:
                count += 1
            else:
                break
        if count > 5:
            count = 5
        current_event[2] = count
        processed_events.append(current_event)
        i += count
    return np.array(processed_events)

def sart_simplify_events(raw, behav_file_path):
    
    sf = raw.info['sfreq']
    events, event_id = mne.events_from_annotations(raw)
    processed_events = modify_sart_event_ids(events, sf)
    
    stim_events = mne.pick_events(processed_events, include=[1])
    probe_events = mne.pick_events(processed_events, include=[2])
    block_events = mne.pick_events(processed_events, include=[3])
    border_events = mne.pick_events(processed_events, include=[4])
    RS_events = mne.pick_events(processed_events, include=[5])
    
    behav = pd.read_csv(behav_file_path)
    digits = behav.digit.dropna().values
    
    #all_digits = behab.digit
    #press = behav.key_resp_testMF.rt
    if len(digits) < len(stim_events):
        stim_events = stim_events[len(stim_events) - len(digits):]
    go_nogo = [101 if i == 3 else 100 for i in digits]
    stim_events[:, 2] = go_nogo
    
    new_event_id = {100:'Go', 101:'NoGo'}

    raw.set_annotations(mne.Annotations([], [], []))
    new_annotations = mne.annotations_from_events(events=stim_events, sfreq=sf, event_desc=new_event_id)
    raw.set_annotations(new_annotations)

    return raw
    

# WORK - LAB_MEETING - CLASS

def standardize_paper(file_path,
                      file_name,
                      new_header = ['Mindstate', 'Confidence', 'Voluntary', 'Sleepiness', 'Time'],
                      check_columns = ['Mindstate', 'Confidence', 'Voluntary', 'Sleepiness'],
                      valid_values = {'Mindstate' : ['ON', 'TRT', 'TUT', 'MB', 'FGT'],
                                      'Confidence': [1,2,3,4,5],
                                      'Voluntary' : ['y', 'n', 'Y', 'N'],
                                      'Sleepiness' : [1,2,3,4,5]},
                      replacement_dicts = {'Mindstate': {'ON' : 1,
                                                         'TRT' : 2,
                                                         'TUT' : 3,
                                                         'MB' : 4,
                                                         'FGT' : 5},
                                           'Voluntary' : {'Y' : 1,
                                                          'N' : 2}}):
    
    # Check the file extension and read the file accordingly
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
        # Convert to CSV (optional: uncomment the next line to save the CSV file)
        # df.to_csv('output.csv', index=False)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please use .xlsx or .csv files.")
    
    # Change the header to the new specified header
    df.columns = new_header
    
    # Verify and replace values in specific columns
    for column in check_columns:
        if column in df.columns:
            df[column] = df[column].apply(lambda x: x if x in valid_values[column] else np.nan)
        else:
            raise ValueError(f"Column {column} not found in the file.")
    
    # Replace values according to specific dictionaries
    for column, replace_dict in replacement_dicts.items():
        if column in df.columns:
            df[column] = df[column].map(replace_dict).fillna(df[column])
    
    df = df.reset_index(drop=True)
    
    df.to_csv(file_name, index=False)
    
    return df
    
    # return df
    
    '''
    MAYBE REPLACE STRING MINDSTATES BY INT ?
    '''

def standardize_WORK_psychopy_csv(file_path,
                                  file_name,
                             mandatory_column = 'gong_sound.started',
                             columns_to_keep = ['key_resp_ms.keys',
                                                'key_resp_confidence.keys',
                                                'key_resp_voluntary.keys',
                                                'key_resp_sleepiness.keys',
                                                'gong_sound.started'],
                             new_header = ['Mindstate',
                                           'Confidence',
                                           'Voluntary',
                                           'Sleepiness',
                                           'Time'],
                             check_columns = ['Mindstate',
                                              'Confidence',
                                              'Voluntary',
                                              'Sleepiness'],
                             valid_values = {'Mindstate' : [1,2,3,4,5],
                                             'Confidence': [1,2,3,4,5],
                                             'Voluntary' : [1,2],
                                             'Sleepiness' : [1,2,3,4,5]},
                             replacement_dicts = {'Mindstate': {1 : 'ON',
                                                                2 : 'TRT',
                                                                3 : 'TUT',
                                                                4 : 'MB',
                                                                5 : 'FGT'},
                                                  'Voluntary' : {1 : 'Y',
                                                                 2 : 'N'}}):
    
    # Load the CSV file with the initial header applied
    df = pd.read_csv(file_path)

    # Delete every line that doesn't have a value in the mandatory column
    df.dropna(subset=[mandatory_column], inplace=True)

    # Keep only specific columns and reorder them
    df = df[columns_to_keep]

    # Rewrite the header
    df.columns = new_header

    # Verify values and replace with NaN where not matching the valid values or if blank
    for column in check_columns:
        df[column] = df[column].apply(lambda x: x if pd.notna(x) and x in valid_values[column] else np.nan)

    # # Replace values according to specific dictionaries
    # for column, replace_dict in replacement_dicts.items():
    #     if column in df.columns:
    #         df[column] = df[column].map(replace_dict).fillna(df[column])
    
    df = df.reset_index(drop=True)
    
    df.to_csv(file_name, index=False)
    
    # return df

    '''
    Floats values, may become a problem ?
    '''

def standardize_SART_psychopy_csv(file_path,
                                  file_name,
                             mandatory_column = 'Mindstate.started',
                             columns_to_keep = ['key_resp_ms.keys',
                                                'key_resp_confidence.keys',
                                                'key_resp_voluntary.keys',
                                                'key_resp_sleepiness.keys',
                                                'Mindstate.started'],
                             new_header = ['Mindstate',
                                           'Confidence',
                                           'Voluntary',
                                           'Sleepiness',
                                           'Time'],
                             check_columns = ['Mindstate',
                                              'Confidence',
                                              'Voluntary',
                                              'Sleepiness'],
                             valid_values = {'Mindstate' : [1,2,3,4,5],
                                             'Confidence': [1,2,3,4,5],
                                             'Voluntary' : [1,2],
                                             'Sleepiness' : [1,2,3,4,5]},
                             replacement_dicts = {'Mindstate': {1 : 'ON',
                                                                2 : 'TRT',
                                                                3 : 'TUT',
                                                                4 : 'MB',
                                                                5 : 'FGT'},
                                                  'Voluntary' : {1 : 'Y',
                                                                 2 : 'N'}}):
    
    # Load the CSV file with the initial header applied
    df = pd.read_csv(file_path)

    # Delete every line that doesn't have a value in the mandatory column
    df.dropna(subset=[mandatory_column], inplace=True)

    # Keep only specific columns and reorder them
    df = df[columns_to_keep]

    # Rewrite the header
    df.columns = new_header

    # Verify values and replace with NaN where not matching the valid values or if blank
    for column in check_columns:
        df[column] = df[column].apply(lambda x: x if pd.notna(x) and x in valid_values[column] else np.nan)

    # Replace values according to specific dictionaries
    # for column, replace_dict in replacement_dicts.items():
    #     if column in df.columns:
    #         df[column] = df[column].map(replace_dict).fillna(df[column])
            
    df = df.reset_index(drop=True)
    
    df.to_csv(file_name, index=False)
    
    # return df

    '''
    Floats values, may become a problem ?
    '''


# ANNOTATE EPOCHS

def remove_indices(original_list, indices_to_remove):
    # We create a new list that includes only those items whose index is not in indices_to_remove
    return [item for idx, item in enumerate(original_list) if idx not in indices_to_remove]

def no_triggers_paper_act_annotation(prefix, eeg_path, probe_path, std_path, session_row, tmin = -20):
    
    #### Format Raw
    raw = mne.io.read_raw(eeg_path, preload = True)
    raw_date = raw.info['meas_date']
    sf = raw.info['sfreq']
    raw_length = len(raw)/sf
    
    beginning_of_recording = raw_date - timedelta(seconds=raw_length)
    
    annot_timings = pd.read_csv(probe_path)
    first_datetime_str = np.unique(annot_timings.date.to_numpy())[0]
    
    first_datetime = datetime.strptime(
        first_datetime_str, "%Y-%m-%d_%Hh%M.%S.%f").replace(
            tzinfo=timezone.utc)
    
    # Delay between beginning of recording & psychopy
    delay_start_beeps = (first_datetime - beginning_of_recording).total_seconds()
    bip_starts_s = annot_timings['gong_sound.started'].dropna().to_numpy()
    bip_nodelay = bip_starts_s + delay_start_beeps
    
    # Gather MS report
    '''
    CHANGE TO NEW COLUMN
    '''
    
    # probe_df = annot_timings[['n_probe','key_resp_ms.keys']]
    # probe_df = probe_df.drop(index = probe_df[probe_df.n_probe.isna()].index)
    # probe_keys = probe_df['key_resp_ms.keys']
    
    # probe_keys.replace(np.nan, int(0), inplace = True)
    # probe_keys = probe_keys.astype(int)
    
    # ms_list = np.array([MS_DICT[report] for report in probe_keys.to_numpy()])
    # to_pop = np.where(ms_list == 'MISS')[0]
    
    # if any(to_pop) :
    #     bip_nodelay = np.delete(bip_nodelay, to_pop)
    #     ms_list = np.delete(ms_list, to_pop)
    
    # to_pop_2 = np.where(ms_list == 'MB')[0]
    # if any(to_pop_2) :
    #     bip_nodelay = np.delete(bip_nodelay, to_pop_2)
    #     ms_list = np.delete(ms_list, to_pop_2)
    
    # Add MS probe Annot to raw
    # raw.set_annotations(mne.Annotations(bip_nodelay, 0, ms_list))
    raw.set_annotations(mne.Annotations(bip_nodelay, 0, 1))
    '''NO ANNOTATIONS ?'''
    
    raw.save(eeg_path, overwrite = True)
    
    return epochs_path, mini_epochs_path

def no_triggers_laptop_act_annotation(prefix, eeg_path, probe_path, std_path, session_row, tmin = -20):
    
    #### Format Raw
    raw = mne.io.read_raw(eeg_path, preload = True)
    raw_date = raw.info['meas_date']
    sf = raw.info['sfreq']
    raw_length = len(raw)/sf
    
    beginning_of_recording = raw_date - timedelta(seconds=raw_length)
    
    annot_timings = pd.read_csv(probe_path)
    first_datetime_str = np.unique(annot_timings.date.to_numpy())[0]
    
    first_datetime = datetime.strptime(
        first_datetime_str, "%Y-%m-%d_%Hh%M.%S.%f").replace(
            tzinfo=timezone.utc)
    
    # Delay between beginning of recording & psychopy
    delay_start_beeps = (first_datetime - beginning_of_recording).total_seconds()
    bip_starts_s = annot_timings['gong_sound.started'].dropna().to_numpy()
    bip_nodelay = bip_starts_s + delay_start_beeps
    
    # Gather MS report
    '''
    CHANGE TO NEW COLUMN
    '''
    # probe_df = annot_timings[['n_probe','key_resp_ms.keys']]
    # probe_df = probe_df.drop(index = probe_df[probe_df.n_probe.isna()].index)
    # probe_keys = probe_df['key_resp_ms.keys']
    
    # probe_keys.replace(np.nan, int(0), inplace = True)
    # probe_keys = probe_keys.astype(int)
    
    # ms_list = np.array([MS_DICT[report] for report in probe_keys.to_numpy()])
    # to_pop = np.where(ms_list == 'MISS')[0]
    
    # if any(to_pop) :
    #     bip_nodelay = np.delete(bip_nodelay, to_pop)
    #     ms_list = np.delete(ms_list, to_pop)
    
    # to_pop_2 = np.where(ms_list == 'MB')[0]
    # if any(to_pop_2) :
    #     bip_nodelay = np.delete(bip_nodelay, to_pop_2)
    #     ms_list = np.delete(ms_list, to_pop_2)
    
    # Add MS probe Annot to raw
    # raw.set_annotations(mne.Annotations(bip_nodelay, 0, ms_list))
    raw.set_annotations(mne.Annotations(bip_nodelay, 0, 1))
    '''NO ANNOTATIONS ?'''
    
    raw.save(eeg_path, overwrite = True)

def with_triggers_act_annotation(prefix, eeg_path, probe_path, session_row, tmin = -20):
    
    raw = mne.io.read_raw(eeg_path, preload = True)
    events, event_id = mne.events_from_annotations(raw)
    
    # df = standardize_WORK_psychopy_csv(probe_path)
    df = pd.read_csv(probe_path)
    
    # df.to_csv('{prefix}.csv', index=False)
    # df = pd.read_csv('{prefix}.csv')
    
    if len(events) == len(df) :
        print('Good alignment.')
        # for i,event in enumerate(events):
            # events[i,2] = df['Mindstate'][i]
    
    elif len(events) > len(df) :
        print('Not the same number of probes.')
        print(f'EEG triggers : {len(events)}')
        print(f'Probes in csv : {len(df)}')
        
        # print(df['Time']/60-df['Time'][0]/60)
        
        print(df['Time'])
        
        print('Choose which triggers from eeg to ignore (indices from 0 to n-1).')
        while len(events) > len(df) :
            print(events[:,0]/250/60 - events[0,0]/250/60)
            count = len(events) - len(df)
            print(f'Still {count} triggers to ignore')
            print('Be careful choose indice of the new events set.')
            to_delete_row = input('Which row to delete ?')
            events = np.delete(events, int(to_delete_row), axis=0)
        
        # for i,event in enumerate(events):
        #     # events[i,2] = df['Mindstate'][i]
        
    else :
        print('Unlogic number of probes, verify manually.')
        print(f'EEG triggers : {len(events)}')
        print(f'Probes in csv : {len(df)}')
        
        # print(df['Time']/60-df['Time'][0]/60)
        
        print(df['Time'])
        
        input('Continue ?')
        while len(events) < len(df) :
            print(events[:,0]/250/60 - events[0,0]/250/60)
            count = len(df) - len(events)
            print(f'Still {count} triggers to ignore')
            to_delete_row = int(input('Which row to delete ?'))
            df = df.drop(to_delete_row)
    
    
    
    '''
    ADAPT EVENT_ID (with MS)
    '''
    
    # new_event_id = {MS_DICT[ev_id] : str(ev_id) for ev_id in np.unique(events[:, 2])}
    
    # mindstates_event_id = {0: 'MISS', 1: 'ON', 2: 'TRT', 3: 'TUT', 4: 'MB', 5: 'FGT'}
    
    # int_to_str_event_id = {v: k for k, v in mindstates_event_id.items()}

    # # Create a new event_id mapping that only includes keys present in the events from the raw file
    # real_event_id = {str(event_id) : int_to_str_event_id[event_id] for event_id in np.unique(events[:, 2]) if event_id in int_to_str_event_id}
    
    # description = np.array([MS_DICT[ms] for ms in events[:,2]])
    
    # new_annotations = mne.annotations_from_events(
    #     events=events, 
    #     sfreq=raw.info['sfreq'],
    #     orig_time=raw.info['meas_date']
    #     # event_desc = description
    # )
    
    # raw.set_annotations(new_annotations)
    
    # nei = {'1' : 'MISS', '2' : 'ON', '3' : 'TRT', '4' : 'TUT'}
    # raw.annotations.rename(new_event_id)
    
    # raw.save(eeg_path, overwrite = True)
    
    # events, event_id = mne.events_from_annotations(raw)


