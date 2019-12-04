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
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd
from pyentrp.entropy import shannon_entropy
from nolds.measures import dfa

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
    RMSSD: float = np.nan
    meanNN: float = np.nan
    SDNN: float = np.nan
    medianNN: float = np.nan
    pNN50: float = np.nan
    pNN20: float = np.nan


@dataclass
class HRVFrequencyFeatures:
    VLF: float = np.nan
    LF: float = np.nan
    HF: float = np.nan
    VHF: float = np.nan
    LFHF: float = np.nan


@dataclass
class HRVNonLinearFeatures:
    DFA1: float = np.nan
    DFA2: float = np.nan


@dataclass
class HRVGeometricFeatures:
    HTI: float = np.nan
    Shannon_h: float = np.nan


def hrv_features(RR, RRi, events, known_sequences=None):
    known_sequences = known_sequences or VALID_SEQUENCE_KEYS

    features = []
    for name, row in events.T.iterrows():  # transpose due to https://github.com/OpenMindInnovation/iguazu/issues/54
        logger.debug('Processing sequence %s', name)
        if name not in known_sequences:
            logger.debug('Sequence %s is not on the known sequence list', name)
            continue

        begin = row.begin
        end = row.end
        RR_sequence = RR.loc[begin:end].copy()
        RRi_sequence = RRi.loc[begin:end].copy()

        logger.debug('RR sequence has %d potential elements', len(RR_sequence))
        time_features = hrv_time_features(RR_sequence)
        geometric_features = hrv_geometric_features(RR_sequence)
        frequency_features = hrv_frequency_features(RRi_sequence)
        nonlinear_features = hrv_nonlinear_features(RR_sequence)

        merged = dict()
        merged.update(asdict(time_features))
        merged.update(asdict(geometric_features))
        merged.update(asdict(frequency_features))
        merged.update(asdict(nonlinear_features))
        features.append((name, merged))

    # Convert from
    # [(sequence_name, {'feat1': value1, ...}), ...]
    # to a dataframe with sequences in rows, features in columns
    if not features:
        df_features = pd.DataFrame()
    else:
        df_features = pd.DataFrame.from_items(features).T

    logger.debug('HRV features:\n%s', df_features.to_string())
    return df_features


def hrv_time_features(df_rr: pd.DataFrame) -> HRVTimeFeatures:
    verify_monotonic(df_rr, 'RR')

    if 'bad' in df_rr:
        df_rr = df_rr.loc[~df_rr.bad]

    features = HRVTimeFeatures()
    if df_rr.empty:
        logger.warning('Not enough RR segments to calculate HRV time features, '
                       'returning nan for all features')
        return features

    RR = df_rr['RR']
    period_mins = (RR.index[-1] - RR.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating time features on %.1f minutes of RR data', period_mins)

    # RMSSD: Root mean square of successive RR interval differences in ms
    # [Shaffer and Ginsberg, page 4]
    # TODO: should this be on the NN (normal peaks) or the RR ?
    #       Neurokit uses NN (even if it calls it RR)
    #       I am going to assume that NN is RR, in other words RR is all clean data
    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for RMSSD is 5 min, '
                       'calculating on %.1f min', period_mins)
    features.RMSSD = np.sqrt(np.mean(np.diff(RR) ** 2))

    # meanNN: Mean of NN. Not a classic feature present on literature (to my knowledge),
    # but calculated in neurokit
    features.meanNN = np.mean(RR)

    # SDNN: Standard deviation of NN intervals
    # [Shaffer and Ginsberg, page 3]
    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for SDNN is 5 min, '
                       'calculating on %.1f min', period_mins)
    features.SDNN = np.std(RR, ddof=1)

    # medianNN: Median of NN. Not a classic feature present on literature (to my knowledge),
    # but calculated in neurokit
    features.medianNN = np.median(RR)

    # pNN50: Percentage of successive RR intervals that differ by more than 50 ms
    # [Shaffer and Ginsberg, page 4]
    if period_mins < 2:
        logger.warning('The recommended minimum amount of data for pNN50 is 2 min, '
                       'calculating on %.1f min', period_mins)
    nn50 = np.sum(np.diff(RR) > 50)
    features.pNN50 = 100 * nn50 / len(RR)

    # pNN50: Percentage of successive RR intervals that differ by more than 20 ms
    # [Voss et al., page 5]
    nn20 = np.sum(np.diff(RR) > 20)
    features.pNN20 = 100 * nn20 / len(RR)

    logger.debug('HRV time features: %s', features)
    return features


def hrv_geometric_features(df_rr: pd.DataFrame) -> HRVGeometricFeatures:
    verify_monotonic(df_rr, 'RR')

    if 'bad' in df_rr:
        df_rr = df_rr.loc[~df_rr.bad]

    features = HRVGeometricFeatures()
    if df_rr.empty:
        logger.warning('Not enough RR segments to calculate HRV geometric features,'
                       'returning nan for all features')
        return features

    RR = df_rr['RR']
    period_mins = (RR.index[-1] - RR.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating geometric features on %.1f minutes of RR data', period_mins)

    # HRV Triangular index: Integral of the density of the RR interval histogram
    # divided by its height
    # [Shaffer and Ginsberg, page 4]
    # According to [Task force, page 356],
    # ... with bins approximately 8 ms long (precisely 7.8125 ms= 1/128 s)
    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for HTI is 5 min, '
                       'calculating on %.1f min', period_mins)
    # Bin width is = 1 / 128 = 0.0078125 seconds = 7.8125 milliseconds
    # note that since RR is in milliseconds, we need to put our bins in ms too
    bin_width = 1000 / 128
    bins = np.arange(RR.min(), RR.max(), step=bin_width)
    histogram = np.digitize(RR, bins)
    max_bin = histogram.max()
    # According to Task force:
    # ... [the HRV triangular index] is approximated by the value:
    # (total number of NN intervals)/ (number of NN intervals in the modal bin)
    #
    # Note that in neurokit, this calculation is wrong, since it uses the
    # histogram density not the regular histogram
    features.HTI = RR.shape[0] / max_bin

    # Shannon entropy
    # In [Voss], it's not really well explained what this is supposed to do
    # "...calculated on the basis ofthe class probabilities pi ... of the NN
    # interval density distribution ... resulting in a smoothed histogram
    # suitable for HRV analysis [1].
    density = histogram / bin_width / histogram.sum()  # This is how np.histogram calculates density
    features.Shannon_h = shannon_entropy(density)

    logger.debug('HRV geometric features: %s', features)
    return features


def hrv_frequency_features(df_rri: pd.DataFrame) -> HRVFrequencyFeatures:
    verify_monotonic(df_rri, 'RRi')

    if df_rri.empty:
        logger.warning('Not enough RR segments to calculate HRV frequency features, '
                       'returning nan for all features')
        return HRVFrequencyFeatures()

    if df_rri.shape[1] != 1:
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

    RRi = df_rri['RRi']
    period_mins = (RRi.index[-1] - RRi.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating spectral features on %.1f minutes of RRi data', period_mins)

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
            bp_windowed = bandpower(RRi, bands={name: (fstart, fstop)},
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


def hrv_nonlinear_features(df_rr: pd.DataFrame) -> HRVNonLinearFeatures:
    verify_monotonic(df_rr, 'RR')

    if 'bad' in df_rr:
        df_rr = df_rr.loc[~df_rr.bad]

    features = HRVNonLinearFeatures()
    if df_rr.empty:
        logger.warning('Not enough RR segments to calculate HRV nonlinear features,'
                       'returning nan for all features')
        return features

    RR = df_rr['RR']
    period_mins = (RR.index[-1] - RR.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating nonlinear features on %.1f minutes of RR data '
                 '(%d samples)', period_mins, len(RR))

    if period_mins < 5:
        logger.warning('The recommended minimum amount of data for DFA1 and DFA2 is 5 min, '
                       'calculating on %.1f min', period_mins)

    # Detrended fluctuation analysis:
    # Voss: quantifies the fractal scaling properties of time series
    # [Voss, page 5]  and [Tarvainen, page 16] define this as the
    # correlation of the RR intervals for the 4th to 16th interval for DFA-alpha1
    # and 16th to 64th interval for DFA-alpha2.
    # However, these are 1-indexed values, not 0-indexed, which is why we need
    # to consider the 3-15 interval and 15-63 interval respectively.
    # On another note, neurokit uses 16th to 66th, who knows why, and does not
    # correct for the 1-indexed samples.
    if len(RR) >= 16:
        features.DFA1 = dfa(RR, np.arange(3, 16))
    else:
        logger.warning('Not enough RR segments to calculate DFA1')

    if len(RR) >= 64:
        features.DFA2 = dfa(RR, np.arange(16, 64))
    else:
        logger.warning('Not enough RR segments to calculate DFA2')

    logger.debug('HRV non-linear features: %s', features)
    return features
