# Packages

import _A_Preprocessing as _A_
import _D_Analyze as _D_

import copy


# Functions

def analysis(data, parameters, info):
    
    analysis_dict = {}
    
    for analysis_method, parameter in parameters.items():
        analysis_function = getattr(_D_, analysis_method)
        analysis = analysis_function(copy.deepcopy(data), parameter, info)
        analysis_dict.update(analysis)
    
    return analysis_dict

def dict_analysis(main_dict, parameters, conditions):
    
    for rec in main_dict.keys():
        for extract in main_dict[rec].keys():
            for method in main_dict[rec][extract].keys():
                
                info = {'rec' : rec, 'extract' : extract, 'method' : method}
                info.update(_A_.extract_info_from_rec_name(rec))
                conditions_check_dict = {key: func(info) for key, func in conditions.items()}
                
                for name, condition in conditions_check_dict.items() :
                    if condition == True :
                        
                        data = main_dict[rec][extract][method]['no_analysis']['data']
                        analysis_dict = analysis(data, parameters=parameters[name], info=info)
                        main_dict[rec][extract][method].update(analysis_dict)
                        
                        
                        # Validate updated data
                        for analysis_key, analysis_data in analysis_dict.items():
                            analysis_data_hash = hash(str(analysis_data))
                            print(f'Analysis data hash for {rec}-{extract}-{method}-{analysis_key}: {analysis_data_hash}')
                            
                            # Double-check that the data in main_dict is updated correctly
                            updated_data_hash = hash(str(main_dict[rec][extract][method][analysis_key]))
                            print(f'Updated main_dict analysis data hash for {rec}-{extract}-{method}-{analysis_key}: {updated_data_hash}')
                            assert analysis_data_hash == updated_data_hash, "Data not updated correctly in main_dict"

    return main_dict

