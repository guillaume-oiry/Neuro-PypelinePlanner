import modules
from parameters import data_query, PARAMETERS
import glob
import warnings
import copy
import multiprocessing
import time

def main(file_path_list, parameters, apply_multiprocessing = True):
    if apply_multiprocessing:
        preprocessing_dict = preprocessing_mp(file_path_list, parameters)
        processing_dict = processing_mp(preprocessing_dict, parameters)
        postprocessing_dict = postprocessing_mp(copy.deepcopy(processing_dict), parameters)
    else:
        preprocessing_dict = preprocessing(file_path_list, parameters)
        processing_dict = processing(preprocessing_dict, parameters)
        postprocessing_dict = postprocessing_mp(copy.deepcopy(processing_dict), parameters)
    return postprocessing_dict

def preprocessing(file_path_list, parameters):

    preprocessing_dict = {}

    for file_path in file_path_list:
        functions = get_functions_with_args(file_path,
                                              parameters = parameters['preprocessing'],
                                              step = 'preprocessing',
                                              step_module = modules.preprocess)
        function, kwargs = functions[0] # In the preprocessing step there is only one function by file.
        data = function(file_path, parameters = kwargs, info=file_path)
        preprocessing_dict[file_path] = nest_data(list(parameters['processing'].keys()), data) # Put the data at the bottom of the processing tree.

    return preprocessing_dict

def preprocessing_mp(file_path_list, parameters):

    preprocessing_dict = {}

    q = multiprocessing.Queue()
    mp_list = []

    for file_path in file_path_list:
        functions = get_functions_with_args(file_path,
                                        parameters = parameters['preprocessing'],
                                        step = 'preprocessing',
                                        step_module = modules.preprocess)
        function, kwargs = functions[0] # In the preprocessing step there is only one function by file.

        process = multiprocessing.Process(target=preprocess_mp, args=(q, file_path, function, kwargs))
        process.start()
        mp_list.append(process)

    for _ in mp_list:
        file_path, data = q.get()
        preprocessing_dict[file_path] = nest_data(list(parameters["processing"].keys()), data) # Put the data at the bottom of the processing tree.

    for p in mp_list:
        p.join()
        #p.close()

    return preprocessing_dict

def preprocess_mp(q, file_path, function, kwargs):
    data = function(file_path = file_path, parameters = kwargs, info = file_path)
    q.put((file_path, data))

def processing(preprocessing_dict, parameters):

    processing_dict = {}

    for file_path, empty_tree in preprocessing_dict.items():
        individual_dict = rec_processing(individual_dict = {file_path : empty_tree},
                                         parameters = parameters,
                                         steps = list(parameters['processing'].keys())
                                         )
        for path, data_tree in individual_dict.items(): # Logically, there is only one set of key-value : the file_path and the corresponding processing tree.
            processing_dict[path] = data_tree

    return processing_dict

def processing_mp(preprocessing_dict, parameters):

    processing_dict = {}

    q = multiprocessing.Queue()
    mp_list = []

    for file_path, empty_tree in preprocessing_dict.items():
        process = multiprocessing.Process(target=process_mp, args=(q, file_path, empty_tree, parameters))
        process.start()
        mp_list.append(process)

    for _ in mp_list:
        individual_dict = q.get()
        for path, data_tree in individual_dict.items(): # Logically, there is only one set of key-value : the file_path and the corresponding processing tree.
            processing_dict[path] = data_tree

    for p in mp_list:
        p.join()
        #p.close()

    return processing_dict

def process_mp(q, file_path, empty_tree, parameters):
    individual_dict = rec_processing(individual_dict = {file_path : empty_tree},
                                     parameters = parameters,
                                     steps = list(parameters['processing'].keys())
                                     )
    q.put(individual_dict)

def rec_processing(individual_dict, parameters, steps, nstep = 0, info = {}):

    if len(steps) == 0:
        return individual_dict

    if nstep >= len(steps):
        return individual_dict

    sub_step = steps[nstep]

    for key in individual_dict.keys():

        if nstep == 0:
            info['file_name'] = key
        else:
            info[steps[nstep-1]] = key

        functions = get_functions_with_args(info = info,
                                            parameters = parameters['processing'][sub_step],
                                            step = 'processing',
                                            step_module = getattr(modules, sub_step))

        for f in functions:
            function, kwargs = f
            datas = function(data = unnest_data(individual_dict[key]), info = info, **kwargs) # unnest to get the preprocessed data at the bottom of the tree
            for label, data in datas.items(): # returned data should be a dict with {label : data, [...]}
                individual_dict[key].update({label : nest_data(steps = steps[nstep+1:], data = data)})

        rec_processing(individual_dict[key], parameters, steps, nstep = nstep+1, info = info)

    return individual_dict

def postprocessing(processing_dict, parameters):

    postprocessing_dict = {}
    postprocessing_parameters = parameters['postprocessing']
    
    functions = get_functions_with_args(info = None,
                                parameters = parameters['postprocessing'],
                                step = 'postprocessing',
                                step_module = modules.postprocessing_functions)

    for f in functions:
        function, kwargs = f
        data = function(copy.deepcopy(processing_dict), parameters, **kwargs)
        postprocessing_dict[function.__name__] = data

    return postprocessing_dict

def postprocessing_mp(processing_dict, parameters):

    postprocessing_dict = {}

    functions = get_functions_with_args(info = None,
                                parameters = parameters['postprocessing'],
                                step = 'postprocessing',
                                step_module = modules.postprocessing_functions)

    q = multiprocessing.Queue()
    mp_list = []

    for f in functions:
        function, kwargs = f
        process = multiprocessing.Process(target=postprocess_mp, args=(q, function, processing_dict, parameters, kwargs))
        process.start()
        mp_list.append(process)

    for _ in mp_list:
        function, data = q.get()
        postprocessing_dict[function.__name__] = data

    for p in mp_list:
        p.join()
        #p.close()

    return postprocessing_dict

def postprocess_mp(q, function, processing_dict, parameters, kwargs):
    data = function(copy.deepcopy(processing_dict), parameters, **kwargs)
    q.put((function, data))

def get_functions_with_args(info, parameters, step, step_module):

    functions = []

    if step == 'postprocessing':
        for function_name, kwargs in parameters.items():
            function = getattr(step_module, function_name)
            functions.append((function, kwargs))
        return functions

    options = [opt['PARAMETERS'] for opt in parameters.values() if opt['CONDITION'](info)]
    if len(options) == 0 : # We don't permit to ignore any file of the query on the preprocessing step, but it's not a problem for the processing step.
        if step == 'preprocessing':
            raise Exception(f"No conditions matching for {info}.")
        elif step == 'processing': 
            warnings.warn(f"No conditions matching for {info}.")
            return []
    elif len(options) > 1 :
        raise Exception(f"Conditions should be mutually exclusive. {len(option)} conditions matched for {info}.")
    else :
        option = options[0]

    for function_name, kwargs in option.items():
        function = getattr(step_module, function_name)
        functions.append((function, kwargs))

    return functions

def nest_data(steps, data):
    if len(steps) == 0:
        return data
    if len(steps) == 1:
        return {f"no_{steps[0]}" : data}
    return {f"no_{steps[0]}" : nest_data(steps[1:], data)}

def unnest_data(d):
    print(list(d.keys()))
    if len(d.keys()) > 1:
        raise Exception("There shouldn't be more than one key at this step.")
    value = d[list(d.keys())[0]]
    if isinstance(value, dict):
        return unnest_data(value)
    return value

if __name__ == "__main__":
    #multiprocessing.set_start_method('spawn')
    file_path_list = glob.glob(data_query)
    processing_dict = main(file_path_list, parameters = PARAMETERS, apply_multiprocessing = False)
    processing_dict_mp = main(file_path_list, parameters = PARAMETERS, apply_multiprocessing = True)
    print(processing_dict)
    print(processing_dict_mp)

