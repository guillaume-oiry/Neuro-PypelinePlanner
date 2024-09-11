# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

import mne

import os
import glob
import json

import _B_Extract as _B_


def define_raw_crops(folder_path):
    
    timings_dict = {}
    
    for path in glob.glob(f'{folder_path}/sub-justine*.fif'):
        
        raw = mne.io.read_raw(path, preload=True)
        file_name = os.path.basename(raw.filenames[0])
        sub = os.path.splitext(file_name)[0]
        raw.plot(block=True)
        
        # Raw crops timings
        print('Raw crops timings')
        timings_dict[sub] = get_timings_dict(raw)
        
    with open(f'{folder_path}/timings_dict.json', 'w') as f:
        json.dump(timings_dict, f)
    
    return timings_dict

def get_timings_dict(data):
    
    print('Write down start, end and name of segments')

    _B_.display_annotations(data)

    #data.plot(block=True)
    
    start_list = []
    end_list = []
    name_list = []

    while True:
        start = input("Enter the start time or indice of the interval (or 'q' to quit): ")
        if start.lower() == 'q':
            print('q')
            break
        start_list.append(start)
        end_list.append(input("Enter the end time or indice of the interval : "))
        name_list.append(input("Enter the name of the interval : "))
    
    print('end of loop')
    
    timings_dict = {name : [] for name in name_list}
    for i, name in enumerate(timings_dict):
        timings_dict[name].append(parse_string_to_number(start_list[i]))
        timings_dict[name].append(parse_string_to_number(end_list[i]))
    
    return timings_dict

def parse_string_to_number(input_string):
    try:
        # Attempt to convert the string to an int
        return int(input_string)
    except ValueError:
        # If int conversion fails, attempt to convert to float
        try:
            return float(input_string)
        except ValueError:
            # If both conversions fail, return an error message
            return 'Error: Cannot convert to int or float'


