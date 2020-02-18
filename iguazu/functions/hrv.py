"""
HRV feature calculation functions and related code

These functions implement the extraction of several HRV features
from either raw RR intervals, interpolated RR intervals or NN intervals.

Initially, these functions were implemented in NeuroKit (in particular this
`function <https://github.com/neuropsychology/NeuroKit.py/blob/master/neurokit/bio/bio_ecg.py#L393>`_.
But after a careful analysis of NeuroKit's code, we decided to take some bits
of it and rewrite others.

These functions reference several publications,

* For most feature definitions and how much data they need:

  Shaffer, F., & Ginsberg, J. P. (2017).
  An Overview of Heart Rate Variability Metrics and Norms.
  Frontiers in Public Health, 5 (September), 1–17. https://doi.org/10.3389/fpubh.2017.00258

* In some cases, an older but complimentary reference:

  Task Force of the European Society of Cardiology (1996).
  Heart Rate Variability.
  Circulation, 93(5), 1043–1065. https://doi.org/10.1161/01.CIR.93.5.1043

* A different reference used by NeuroKit for some features not included in the
  previous references:

  Voss, A., Schroeder, R., Heitmann, A., Peters, A., & Perz, S. (2015).
  Short-term heart rate variability - Influence of gender and age in healthy subjects.
  PLoS ONE, 10(3), 1–33. https://doi.org/10.1371/journal.pone.0118308

* Finally, the Kubios manual:

  Tarvainen MNiskanen J. (2012).
  Kubios HRV version 2.1 USER’S GUIDE.
  Finland: Biosignal Analysis And, 1–44.
  Retrieved from http://pulse-sports.ru/a_ryzhov/rr/Kubios_HRV_Users_Guide.pdf

Notes
=====

We should review in which cases we need to use the raw RR or the NN intervals,
because literature often use these terms interchangeably.

"""

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from nolds.measures import dfa
from pyentrp.entropy import shannon_entropy

from iguazu.core.features import dataclass_to_dataframe
from iguazu.functions.common import verify_monotonic
from iguazu.functions.spectral import bandpower
from iguazu.functions.unity import VALID_SEQUENCE_KEYS

logger = logging.getLogger(__name__)


# The functions in this module return several values at once. The following
# dataclasses are defined for an expressive, explicit code, and to avoid
# returning a dict. We also get, as a bonus, automatic default values when
# the feature cannot be calculated.

@dataclass
class HRVTimeFeatures:
    RMSSD: float = field(default=np.nan,
                         metadata=dict(
                             name='Root mean square of successive NN interval differences',
                             unit='ms',
                         ))
    meanNN: float = field(default=np.nan,
                          metadata=dict(
                             name='Mean of NN intervals',
                             unit='ms',
                          ))
    SDNN: float = field(default=np.nan,
                        metadata=dict(
                            name='Standard deviation of NN intervals',
                            unit='ms',
                        ))
    medianNN: float = field(default=np.nan,
                            metadata=dict(
                                name='Median of NN intervals',
                                unit='ms',
                            ))
    pNN50: float = field(default=np.nan,
                         metadata=dict(
                            name='Percentage of successive NN intervals that differ by more than 50 ms',
                            unit='%',
                         ))
    pNN20: float = field(default=np.nan,
                         metadata=dict(
                            name='Percentage of successive NN intervals that differ by more than 20 ms',
                            unit='%',
                         ))


@dataclass
class HRVFrequencyFeatures:
    VLF: float = field(default=np.nan,
                       metadata=dict(
                           name='Absolute power of the very-low frequency band',
                           unit='ms^2',
                       ))
    LF: float = field(default=np.nan,
                      metadata=dict(
                          name='Absolute power of the low frequency band',
                          unit='ms^2',
                      ))
    HF: float = field(default=np.nan,
                      metadata=dict(
                          name='Absolute power of the high frequency band',
                          unit='ms^2',
                      ))
    VHF: float = field(default=np.nan,
                       metadata=dict(
                           name='Absolute power of the very-high frequency band',
                           unit='ms^2',
                       ))
    LFHF: float = field(default=np.nan,
                        metadata=dict(
                            name='Ratio of LF-to-HF power',
                            unit='%',
                        ))


@dataclass
class HRVNonLinearFeatures:
    DFA1: float = field(default=np.nan,
                        metadata=dict(
                            name='DFA α1, short-term fractal scaling exponent',
                            unit=None,
                        ))
    DFA2: float = field(default=np.nan,
                        metadata=dict(
                            name='DFA α2, long-term fractal scaling exponent',
                            unit=None,
                        ))


@dataclass
class HRVGeometricFeatures:
    HTI: float = field(default=np.nan,
                       metadata=dict(
                           name='HRV triangular index',
                           unit=None,
                       ))
    Shannon_h: float = field(default=np.nan,
                             metadata=dict(
                                 name='Shannon entropy',
                                 unit='bit',
                             ))


# def hrv_features_dataframe(*args, **kwargs):
#     features = hrv_features(*args, **kwargs)
#     # Convert from
#     # [(sequence_name, {'feat1': value1, ...}), ...]
#     # to a dataframe with sequences in rows, features in columns
#     if not features:
#         df_features = pd.DataFrame()
#     else:
#         tmp = []
#         for f in features:
#             tmp.append(
#
#             )
#         tmp = pd.DataFrame.from_dict(dict(features), orient='index')
#         df_features = pd.concat([tmp[col].apply(pd.Series) for col in tmp.columns],
#                                 axis='index', sort=False)
#         import ipdb; ipdb.set_trace(context=21)
#         pass
#
#
#     logger.debug('HRV features, wide version:\n%s', df_features.to_string())
#
#     df_wide = df_features.rename_axis(index='id').reset_index()
#
#     return df_features


def hrv_features(nn, nn_interpolated, events, known_sequences=None):
    known_sequences = known_sequences or VALID_SEQUENCE_KEYS

    features = []
    # for name, row in events.T.iterrows():  # transpose due to https://github.com/OpenMindInnovation/iguazu/issues/54
    for index, row in events.iterrows():
        logger.debug('Processing sequence %s at %s', row.id, index)
        if row.id not in known_sequences:
            logger.debug('Sequence %s is not on the known sequence list', row.id)
            continue

        begin = row.begin
        end = row.end
        nn_sequence = nn.loc[begin:end].copy()
        nni_sequence = nn_interpolated.loc[begin:end].copy()

        logger.debug('NN series has %d samples', len(nn_sequence))
        time_features = hrv_time_features(nn_sequence)
        geometric_features = hrv_geometric_features(nn_sequence)
        frequency_features = hrv_frequency_features(nni_sequence)
        nonlinear_features = hrv_nonlinear_features(nn_sequence)

        all_features = (
            pd.concat([dataclass_to_dataframe(time_features),
                       dataclass_to_dataframe(geometric_features),
                       dataclass_to_dataframe(frequency_features),
                       dataclass_to_dataframe(nonlinear_features)],
                      axis='index', sort=False)
            .rename_axis(index='id')
            .reset_index()
        )
        all_features.insert(0, 'reference', row.id)
        features.append(all_features)

    if len(features) > 0:
        features = pd.concat(features, axis='index', ignore_index=True, sort=False)
        logger.info('Generated a feature dataframe of shape %s', features.shape)
    else:
        logger.info('No features were generated')
        features = pd.DataFrame(columns=['id', 'reference', 'value'])

    return features


def hrv_time_features(dataframe: pd.DataFrame, column: str = 'NN') -> HRVTimeFeatures:
    verify_monotonic(dataframe, column)

    if 'bad' in dataframe:
        dataframe = dataframe.loc[~dataframe.bad]

    features = HRVTimeFeatures()
    if dataframe.empty:
        logger.warning('Not enough NN segments to calculate HRV time features, '
                       'returning nan for all features')
        return features

    nn = dataframe['NN']
    period_mins = (nn.index[-1] - nn.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating time features on %.1f minutes of NN data', period_mins)

    # RMSSD: Root mean square of successive NN interval differences in ms
    # [Shaffer and Ginsberg, page 4]
    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for RMSSD is 5 min, '
                       'calculating on %.1f min', period_mins)
    features.RMSSD = np.sqrt(np.mean(np.diff(nn) ** 2))

    # meanNN: Mean of NN. Not a classic feature present on literature (to my knowledge),
    # but calculated in neurokit
    features.meanNN = np.mean(nn)

    # SDNN: Standard deviation of NN intervals
    # [Shaffer and Ginsberg, page 3]
    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for SDNN is 5 min, '
                       'calculating on %.1f min', period_mins)
    features.SDNN = np.std(nn, ddof=1)

    # medianNN: Median of NN. Not a classic feature present on literature (to my knowledge),
    # but calculated in neurokit
    features.medianNN = np.median(nn)

    # pNN50: Percentage of successive NN intervals that differ by more than 50 ms
    # [Shaffer and Ginsberg, page 4]
    if period_mins < 2:
        logger.warning('The recommended minimum amount of data for pNN50 is 2 min, '
                       'calculating on %.1f min', period_mins)
    nn50 = np.sum(np.diff(nn) > 50)
    features.pNN50 = 100 * nn50 / len(nn)

    # pNN50: Percentage of successive nn intervals that differ by more than 20 ms
    # [Voss et al., page 5]
    nn20 = np.sum(np.diff(nn) > 20)
    features.pNN20 = 100 * nn20 / len(nn)

    logger.debug('HRV time features: %s', features)
    return features


def hrv_geometric_features(dataframe: pd.DataFrame, column: str = 'NN') -> HRVGeometricFeatures:
    verify_monotonic(dataframe, column)

    if 'bad' in dataframe:
        dataframe = dataframe.loc[~dataframe.bad]

    features = HRVGeometricFeatures()
    if dataframe.empty:
        logger.warning('Not enough NN segments to calculate HRV geometric features,'
                       'returning nan for all features')
        return features

    nn = dataframe[column]
    period_mins = (nn.index[-1] - nn.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating geometric features on %.1f minutes of NN data', period_mins)

    # HRV Triangular index: Integral of the density of the NN interval histogram
    # divided by its height
    # [Shaffer and Ginsberg, page 4]
    # According to [Task force, page 356],
    # ... with bins approximately 8 ms long (precisely 7.8125 ms= 1/128 s)
    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for HTI is 5 min, '
                       'calculating on %.1f min', period_mins)
    # Bin width is = 1 / 128 = 0.0078125 seconds = 7.8125 milliseconds
    # note that since NN is in milliseconds, we need to put our bins in ms too
    bin_width = 1000 / 128
    bins = np.arange(nn.min(), nn.max(), step=bin_width)
    histogram = np.digitize(nn, bins)
    max_bin = histogram.max()
    # According to Task force:
    # ... [the HRV triangular index] is approximated by the value:
    # (total number of NN intervals)/ (number of NN intervals in the modal bin)
    #
    # Note that in neurokit, this calculation is wrong, since it uses the
    # histogram density not the regular histogram
    features.HTI = nn.shape[0] / max_bin

    # Shannon entropy
    # In [Voss], it's not really well explained what this is supposed to do
    # "...calculated on the basis of the class probabilities p_i ... of the NN
    # interval density distribution ... resulting in a smoothed histogram
    # suitable for HRV analysis [1].
    density = histogram / bin_width / histogram.sum()  # This is how np.histogram calculates density
    features.Shannon_h = shannon_entropy(density)

    logger.debug('HRV geometric features: %s', features)
    return features


def hrv_frequency_features(dataframe: pd.DataFrame, column: str = 'NNi') -> HRVFrequencyFeatures:
    verify_monotonic(dataframe, column)

    if dataframe.empty:
        logger.warning('Not enough NN segments to calculate HRV frequency features, '
                       'returning nan for all features')
        return HRVFrequencyFeatures()

    if dataframe.shape[1] != 1:
        # Fail now, otherwise the mean on the bandpower will give many results
        raise ValueError('hrv_frequency_features requires a single-column dataframe')

    # band defined as (f_start, f_stop, epoch_size, epoch_overlap)
    # epoch overlap will be systematically size - 1 to get one epoch per second
    bands = dict(
        VLF=(0.003, 0.04, 300, 299),  # 12 bins at 512 Hz
        LF= (0.040, 0.15, 120, 119),  # 13 bins at 512 Hz
        HF= (0.150, 0.40,  60,  59),  # 15 bins at 512 Hz
        VHF=(0.400, 0.50,  60,  59),  # 6  bins at 512 Hz
    )

    nni = dataframe[column]
    period_mins = (nni.index[-1] - nni.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating spectral features on %.1f minutes of NNi data', period_mins)

    # Show all warnings first
    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for VLF power is 5 min, '
                       'calculating on %.1f min', period_mins)
    if period_mins < 2:
        logger.warning('The recommended minimum amount of data for LF power is 2 min, '
                       'calculating on %.1f min', period_mins)
    if period_mins < 1:
        logger.warning('The recommended minimum amount of data for HF power is 1 min, '
                       'calculating on %.1f min', period_mins)
        logger.warning('The recommended minimum amount of data for VHF power is 1 min, '
                       'calculating on %.1f min', period_mins)

    powers = {}
    for name in bands:
        fstart, fstop, size, overlap = bands[name]
        try:
            # Note: We are using spectrum, not density. I do not know a paper
            # that gives the detail of whether this power is calculated on a
            # density or regular spectrum, but papers usually report this value
            # with ms^2 units: Schaffer, (table 2), task force (figure 4).
            # Counter example: task force (figure 3)  ¯\_(ツ)_/¯
            bp_windowed = bandpower(nni, bands={name: (fstart, fstop)},
                                    epoch_size=size, epoch_overlap=overlap,
                                    scaling='spectrum', relative=False)
            powers[name] = bp_windowed.mean()[0]
        except ValueError as ex:
            logger.warning('Bandpower failed: %s, setting %s to nan', str(ex), name)
            powers[name] = np.nan

    features = HRVFrequencyFeatures(**powers)
    features.LFHF = features.LF / features.HF

    logger.debug('HRV frequency features: %s', features)
    return features


def hrv_nonlinear_features(dataframe: pd.DataFrame, column: str = 'NN') -> HRVNonLinearFeatures:
    verify_monotonic(dataframe, column)

    if 'bad' in dataframe:
        dataframe = dataframe.loc[~dataframe.bad]

    features = HRVNonLinearFeatures()
    if dataframe.empty:
        logger.warning('Not enough NN segments to calculate HRV nonlinear features,'
                       'returning nan for all features')
        return features

    nn = dataframe[column]
    period_mins = (nn.index[-1] - nn.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating nonlinear features on %.1f minutes of NN data '
                 '(%d samples)', period_mins, len(nn))

    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for DFA1 and DFA2 is 5 min, '
                       'calculating on %.1f min', period_mins)

    # Detrended fluctuation analysis:
    # Voss: quantifies the fractal scaling properties of time series
    # [Voss, page 5]  and [Tarvainen, page 16] define this as the
    # correlation of the NN intervals for the 4th to 16th interval for DFA-alpha1
    # and 16th to 64th interval for DFA-alpha2.
    # However, these are 1-indexed values, not 0-indexed, which is why we need
    # to consider the 3-15 interval and 15-63 interval respectively.
    # On another note, neurokit uses 16th to 66th, who knows why, and does not
    # correct for the 1-indexed samples.
    if len(nn) >= 16:
        features.DFA1 = dfa(nn, np.arange(3, 16))
    else:
        logger.warning('Not enough NN segments to calculate DFA1')

    if len(nn) >= 64:
        features.DFA2 = dfa(nn, np.arange(16, 64))
    else:
        logger.warning('Not enough NN segments to calculate DFA2')

    logger.debug('HRV non-linear features: %s', features)
    return features
