# Packages

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
    
    for sub in main_dict.keys():
        
        info = {'sub' : sub}
        conditions_check_dict = {key: func(info) for key, func in conditions.items()}
        
        for name, condition in conditions_check_dict.items() :
            if condition == True :
                
                raw = main_dict[sub]['raw']['no_cleaning']['no_analysis']['data']
                extracting_dict = extracting(raw, parameters=parameters[name], info=info)
                main_dict[sub].update(extracting_dict)
    
    return main_dict

