# Packages

import _A_Preprocessing
import _B_Extract
import _C_Clean 
import _D_Analyze
import _E_Plot

import copy


PARAMETERS = {'preprocessing' : {'sart' : {'CONDITION' : lambda file_path : 'task-sart' in file_path,
                                           'PARAMETERS' : {'EPICE_minimal_preprocessing' : {'LOW_FREQ' : 0.1,
                                                                                            'HIGH_FREQ' : 40,
                                                                                            'NOTCH_FILTER' : 50}}},
                                 'other' : {'CONDITION' : lambda file_path : True,
                                            'PARAMETERS' : {'EPICE_minimal_preprocessing' : {'LOW_FREQ' : 0.1,
                                                                                            'HIGH_FREQ' : 40,
                                                                                            'NOTCH_FILTER' : 50}}}},
              'processing' : {'extraction' : {},
                              'cleaning' : {},
                              'analysis' : {},
                              'plot' : {}},
              'postprocessing' : {'scheme1' : {'compressions' : {'func1' : {}},
                                               'statistics' : {'func1' : {},
                                                               'func2' : {}},
                                               'figures' : {'func1' : {},
                                                            'func2' : {},
                                                            'func3' : {}
                                                            }
                                               }
                                  }
              }

'''
postprocessing_dict = {'scheme1' : {'floor1-a' : {'data' : data,
                                                  'statistics' : {'func1' : {},
                                                                  'func2' : {}},
                                                  'figures' : {'func1' : {},
                                                               'func2' : {},
                                                               'func3' : {}}},
                                    'floor1-b' : {'data' : data,
                                                  'statistics' : statistics,
                                                  'figures' : figures}}}
'''

def pipeline(file_path_list, parameters):

    def nest_data(steps, data):
        if len(steps) == 1:
            return {f"no_{steps[0]}" : data}
        return {f"no_{steps[0]}" : nest_data(steps[1:], data)}

    def unnest_data(d):
        if len(d.keys()) > 1:
            raise Exception("There shouldn't me more than one key at this step.")
        value = d[*d.keys()]
        if isinstance(value, dict):
            return unnest_data(value)
        return value
    
    def preprocessing():
        main_dict = {}
        preprocessing_options = parameters['preprocessing'].values()
        for file_path in file_path_list:
            option = [opt['PARAMETERS'] for opt in preprocessing_options if opt['CONDITIONS'](file_path)][0]
            function = option[*option.keys()]
            parameters = option[function]
            preprocessing_function = getattr(_A_Preprocessing, function)
            raw = preprocessing_function(file_path, parameters=parameters, info=file_path)
            main_dict[file_path] = nest_data(parameters['processing'].keys(), raw)
        return main_dict

    def processing(main_dict, steps = parameters['processing'].keys(), info = {}):

        if len(steps) == 0:
            return main_dict

        step = steps[0]
        processing_step_options = parameters['processing'][step].values()
        for key in main_dict.keys():
            info.update({step : key})
            option = [opt['PARAMETERS'] for opt in processing_step_options if opt['CONDITIONS'](info)][0]
            for function, kwargs in option['PARAMETERS'].items():
                step_function = getattr(step, function)
                datas = step_function(unnest_data(main_dict[key]), info, **kwargs) # returned data should be a dict with {label : data, [...]}
                for label, data in datas.items():
                    main_dict[key][label].update(nest_data(steps = steps[1:], data = data))
        return processing(main_dict[key], steps[1:], info = info)

    def postprocessing(main_dict, processing_steps = parameters['processing'].keys(), schemes = parameters['postprocessing']):

        def postprocessing_scheme(main_dict, scheme_dict, scheme_steps, scheme_parameters, processing_steps = processing_steps):

            if len(scheme_steps) == 0:
                return scheme_dict
            
            step = scheme_steps[0]
            step_parameters = scheme_parameters[step]
            for function, kwargs in step_parameters.items():
                step_function = getattr(step, function)
                datas = step_function(main_dict, scheme_dict, **kwargs) # returned data should be a dict with {label : data, [...]}
                for label, data in datas.items():
                    scheme_dict[step][label].update(data)

            return postprocessing_scheme(main_dict, scheme_dict, scheme_steps[1:], scheme_parameters, processing_steps)

        postprocessing_dict = {}

        for scheme_name, scheme_parameters in schemes.values():
            scheme_steps = scheme_parameters.keys()
            postprocessing_dict[scheme_name] = postprocessing_scheme(main_dict = main_dict.copy(),
                                                                     scheme_dict = {},
                                                                     scheme_steps = scheme_steps.copy(),
                                                                     scheme_parameters = scheme_parameters.copy(),
                                                                     processing_steps = processing_steps)

        return postprocessing_dict

    return preprocessing, processing, postprocessing


