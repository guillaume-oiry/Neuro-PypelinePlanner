            processing(main_dict[key], steps, nstep = nstep+1, info = info)

    def postprocessing(main_dict, processing_steps = parameters['processing'].keys(), schemes = parameters['postprocessing']):
