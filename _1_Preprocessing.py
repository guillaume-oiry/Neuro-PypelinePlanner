# Packages

import _A_Preprocessing as _A_


# Functions

def minimal_preprocessing(file_path, parameters, info):
    
    #extract_dict = {}
    
    for minimal_preprocessing_method, parameter in parameters.items():
        minimal_preprocessing_function = getattr(_A_, minimal_preprocessing_method)
        raw = minimal_preprocessing_function(file_path, parameter, info)
    
    return raw

def dict_minimal_preprocessing(file_path_list, parameters, conditions):
    
    by_sub_dict = {}
    
    for file_path in file_path_list:
        
        info = {'file_path' : file_path}
        conditions_check_dict = {key: func(info) for key, func in conditions.items()}
        for name, condition in conditions_check_dict.items() :
            if condition == True :
                
                raw = minimal_preprocessing(file_path, parameters=parameters[name], info=info)
                by_sub_dict.update(raw)
    
    return by_sub_dict

