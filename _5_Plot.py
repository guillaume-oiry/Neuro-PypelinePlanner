# Packages

import _E_Plot as _E_

import copy


# Functions

def plot(data, parameters, info):
    
    plot_dict = {}
    
    for plot_method, parameter in parameters.items():
        plot_function = getattr(_E_, plot_method)
        plot = plot_function(copy.deepcopy(data), parameter, info)
        plot_dict.update(plot)
    
    return plot_dict

def dict_plotting(main_dict, parameters, conditions):

    for sub in main_dict.keys():
        for extract in main_dict[sub].keys():
            for method in main_dict[sub][extract].keys():
                for analysis in main_dict[sub][extract][method].keys():
                    
                    info = {'sub' : sub, 'extract' : extract, 'method' : method, 'analysis' : analysis}
                    conditions_check_dict = {key: func(info) for key, func in conditions.items()}
                    
                    for name, condition in conditions_check_dict.items() :
                        if condition == True :
                            data = main_dict[sub][extract][method][analysis]['data']
                            main_dict[sub][extract][method][analysis].update(plot(data, parameters=parameters[name], info=info))
                        
    return main_dict

