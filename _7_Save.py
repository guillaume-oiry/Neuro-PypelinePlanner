# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

import mne
import datetime


def save_if_fig(item, report, tags = ['fig']):
    caption = ''
    for tag in tags :
        caption += f'{tag}/'
    try :
        report.add_figure(fig = item,
                          title = caption,
                          caption = caption,
                          image_format="PNG",
                          tags=tags)
    except :
        pass
    
    return report

def save_figs_to_report(main_dict, save_path, name = 'Report'):
    report = mne.Report(title=f"{name}")
    
    for sub_id, extracts in main_dict.items():
        report = save_if_fig(extracts, report, tags = [sub_id])
        for extract, methods in extracts.items():
            report = save_if_fig(methods, report, tags = [sub_id, extract])
            try :
                for method, analysis_list in methods.items():
                    report = save_if_fig(analysis_list, report, tags = [sub_id, extract, method])
                    try : 
                        for analysis, plots in analysis_list.items():
                            report = save_if_fig(plots, report, tags = [sub_id, extract, method, analysis])
                            try :
                                for plot, item in plots.items():
                                    report = save_if_fig(item, report, tags = [sub_id, extract, method, analysis])
                            except :
                                pass
                    except :
                        pass
            except :
                pass

    time = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    report.save(f"{save_path}/{name}_{time}.html", overwrite=True)

