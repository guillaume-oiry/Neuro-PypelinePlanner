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
    else:
        preprocessing_dict = preprocessing(file_path_list, parameters)
        processing_dict = processing(preprocessing_dict, parameters)
    return processing_dict

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

def get_functions_with_args(info, parameters, step, step_module):

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

    functions = []
    for function_name, kwargs in option.items():
        function = getattr(step_module, function_name)
        functions.append((function, kwargs))

    return functions

'''
def postprocessing(processing_dict, parameters, apply_multiprocessing = True):

    print("starting postprocessing")

    postprocessing_dict = {}
    postprocessing_parameters = parameters['postprocessing']

    if apply_multiprocessing:
        q = multiprocessing.Queue()
        mp_list = []
        def mp_postprocess(q, postprocessing_function, parameters, kwargs, function):
            data = postprocessing_function(copy.deepcopy(processing_dict), parameters, **kwargs) # returned data should be a dict with {label : data, [...]}
            q.put((function, data))

    for function, kwargs in postprocessing_parameters.items():

        postprocessing_function = getattr(modules.postprocessing_functions, function)
        #data = postprocessing_function(copy.deepcopy(processing_dict), parameters, **kwargs) # returned data should be a dict with {label : data, [...]}

        if apply_multiprocessing:
            process = multiprocessing.Process(target=mp_postprocess, args=(q, postprocessing_function, parameters, kwargs, function))
            process.start()
            mp_list.append(process)
        else:
            data = postprocessing_function(copy.deepcopy(processing_dict), parameters, **kwargs) # returned data should be a dict with {label : data, [...]}
            postprocessing_dict[function] = data

    if apply_multiprocessing:

        for _ in mp_list:
            function, data = q.get()
            postprocessing_dict[function] = data

        for p in mp_list:
            p.join()
            p.close()

    return postprocessing_dict


    # DRAFT OF ANOTHER APPROACH TO POSTPROCESSING


    def postprocessing_scheme(processing_dict, scheme_dict, scheme_steps, scheme_parameters, processing_steps = processing_steps):

        if len(scheme_steps) == 0:
            return scheme_dict

        step = scheme_steps[0]
        step_parameters = scheme_parameters[step]
        for function, kwargs in step_parameters.items():
            step_function = getattr(step, function)
            datas = step_function(processing_dict, scheme_dict, **kwargs) # returned data should be a dict with {label : data, [...]}
            for label, data in datas.items():
                scheme_dict[step][label].update(data)

        return postprocessing_scheme(processing_dict, scheme_dict, scheme_steps[1:], scheme_parameters, processing_steps)

    for scheme_name, scheme_parameters in schemes.items():
        scheme_steps = scheme_parameters.keys()
        postprocessing_dict[scheme_name] = postprocessing_scheme(processing_dict = processing_dict.copy(),
                                                                    scheme_dict = {},
                                                                    scheme_steps = scheme_steps.copy(),
                                                                    scheme_parameters = scheme_parameters.copy(),
                                                                    processing_steps = processing_steps)

    return postprocessing_dict

def report():
    pass

def save():
    pass

'''

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

def compare_timings():

    stats = []

    for mp in [True, False]:
        start_global = time.perf_counter()

        start_preprocessing = time.perf_counter()
        processing_dict = preprocessing(mp = mp)
        end_preprocessing = time.perf_counter()
        duration_preprocessing = end_preprocessing - start_preprocessing

        start_processing = time.perf_counter()
        processing_dict = processing(main_dict = processing_dict, steps = list(PARAMETERS['processing'].keys()), nstep = 0, info = {}, mp = mp)
        print(processing_dict)
        end_processing = time.perf_counter()
        duration_processing = end_processing - start_processing

        start_postprocessing = time.perf_counter()
        postprocessing_dict = postprocessing(processing_dict = processing_dict, parameters = PARAMETERS, mp = mp)
        end_postprocessing = time.perf_counter()
        duration_postprocessing = end_postprocessing - start_postprocessing

        end_global = time.perf_counter()
        duration_global = end_global - start_global

        stat = f"MP {mp} : {duration_global}\n - preprocessing : {duration_preprocessing}\n - processing : {duration_processing}\n - postprocessing : {duration_postprocessing}\n"
        stats.append(stat)

    for s in stats:
        print(s)



if __name__ == "__main__":
    #multiprocessing.set_start_method('spawn')
    file_path_list = glob.glob(data_query)
    processing_dict = main(file_path_list, parameters = PARAMETERS, apply_multiprocessing = False)
    processing_dict_mp = main(file_path_list, parameters = PARAMETERS, apply_multiprocessing = True)
    print(processing_dict)
    print(processing_dict_mp)


