# Packages

import _A_Preprocessing as _A_
import _B_Extract as _B_


# Functions

def extracting(data, parameters, info):
    
    extract_dict = {}
    
    for extracting_method, parameter in parameters.items():
        extracting_function = getattr(_B_, extracting_method)
        extract = extracting_function(data, parameter, info)
        extract_dict.update(extract)
    
    return extract_dict

def dict_extracting(main_dict, parameters, conditions):
    
    for rec in main_dict.keys():
        
        info = {'rec' : rec}
        info.update(_A_.extract_info_from_rec_name(rec))
        conditions_check_dict = {key: func(info) for key, func in conditions.items()}
        
        for name, condition in conditions_check_dict.items() :
            if condition == True :
                
                raw = main_dict[rec]['raw']['no_cleaning']['no_analysis']['data']
                extracting_dict = extracting(raw, parameters=parameters[name], info=info)
                main_dict[rec].update(extracting_dict)
    
    return main_dict

