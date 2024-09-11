# Packages

import _F_Transversal as _F_


# Functions

def transversal_processing(by_sub_dict, parameters):
    
    processing_dict = {}
    
    for processing_method, parameter in parameters.items():
        processing_function = getattr(_F_, processing_method)
        processing = processing_function(by_sub_dict, parameter)
        processing_dict.update(processing)
    
    return processing_dict
    
