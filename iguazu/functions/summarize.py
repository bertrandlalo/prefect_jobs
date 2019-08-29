from importlib import import_module

import numpy as np
import pandas as pd
from scipy.stats import linregress
from sklearn.metrics import auc


def signal_to_feature(data, sequences_report, *, feature_definitions, sequences=None):
    ''' Extract features from a time series defined on a period (slice).

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the processed time series

    sequences_report: pd.DataFrame
        Dataframe with two rows [begins, ends]
    feature_definitions: dict
        Dictionary where keys define the name of the feature (suffix of the column)
        and the values are dictionary that define the feature, with the following keys:
            - columns (list): to select a subpart of the data. Default to all columns.
            - class (str of type module_name.func_name): to apply a reducing function to a pandas.Series.
            - custom (str) : to compute custom features (eg. linear regression, auc)
            - divide_by_duration (bool) : whether or not the feature should be divided by the
              duration of the slice. Default to False.
            - drop_bad_samples (bool): When True, if a column in the data is called "bad",
              then consider only the good samples (ie. where bad is False). Default to False.
            - empty_policy (str|float|NaN): Value to set when the truncated data is empty
               (for example, if all samples have been dropped because they were bad).
                Default to np.NaN.
    sequences: list
        List of sequence names to consider. If None, all available sequences
        from sequences_report are considered.

    Returns
    -------
    features: pd.DataFrame

    Examples
    --------

    In this example, we have SCR peaks characteristics as data and we extract
    certain features on specific periods/sequences of the VR session.

    For example, we extract:

        - 'tau' defined as the sum of the column 'SCR_peaks_detected',
        ie. the sum of the detected peaks on a specific period, divided by the
        period duration.

        - 'median' defined as the median of columns 'SCR_peaks_increase-duration',
        and 'SCR_peaks_increase-amplitude'.

    The result is a dataframe where the index are the period names and the column
    are named by column_feature (eg. SCR_peaks_detected_tau for feature tau estimated on
    SCR_peaks_detected).

    >>> data
                                                    SCR_peaks_detected   SCR_peaks_increase-duration       bad
            2019-03-29 13:36:33.376220951+00:00                True     1.374938                    ...  False
            2019-03-29 13:36:41.018457394+00:00                True     2.367081                    ...  False
            2019-03-29 13:54:12.321063443+00:00                True     7.499662                    ...   True
            2019-03-29 13:54:29.615212103+00:00                True     6.148160                    ...  False
            2019-03-29 13:54:44.495406190+00:00                True     6.896174                    ...  False
                ...
    >>> sequences_report
                                     intro_sequence_0  ...          cardiac-coherence_survey_1
            begin 2019-03-29 13:36:19.863029298+00:00  ... 2019-03-29 13:48:34.481497988+00:00
            end   2019-03-29 13:38:03.406418841+00:00  ... 2019-03-29 13:49:28.501953058+00:00
    >>> feature_definitions = { "tau": {"class": "numpy.sum", "columns": ["SCR_peaks_detected"],
                                "divide_by_duration": True, "empty_policy": 0.0, "drop_bad_samples": True},
                            "median": {"class": "numpy.nanmedian", "columns": ['SCR_peaks_increase-duration', 'SCR_peaks_increase-amplitude'],
                                "divide_by_duration": False, "empty_policy": "bad", "drop_bad_samples": True}}
    >>> features = signal_to_feature(data, sequences_report, feature_definitions=scr_feature_definitions, sequences=None)
    >>> features
        name                                               SCR_peaks_detected_tau  ... SCR_peaks_increase-duration_median
        intro_sequence_0                                                        2  ...                            1.87101
        physio-sonification_playground_0                                      bad  ...                                bad
        space-stress_survey_0                                                   2  ...                             3.9842
        space-stress_survey_1                                                   5  ...                             2.7323
        physio-sonification_sequence_0                                        bad  ...                                bad
        space-stress_sequence_0                                                37  ...                            2.45887
        baseline_eyes-opened_0                                                bad  ...                                bad
        baseline_eyes-opened_1                                                bad  ...                                bad
        baseline_eyes-opened_2                                                bad  ...                                bad
        baseline_eyes-opened_3                                                bad  ...                                bad

    '''
    for feature_definition in feature_definitions.values():
        if "columns" not in feature_definition:
            feature_definition["columns"] = None
        if "divide_by_duration" not in feature_definition:
            feature_definition["divide_by_duration"] = False
        if "drop_bad_samples" not in feature_definition:
            feature_definition["drop_bad_samples"] = False
        if "empty_policy" not in feature_definition:
            feature_definition["empty_policy"] = np.NaN
    sequences = sequences or sequences_report.columns

    features = [pd.DataFrame()]
    for sequence in sequences:
        for sequence_occurence in [s for s in sequences_report.columns if sequence in s]:
            begin = sequences_report.loc["begin", sequence_occurence]
            end = sequences_report.loc["end", sequence_occurence]
            data_truncated = data[begin:end]
            duration = (end - begin) / np.timedelta64(1, 's')
            if not data_truncated.empty:
                data_truncated.index -= data_truncated.index[0]
                data_truncated.index /= np.timedelta64(1, 's')  # convert datetime index into floats

            features_on_sequence = []

            for feature_name, feature_definition in feature_definitions.items():
                empty_policy = feature_definition["empty_policy"]
                if feature_definition["columns"] in ["all", None]:
                    columns = data_truncated.columns
                else:
                    columns = set(feature_definition["columns"])
                    if not columns.issubset(data_truncated.columns):
                        raise ValueError("Columns should be a subset of data.columns")
                tmp = data_truncated.loc[:, list(columns)]  # this makes a copy
                if feature_definition["drop_bad_samples"] and "bad" in data_truncated:
                    tmp = tmp[~data_truncated.bad]

                if "custom" in feature_definition:
                    custom = feature_definition["custom"]
                    if custom == "linregress":
                        if tmp.empty:
                            feat = pd.DataFrame(columns=columns,
                                                index=[feature_name + "_slope", feature_name + "_rvalue"],
                                                data=np.array([[empty_policy] * len(columns)] * 2)).T
                        else:
                            feat = [pd.DataFrame()]
                            for column in columns:
                                tmp_col = tmp[column].dropna()
                                if tmp_col.empty:
                                    slope, rvalue = empty_policy, empty_policy
                                else:
                                    x = tmp_col.values.astype(float)
                                    y = tmp_col.index
                                    slope, intercept, rvalue, pvalue, stderr = linregress(x, y)

                                feat.append(pd.DataFrame(index=[feature_name + "_slope", feature_name + "_rvalue"],
                                                         data=[slope, rvalue], columns=[column]))
                            feat = pd.concat(feat, axis=0, sort=True).T
                    elif custom == "auc":
                        if tmp.empty:
                            feat = pd.DataFrame(columns=columns,
                                                index=[feature_name],
                                                data=[empty_policy] * len(columns)).T
                        else:
                            feat = [pd.DataFrame()]
                            for column in columns:
                                tmp_col = tmp[column].dropna()
                                if len(tmp_col) <= 1:  # At least 2 points are needed to compute area under curve
                                    auc_value = empty_policy
                                else:
                                    y = tmp_col.values.astype(float)
                                    x = tmp_col.index
                                    auc_value = auc(y=y, x=x)
                                feat.append(pd.DataFrame(index=[feature_name],
                                                         data=[auc_value], columns=[column]))
                            feat = pd.concat(feat, axis=0, sort=True).T
                    else:
                        raise ValueError(f'Unknown custom definition "{custom}"')
                else:
                    if tmp.empty:
                        feat = pd.DataFrame(index=columns,
                                            columns=[feature_name],
                                            data=[empty_policy] * len(columns))
                    else:

                        split = feature_definition["class"].rsplit('.', 1)
                        module_name = split[0]
                        class_name = split[1]
                        m = import_module(module_name)
                        _func = getattr(m, class_name)
                        feat = tmp.astype(float).apply(_func)

                if feature_definition["divide_by_duration"]:
                    feat /= duration

                if type(feat) == pd.Series:
                    feat_columns = [feature_name]
                else:
                    feat_columns = feat.columns
                features_on_sequence.append(pd.DataFrame(feat, columns=feat_columns))
            # concat all the features list in a DataFrame
            features_on_sequence = pd.concat(features_on_sequence, axis=1, sort=True).T
            # small magic to melt the DataFrame in a flat (one row) one, with columns are
            # renamed with their name with as suffix "_" + index name,
            #  that is columns are: column-name_feature-name
            features_on_sequence_flat = features_on_sequence.reset_index().melt(id_vars=['index'],
                                                                                value_vars=features_on_sequence.columns)
            features_on_sequence_flat['name'] = features_on_sequence_flat['variable'] + '_' + features_on_sequence_flat[
                'index']
            features_on_sequence_flat = features_on_sequence_flat[['name', 'value']].set_index('name').transpose()
            features_on_sequence_flat.index = [sequence_occurence]
            # drop columns that have ONLY NaNs
            features_on_sequence_flat = features_on_sequence_flat.dropna(how="all", axis=1)

            features.append(features_on_sequence_flat)
    features = pd.concat(features, sort=False)

    return features

