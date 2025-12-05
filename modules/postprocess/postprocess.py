import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne
from . import cpp_postprocess

import pycatch22
import os
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
from sklearn.decomposition import PCA


# PSD MEAN


def psd_mean(processing_dict, parameters, plot_freqs_interval=[0, 40]):

    view_parameters = {
        "extraction": {
            "raw": lambda info: "no_extraction" in info["extraction"],
            "epochs": lambda info: "epochs" in info["extraction"],
        },
        "analysis": ["psd_data"],
        "file_path": lambda info: ".edf" in info["file_path"],
    }
    view_dict = view(processing_dict, parameters, view_parameters)

    postprocessing_data = {}
    for label, data in view_dict.items():
        psd_list = data["psd_data"]
        ch_picks = psd_list[1].info[
            "ch_names"
        ]  # All the recordings don't have the same number of channels and this one has the minimal set.
        psd_mean_data = compute_psd_mean(psd_list, ch_picks)
        psd_mean_plot = psd_plot(
            psd=psd_mean_data, freqs_interval=plot_freqs_interval, title=f"PSD {label}"
        )
        postprocessing_data[label] = {"data": psd_mean_data, "plot": psd_mean_plot}

    return postprocessing_data


def compute_psd_mean(psd_list, ch_picks):

    array_list = []
    freqs = psd_list[0].freqs
    for psd in psd_list:
        data = psd.pick(ch_picks)._data
        if (
            data.ndim == 3
        ):  # If psd data from epochs process an individual mean first so that each subject is one data point.
            data = np.mean(data, axis=0)
        array_list.append(data)

    psd_stack = np.stack(array_list, axis=2)
    psd_mean_data = np.mean(psd_stack, axis=2)
    psd_mean_data = pd.DataFrame(
        psd_mean_data, index=ch_picks, columns=psd_list[0].freqs
    )

    return psd_mean_data


def psd_plot(psd, freqs_interval=[0, 40], title=""):

    if isinstance(psd, mne.time_frequency.Spectrum):
        psd = pd.DataFrame(psd._data, index=psd.info["ch_names"], columns=psd.freqs)
    elif isinstance(psd, pd.DataFrame):
        pass
    else:
        raise Exception(
            f"Can't plot the psd. The psd must be formatted into a mne Spectrum object or a pandas DataFrame with channel names as index and frequencies as columns."
        )

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 12), layout="constrained")

    freqs = psd.columns
    for ch, row in psd.iterrows():
        ax.plot(row.index, np.log10(row.values), label=ch, alpha=0.8)

    ax.set_title(title, fontsize=50)
    ax.set_xlabel("Frequency (Hz)", fontsize=30)
    ax.set_ylabel("(dB)", fontsize=30)
    ax.set_xlim(freqs_interval)
    ax.legend()

    plt.close()
    return fig


# CATCH-22


def C22_epochs_3D_PCA(processing_dict, parameters, n_components=2, mp=True):

    # Adjust the view
    view_parameters = {
        "extraction": {"epochs": lambda info: "epochs" in info["extraction"]}
    }
    view_epochs = view(
        processing_dict=processing_dict,
        parameters=parameters,
        view_parameters=view_parameters,
    )

    # Gather all C22 features of every channel of every epoch
    ch_names = view_epochs["epochs"][1].info[
        "ch_names"
    ]  # The second epochs set have the minimal set of channels
    if mp:
        df = epochs_C22_df_mt(epochs_list=view_epochs["epochs"], ch_names=ch_names)
    else:
        df = epochs_C22_df(epochs_list=view_epochs["epochs"], ch_names=ch_names)

    # PCA compute
    pca_data = PCA(n_components=n_components).fit_transform(all_df_mt.T)

    # PCA figure
    if n_components in [2, 3]:
        fig = epochs_C22_PCA_plot(pca_data=pca_data, n_components=n_components)
        return {"features_df": df, "PCA_data" : pca_data, "PCA_fig": fig}
    else:
        return {"features_df": df, "PCA_data" : pca_data}



def epochs_C22_df(epochs_list, ch_names):
    data_dict = {}
    for i, epochs in enumerate(epochs_list):
        for n, epoch in enumerate(epochs):
            results = {}
            for ch_name in ch_names:
                signal = copy.deepcopy(epoch[epochs.info["ch_names"].index(ch_name)])
                result = pycatch22.catch22_all(signal)
                for f, feature_name in enumerate(result["names"]):
                    results[f"{ch_name}-{feature_name}"] = result["values"][f]
            data_dict[f"{i}-{n}"] = pd.Series(results)
    df = pd.DataFrame(data_dict)
    return df


def epochs_C22_df_mt(epochs_list, ch_names):

    data_dict = {}

    for i, epochs in enumerate(epochs_list):

        ch_idx = {}
        for ch_name in ch_names:
            ch_idx[ch_name] = epochs.info["ch_names"].index(ch_name)

        threads_to_use = os.cpu_count()
        results_list = Parallel(n_jobs=threads_to_use)(
            delayed(compute_C22_features)(epoch_data, ch_idx, i, n)
            for n, epoch_data in enumerate(epochs)
        )

        for r in results_list:
            data_dict.update(r)

    df = pd.DataFrame(data_dict)
    return df


def compute_C22_features(epoch_data, ch_idx, i, n):

    results = {}
    for ch, ch_name in enumerate(ch_names):
        signal = epoch_data[ch_idx[ch_name]]
        result = pycatch22.catch22_all(signal)
        for f, feature_name in enumerate(result["names"]):
            results[f"{ch_name}-{feature_name}"] = result["values"][f]
    r = {f"{i}-{n}": pd.Series(results)}
    return r


def epochs_C22_PCA_plot(pca_data, n_components):

    if n_components == 2:

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        ax.scatter(
            pca_data[:, 0],
            pca_data[:, 1],
            s=40,
        )

        ax.set(
            title="First two PCA dimensions",
            xlabel="1st Eigenvector",
            ylabel="2nd Eigenvector",
        )

        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])

    elif n_components == 3:

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="3d", elev=-150, azim=110)

        ax.scatter(
            pca_data[:, 0],
            pca_data[:, 1],
            pca_data[:, 2],
            s=40,
        )

        ax.set(
            title="First three PCA dimensions",
            xlabel="1st Eigenvector",
            ylabel="2nd Eigenvector",
            zlabel="3rd Eigenvector",
        )

        ax.xaxis.set_ticklabels([])
        ax.yaxis.set_ticklabels([])
        ax.zaxis.set_ticklabels([])

    else:
        raise ValueError("We can plot only 2 or 3 PCA components.")

    plt.show()
    return fig


# VIEW HELPER FUNCTION


def view(processing_dict, parameters, view_parameters):

    # 1 - Create the tree of the view dictionnary
    view = create_tree(view_parameters)

    # 2 - Fill the tree of the view dictionnary according to conditions
    view = fill_tree(
        processing_dict=processing_dict,
        view_parameters=view_parameters,
        steps=["file_path", *list(parameters["processing"].keys())],
        nstep=0,
        view=view,
        info={},
    )

    return view


def create_tree(view_parameters, view=None):

    if view == None:
        view = {}

    # The view dict will be nested at a step only if there are several possible conditions,
    # so only if conditions are registered as a list or a dict of conditions.

    view_parameters = {
        key: value
        for key, value in view_parameters.items()
        if (isinstance(value, list) or isinstance(value, dict))
    }
    if not view_parameters:
        return view

    for key, value in view_parameters.items():

        if isinstance(value, list):
            for c in value:
                view[c] = {}
                next_view_parameters = copy.deepcopy(view_parameters)
                del next_view_parameters[key]
                create_tree(next_view_parameters, view[c])

        elif isinstance(value, dict):
            for c in value.keys():
                view[c] = {}
                next_view_parameters = copy.deepcopy(view_parameters)
                del next_view_parameters[key]
                create_tree(next_view_parameters, view[c])

        return view


def fill_tree(processing_dict, view_parameters, steps, nstep=0, view=None, info=None):

    if view is None:
        view = {}
    if info is None:
        info = {}

    if nstep >= len(steps):
        return

    for key, value in processing_dict.items():

        info_copy = info.copy()
        info_copy[steps[nstep]] = key

        # If the value is a dict we are not at the bottom file level yet.
        if type(value) is dict:
            fill_tree(
                processing_dict[key],
                view_parameters,
                steps,
                nstep=nstep + 1,
                view=view,
                info=info_copy,
            )

        else:
            check = True
            path = []
            for step, condition in view_parameters.items():
                check, path = check_conditions(check, path, step, condition, info_copy)
            if check:
                update_tree(view, path, value)

    return view


def check_conditions(check, path, step, condition, info):
    match str(type(condition)):
        case "<class 'function'>":
            if not condition(info):
                check = False
        case "<class 'str'>":
            if condition == "all":
                path.append(info[step])
            else:
                raise Exception(f"'{condition}' is not a valid argument")
        case "<class 'list'>":
            if info[step] in condition:
                path.append(info[step])
            else:
                check = False
        case "<class 'dict'>":
            dict_check = False
            for category, cond in condition.items():
                if cond(info):
                    path.append(category)
                    dict_check = True
            if dict_check == False:
                check = False
    return check, path


def update_tree(view, path, value):
    p = path.copy()
    current = view

    # descend
    while len(p) > 1:
        head = p.pop(0)
        current = current[head]

    leaf = p[0]

    # If this is the first real value and the node is an empty dict, replace it
    if isinstance(current[leaf], dict) and not current[leaf]:
        # Replace empty dict with list containing the new value
        current[leaf] = [value]
        return

    # Otherwise proceed normally
    if isinstance(current[leaf], list):
        current[leaf].append(value)
    else:
        current[leaf] = [current[leaf], value]


"""
def update_tree(view, path, value):
    if len(path) == 0:
        print(path)
        if type(view) is dict:
            view = [copy.deepcopy(value)]
        elif type(view) is list:
            view.append(copy.deepcopy(value))
    while len(path) > 1:
        view = view[path.pop(0)]
    if isinstance(view[path[0]], dict):
        view[path.pop(0)] = [copy.deepcopy(value)]
    elif isinstance(view[path[0]], list):
        view[path.pop(0)].append(copy.deepcopy(value))
"""
