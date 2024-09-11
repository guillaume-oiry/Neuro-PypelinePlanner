# Packages

import numpy as np

import matplotlib.pyplot as plt


# Modules

def PSD_plot_ch_comparison(by_sub_dict, parameters):

    processing = {'PSD_plot_ch_comparison' : {}}
    
    #Scrap parameters
    ch_pick_list = parameters['CH_PICK']
    
    for sub, extracts in by_sub_dict.items():
        processing['PSD_plot_ch_comparison'][sub] = {}
        
        for extract, methods in extracts.items():
            info = {'sub' : sub, 'extract' : extract}
            condition = parameters['CONDITION']
            
            n_total = by_sub_dict[sub][extract]['no_cleaning']['no_analysis']['data'].get_data().shape[0]
            
            condition_check = condition(info)
            if condition_check == True :
                
                processing['PSD_plot_ch_comparison'][sub][extract] = {}
                
                for ch_pick in ch_pick_list :
                    ch_list = ['Fp1','Fp2','Fz','Cz','Pz','O1','O2']
                    index = ch_list.index(ch_pick)
                    freqs = np.linspace(0.5, 40, 80)
                    
                    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12), layout = "constrained")
                    
                    data_dict = {}
                    for method in methods.keys():
                        
                        #if ('cutoff-5' in method) or ('cutoff-20' in method) or ('cutoff-80' in method) or ('no_cleaning' in method) :
                        
                        try:
                            data_dict[method] = by_sub_dict[sub][extract][method]['PSD']['data']
                        except:
                            pass
                    
                    for method, data in data_dict.items():
                        
                        data = np.log10(data)

                        ndim = data.ndim
                        
                        n_epochs = data.shape[0]
                                                
                        if ndim == 3:
                            data_std = np.std(data, axis=0)
                            data = np.mean(data, axis=0)
                        
                        ax.plot(freqs, np.array(data[index]).T, label = f'{method} (n = {np.rint((n_epochs / n_total)*100)} %)', alpha = .8)
                        if ndim == 3 :
                            ax.fill_between(freqs, data[index] - data_std[index], data[index] + data_std[index], alpha = .1)

                    # Set the title and labels
                    ax.set_title(f'{info['extract'].replace('epochs_', '')}_PSD-{ch_pick}', fontsize=50)
                    ax.set_xlabel('Frequency (Hz)', fontsize=30)
                    ax.set_ylabel('(dB)', fontsize=30) # this is dB
                    ax.set_xlim([0.5, 40])
                    
                    # ax.set_ylim([-30, 60])
                    ax.legend()
                    
                    # Show the plot
                    #plt.legend(prop={'size':20})
                    
                    processing['PSD_plot_ch_comparison'][sub][extract][f'PSD_{ch_pick}_comparison'] = fig
                    
                    plt.close()

    return processing

def plot_evoked_comparison(by_sub_dict, parameters):
    
    processing = {'plot_evoked_comparison':{}}
    
    #Scrap parameters
    ch_pick_list = parameters['CH_PICK']
    
    for sub, extracts in by_sub_dict.items():
        processing['plot_evoked_comparison'][sub] = {}
        for extract, methods in extracts.items():
            info = {'sub' : sub, 'extract' : extract}
            condition = parameters['CONDITION']
            
            n_total = by_sub_dict[sub][extract]['no_cleaning']['no_analysis']['data'].get_data().shape[0]
            
            condition_check = condition(info)
            if condition_check == True :
                
                processing['plot_evoked_comparison'][sub][extract] = {}
                
                for ch_pick in ch_pick_list :
            
                    data_dict = {}
                    n_epochs_dict = {}
                    
                    for method in methods.keys():
                        
                        #if ('cutoff-5' in method) or ('cutoff-20' in method) or ('cutoff-80' in method) or ('no_cleaning' in method) :
                        
                        try:
                            data_dict[method] = by_sub_dict[sub][extract][method]['ERP']['data']
                            n_epochs_dict[method] = by_sub_dict[sub][extract][method]['no_analysis']['data'].get_data().shape[0]
                            
                        except:
                            pass

                    fig, ax1 = plt.subplots(1, 1, figsize=(14, 6))
                    
                    ch = ['Fp1','Fp2','Fz','Cz','Pz','O1','O2']
                    index = ch.index(ch_pick)
                    
                    for method, evoked_data in data_dict.items():
                        data = evoked_data.get_data()
                        ch_data = data[index] * 1e6
                        n_epochs = n_epochs_dict[method]
                        ax1.plot(evoked_data.times, ch_data, label=f'{method} (n = {np.rint((n_epochs / n_total)*100)} %)')
                    
                    ax1.set_xlabel('Time (s)')
                    ax1.set_ylabel('Amplitude (µV)')
                    ax1.set_title(f'{info['extract'].replace('epochs_', '')} Responses at {ch_pick}')
                    ax1.legend()
                    ax1.get_yaxis().get_major_formatter().set_useOffset(False)
                    ax1.get_yaxis().get_major_formatter().set_scientific(False)
                    plt.tight_layout()
                    
                    processing['plot_evoked_comparison'][sub][extract][f'ERP_{ch_pick}_comparison'] = fig
                    
                    plt.close()
    
    return processing

def plot_evoked_Go_NoGo(by_sub_dict, parameters):
    
    processing = {'plot_evoked_Go_NoGo':{}}
    
    #Scrap parameters
    ch_pick_list = parameters['CH_PICK']
    
    for sub in by_sub_dict.keys():
        
        processing['plot_evoked_Go_NoGo'][sub] = {}
        
        n_total_go = by_sub_dict[sub]['epochs_Go']['no_cleaning']['no_analysis']['data'].get_data().shape[0]
        n_total_nogo = by_sub_dict[sub]['epochs_NoGo']['no_cleaning']['no_analysis']['data'].get_data().shape[0]
        
        for method in by_sub_dict[sub]['epochs_Go'].keys():
            
            processing['plot_evoked_Go_NoGo'][sub][method] = {}
            
            info = {'sub' : sub}
            condition = parameters['CONDITION']
            condition_check = condition(info)
            if condition_check == True :
                
                #try:
                erp_go = by_sub_dict[sub]['epochs_Go'][method]['ERP']['data']
                n_epochs_go = by_sub_dict[sub]['epochs_Go'][method]['no_analysis']['data'].get_data().shape[0]
                
                erp_nogo = by_sub_dict[sub]['epochs_NoGo'][method]['ERP']['data']
                n_epochs_nogo = by_sub_dict[sub]['epochs_NoGo'][method]['no_analysis']['data'].get_data().shape[0]
                
                for ch_pick in ch_pick_list :
                    
                    fig, ax1 = plt.subplots(1, 1, figsize=(14, 6))
                    
                    ch = ['Fp1','Fp2','Fz','Cz','Pz','O1','O2']
                    index = ch.index(ch_pick)
                    
                    data_go = erp_go.get_data()
                    data_ch_go = data_go[index] * 1e6
                    ax1.plot(erp_go.times, data_ch_go, label=f'Go : {method} (n = {np.rint((n_epochs_go / n_total_go)*100)} %)')

                    data_nogo = erp_nogo.get_data()
                    data_ch_nogo = data_nogo[index] * 1e6
                    ax1.plot(erp_nogo.times, data_ch_nogo, label=f'NoGo : {method} (n = {np.rint((n_epochs_nogo / n_total_nogo)*100)} %)')
                
                    ax1.set_xlabel('Time (s)')
                    ax1.set_ylabel('Amplitude (µV)')
                    ax1.set_title(f'Go / NoGo Responses at {ch_pick}')
                    ax1.legend()
                    ax1.get_yaxis().get_major_formatter().set_useOffset(False)
                    ax1.get_yaxis().get_major_formatter().set_scientific(False)
                    plt.tight_layout()
                    
                    processing['plot_evoked_Go_NoGo'][sub][method][f'ERP_Go_NoGo_{ch_pick}'] = fig
                    
                    plt.close()
            
                #except:
                #        pass

    return processing


