# Packages

import _C_Clean as _C_

import copy


# Function

def cleaning(data, parameters, info, original_data):
    
    clean_dict = {}
    
    for cleaning_method, parameter in parameters.items():
        cleaning_function = getattr(_C_, cleaning_method)
        clean = cleaning_function(data = copy.deepcopy(data),
                                  parameters = parameter,
                                  info = info,
                                  original_data=copy.deepcopy(original_data))
        clean_dict.update(clean)
    
    return clean_dict

def dict_cleaning(main_dict, parameters, conditions):
    
    for sub in main_dict.keys():
        for extract in main_dict[sub].keys():
            
            info = {'sub' : sub, 'extract' : extract}
            conditions_check_dict = {key: func(info) for key, func in conditions.items()}
            
            for name, condition in conditions_check_dict.items() :
                if condition == True :

                    target_data = main_dict[sub][extract]['no_cleaning']['no_analysis']['data']
                    original_data = main_dict[sub]['raw']['no_cleaning']['no_analysis']['data']
                    
                    cleaning_dict = cleaning(data=target_data, parameters=parameters[name], info=info, original_data=original_data)
                    main_dict[sub][extract].update(cleaning_dict)

                    # Validate updated data
                    for key, cleaned_data_dict in cleaning_dict.items():
                        cleaned_data = cleaned_data_dict['no_analysis']['data'].get_data()
                        cleaned_data_hash = hash(cleaned_data.tostring())
                        print(f'Cleaned data hash for {sub}-{extract}-{key}: {cleaned_data_hash}')
                        
                        # Double-check that the data in main_dict is updated correctly
                        updated_data_hash = hash(main_dict[sub][extract][key]['no_analysis']['data'].get_data().tostring())
                        print(f'Updated main_dict cleaned data hash for {sub}-{extract}-{key}: {updated_data_hash}')
                        assert cleaned_data_hash == updated_data_hash, "Data not updated correctly in main_dict"

    return main_dict

