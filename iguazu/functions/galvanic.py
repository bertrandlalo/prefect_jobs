import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm
from dsu.cvxEDA import apply_cvxEDA
from dsu.dsp.filters import filtfilt_signal, scale_signal, drop_rows
from dsu.dsp.peaks import detect_peaks
from dsu.epoch import sliding_window
from dsu.pandas_helpers import estimate_rate
from sklearn.metrics import auc
from sklearn.preprocessing import RobustScaler

from iguazu.core.features import dataclass_to_dataframe

logger = logging.getLogger(__name__)


class GSRArtifactCorruption(Exception):
    """Exception used when GSR signal is corrupted"""
    pass


def galvanic_clean(signals, events, annotations, column, warmup_duration, corrupted_maxratio,
                   interpolation_kwargs, filter_kwargs, scaling_kwargs):
    """
     Preprocess the galvanic data.
     It should be noted that some steps here are specific to the device we use, ie. Nexus from MindMedia.
     Eg. When the amplifier saturates (ie. Voltage above 2V, ie. resistance too low), Nexus will return 0.0, but other
     devices might have different behaviors.

    The pipeline will:

        - lowpass the resulting signal using :py:func:dsu.filters.dsp.bandpass_signal with `filter_kwargs`
        - remove the bad samples and interpolate the missing signal e calling :py:meth:pandas.Series.interpolat with `interpolation_kwargs`.
        - inverse the signal to access galvanic conductance (G=1/R)
        - scale the signal on the whole session using using :py:func:dsu.filters.dsp.scale_signal with `scaling_kwargs`

    Parameters
    ----------
    column: str  #TODO: since it's now standardized, should we fix this to 'GSR'?
        Name of column where the data of interest are located.
    processing steps, ie. that we can then set to bad ).
    interpolation_kwargs:
        Keywords arguments to interpolate the missing (bad) samples.
    filter_kwargs:
        Keywords arguments to lowpass the data.
    scaling_kwargs:
        Keywords arguments to scale the data.

    Returns
    -------
    data: pd.DataFrame
          Dataframe with columns 'gsr', 'gsr_clean', 'gsr_clean_inversed', 'gsr_clean_inversed_lowpassed',
          'gsr_clean_inversed_lowpassed_zscored', 'bad'

    Examples
    --------

        .. image:: ../source/_static/examples/galvanic_functions/io_clean.png

    """

    warmup_timedelta = np.timedelta64(1, 's') * warmup_duration
    begins = events.index[0] - warmup_timedelta  # begin 30 seconds before the beginning of the session
    ends = events.index[-1] + warmup_timedelta  # end 30 seconds after the beginning of the session

    # truncate dataframe on session times
    signals = signals.loc[:, [column]]

    signals.loc[:begins] = np.NaN
    signals.loc[ends:] = np.NaN

    annotations.loc[:begins, [column]] = 'outside_session'
    annotations.loc[ends:, [column]] = 'outside_session'

    # estimate the corrupted ratio
    # if too many samples were dropped, raise an error
    # TODO/Question: do we keep raising an error when corrupted ratio is above a threshold?
    corrupted_ratio = (~annotations[annotations.GSR != 'outside_session'].replace('', np.NaN).isna()).mean()[0]
    if corrupted_ratio > corrupted_maxratio:
        raise GSRArtifactCorruption(f'Artifact corruption of {corrupted_ratio * 100:.0f}% '
                          f'exceeds {corrupted_maxratio * 100:.0f}%')

    # set as 'bad' samples that are more than 5  standard deviations from mean
    outliers = signals[((signals[column] - signals[column].mean()) / signals[column].std()).abs() > 5].dropna().index
    annotations.loc[outliers, column] = 'outliers'
    signals.loc[outliers, column] = np.NaN

    # lowpass filter signal
    logger.debug('Filter with %s to %s Hz', filter_kwargs.get('filter_type', 'bandpass'),
                 filter_kwargs.get('frequencies', []))
    signals = filtfilt_signal(signals, columns=[column],
                              **filter_kwargs, suffix='_filtered')

    # bad sample interpolation
    logger.debug('Interpolating %d/%d bad samples', signals[column].isna().sum(), signals.shape[0])
    # make a copy of the signal with suffix "_clean", mask bad samples
    signals_clean = signals[[column + '_filtered']].copy().add_suffix('_clean')
    # Pandas does not like tz-aware timestamps when interpolating
    if signals_clean.index.tzinfo is None:
        # old way: tz-naive
        signals_clean.interpolate(**interpolation_kwargs, inplace=True)
    else:
        # new way: with timezone. Convert to tz-naive, interpolate, then back to tz-aware
        signals_clean = (
            signals_clean.set_index(signals_clean.index.tz_convert(None))
                .interpolate(**interpolation_kwargs)
                .set_index(signals_clean.index))

    # scale signal on the all session
    logger.debug('Rescaling signals')
    signals_clean = scale_signal(signals_clean, columns=[column + '_filtered_clean'], suffix='_zscored',
                                 **scaling_kwargs)

    # return preprocessed data
    logger.debug('Concatenating clean and filtered signals')
    signals = pd.concat([signals, signals_clean], axis=1)

    return signals, annotations


def downsample(signals, sampling_rate):
    # downsample by dropping rows
    # TODO consider if should we decimate? That is, lowpass filter first?
    logger.debug('Downsampling signal to %d Hz', sampling_rate)
    return drop_rows(signals, sampling_rate)


def galvanic_cvx(signals, annotations, column=None, warmup_duration=15, threshold_scr=4.0,
                 cvxeda_params=None, epoch_size=None, epoch_overlap=None):
    """ Separate galvanic components using a convex deconvolution.

    This function separates the phasic (SCR) and tonic (SCL) galvanic components
    using the cvxEDA algorithm.

    For large signals, the underlying library (cvx) is particularly heavy on
    memory usage. Also, since it uses C code, it holds and does not relase the
    Python global interpreter lock (GIL). This makes everything more difficult,
    in particular for Iguazu. In order to manage this, one can do the algorithm
    by epochs using both the `epoch_size` and `epoch_overlap` parameters.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the preprocessed GSR in channel given by column_name.
    column: str | None
        Name of column where the data of interest are located.
        If None, the first column is considered.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    threshold_scr:
        Maximum acceptable amplitude of SCR component.
    cvxeda_params:
        Keywords arguments to apply cvxEDA algorithm.
    epoch_size: float
        Size in seconds of the epoch size. When set to ``None``, cvxEDA will
        be applied only once on the whole signal.
    epoch_overlap: float
        Size in seconds of the epoch overlap. When set to ``None``, cvxEDA will
        be applied only once on the whole signal.

    Returns
    -------
    data: pd.DataFrame
        Dataframe with columns: `..._SCR`, `..._SCL` and `bad`.

    Examples
    --------

      .. image:: ../source/_static/examples/galvanic_functions/io_deconvolution.png

    """
    cvxeda_params = cvxeda_params or {}

    # extract SCR and SCL component using deconvolution toolbox cvxEDA

    # if no column is specified, consider the first one
    column = column or signals.columns[-1]

    n = signals.shape[0]
    idx_epochs = np.arange(n)[np.newaxis, :]
    idx_warmup = slice(0, n)

    if epoch_size is not None and epoch_overlap is not None:
        fs = estimate_rate(signals)
        n_warmup = int(warmup_duration * fs)
        n_epoch = int(epoch_size * fs) + n_warmup
        n_overlap = int(epoch_overlap * fs)
        logger.debug('Attempting to epoch signal of %d samples into epochs '
                     'of %d samples and %d overlap', n, n_epoch, n_overlap)

        if n < n_epoch + n_overlap:
            # Data is not big enough for window
            logger.debug('Cannot epoch into epochs of %d samples, signal is not '
                         'large enough. Falling back to complete implementation.',
                         n_epoch)
        else:
            idx_epochs = sliding_window(np.arange(n), size=n_epoch, stepsize=n_overlap)
            idx_warmup = slice(n_warmup, -n_warmup)
            logger.debug('cvxEDA epoched implementation with %d epochs', len(idx_epochs))

    else:
        logger.debug('cvxEDA complete implementation')

    epochs = []
    for i, idx in enumerate(idx_epochs):
        logger.debug('Epoch %d / %d', i + 1, len(idx_epochs))
        input = signals.iloc[idx][[column]].dropna()
        if not input.empty:
            chunk = (
                apply_cvxEDA(input, **cvxeda_params)
                    .iloc[idx_warmup]
                    .rename_axis(index='epoched_index')
                    .reset_index()
            )
            epochs.append(chunk)

    if not epochs:
        return pd.DataFrame(), pd.DataFrame()  # or None?

    signals = (
        pd.concat(epochs, ignore_index=False)
            .groupby('epoched_index')
            .mean()
            .rename_axis(index=signals.index.name)
    )

    # add an annotation rejection boolean on amplitude criteria
    # todo: helpers with inputs: data, annotations, and index or bool condition, that sets values in data to NaN and annotate in annotations
    annotations.loc[signals[signals[
                                column + '_SCR'] >= threshold_scr].index, 'GSR'] = 'CVX SCR outlier'  # Todo: question: should we add a new column?

    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')
    annotations.loc[:signals.index[0] + warm_up_timedelta,
    'GSR'] = 'CVX wam up'  # Todo: question: should we add a new column?
    annotations.loc[signals.index[-1] - warm_up_timedelta:,
    'GSR'] = 'CVX wam up'  # Todo: question: should we add a new column?
    # replace column string name by 'gsr' for lisibility purpose
    signals.columns = signals.columns.str.replace(column, 'GSR')

    return signals, annotations


def galvanic_scrpeaks(signals, annotations, column='GSR_SCR', peaks_kwargs=None, max_increase_duration=7):
    """ Detect peaks of SCR component and estimate their characteristics.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the deconvoluted GSR in channel given by column_name.
    column: str | None
        Name of column where the data of interest are located.
        If None, the first column is considered.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    peaks_kwargs:
        Keywords arguments to detect peaks and define their characteristics.
    max_increase_duration:
        Maximum duration for the peak to rise

    Returns
    -------
     data : pd.DataFrame
            Dataframe with columns: ['SCR', 'SCR_peaks_detected', 'SCR_peaks_increase-duration',
                                'SCR_peaks_increase-amplitude',
                                'SCR_peaks_recovery-duration', 'bad']

    Examples
    --------

      .. image:: ../source/_static/examples/galvanic_functions/io_scrpeaks.png


    """
    # Define the scaler to apply before detecting peaks
    scaler = RobustScaler(with_centering=False, quantile_range=(5, 95.0))
    # Detect peaks and estimate their properties
    data = detect_peaks(signals, column=column, estimate_properties=True, scaler=scaler, **peaks_kwargs)

    data = data[data.label == 'peak'].loc[:,
           ['value', 'left_local', 'left_prominence', 'right_ips']]
    # Rename columns for lisibility purposes
    data = data.rename(
        columns={
            'value': column + '_peaks_value',
            'left_local': column + '_peaks_increase-duration',
            'left_prominence': column + '_peaks_increase-amplitude',
            'right_ips': column + '_peaks_recovery-duration'
        })

    # Append the 'bad' column from input data
    # data.loc[:, 'bad'] = bad
    # Update the bad column with this new kind of artifact, being false peak detection
    # (when thee increase duration is greater than the prominence window,
    # it means no local minima has been found, hence the peak was not significant)
    annotations = pd.DataFrame(index=data.index, columns=data.columns)
    false_detections = (data[column + '_peaks_increase-duration'] >= max_increase_duration).values
    annotations.loc[false_detections, :] = 'false_peak_detection'
    # To ease the extraction of peak rate, let's add a column with boolean values
    # True if the peak is kept, False if not.
    data.loc[false_detections, :] = np.NaN

    return data, annotations


from dataclasses import dataclass, field


# Galvanic features
# -----------------
@dataclass
class SCRFeatures:
    SCRamplitude: float = field(default=np.nan,
                                metadata={'doc': 'Mean amplitude of SCR component', 'units': 'au'})
    SCRincrease: float = field(default=np.nan,
                               metadata={'doc': 'Increase duration of SCR component', 'units': 's'})
    SCRdecrease: float = field(default=np.nan,
                               metadata={'doc': 'Recovery duration of SCR component', 'units': 's'})
    SCRrate: float = field(default=np.nan,
                           metadata={'doc': 'Number of SCR peaks divided by duration', 'units': 'peaks/s'})


@dataclass
class SCLFeatures:
    SCLmean: float = field(default=np.nan,
                           metadata={'doc': 'Mean of SCL component', 'units': 'su'})
    SCLmedian: float = field(default=np.nan,
                             metadata={'doc': 'Median of SCL component', 'units': 'su'})
    SCLsd: float = field(default=np.nan,
                         metadata={'doc': 'Standard deviation of SCL component', 'units': 'su'})
    SCLauc: float = field(default=np.nan,
                          metadata={'doc': 'Area Under Curve divided by duration of SCL component', 'units': 'su/s'})
    SCLslope: float = field(default=np.nan,
                            metadata={'doc': 'Slope from linear regression on SCL component', 'units': 'su'})
    SCLintercept: float = field(default=np.nan,
                                metadata={'doc': 'Intercept from linear regression on SCL component', 'units': 'su'})
    SCLr: float = field(default=np.nan,
                        metadata={'doc': 'R coefficient from linear regression on SCL component', 'units': 'su'})


# @dataclass
# class HRVFrequencyFeatures:
#     VLF: float = np.nan
#     LF: float = np.nan
#     HF: float = np.nan
#     VHF: float = np.nan
#     LFHF: float = np.nan


def linear_regression(y, x):
    y = np.asarray(y)
    x = np.asarray(x)

    rlm = sm.RLM(y, sm.tools.add_constant(x), M=sm.robust.norms.HuberT())
    results = rlm.fit(conv='coefs', tol=1e-3)
    logger.debug('Linear regression results:\n%s', results.summary())

    intercept, slope = results.params
    _, pvalue = results.pvalues  # p-value Wald test of intercept and slope
    r = np.corrcoef(x, y)[0, 1]
    ss_res = np.sum(results.resid ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    return slope, intercept, r, r2, pvalue


def scl_features(scl: pd.Series) -> SCLFeatures:
    features = SCLFeatures()

    # drop NaN
    scl = scl.dropna()

    if scl.empty:
        logger.warning('Not enough SCL samples to calculate SCL features, '
                       'returning nan for all features')
        return features

    period_mins = (scl.index[-1] - scl.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating time features on %.1f minutes of SCL data', period_mins)

    features.SCLmean = np.mean(scl)
    features.SCLmedian = np.median(scl)
    features.SCLsd = np.std(scl)

    # convert datetime index into floats
    scl.index -= scl.index[0]
    scl.index /= np.timedelta64(1, 's')

    x = scl.index
    y = scl.values.astype(float)

    features.SCLauc = auc(y=y, x=x) / period_mins
    features.SCLslope, features.SCLintercept, features.SCLr, _, _ = linear_regression(y, x)

    logger.debug('SCL features: %s', features)
    return features


def scr_features(scr: pd.Series, peaks: pd.DataFrame) -> SCRFeatures:
    features = SCRFeatures()

    # drop NaN
    scr = scr.dropna()

    if scr.empty:
        logger.warning('Not enough SCR samples to calculate SCL features, '
                       'returning nan for all features')
        return features

    # drop NaN
    peaks = peaks.dropna()

    if peaks.empty:
        # just means that there were no SCR peaks, return 0 to all features
        features.SCRamplitude = features.SCRincrease = features.SCRdecrease = features.SCRrate = 0.
        return features

    period_mins = (scr.index[-1] - scr.index[0]) / np.timedelta64(60, 's')
    logger.debug('Calculating peak features on %.1f minutes of SCR data', period_mins)

    features.SCRamplitude = np.mean(peaks['GSR_SCR_peaks_increase-amplitude'])
    features.SCRincrease = np.mean(peaks['GSR_SCR_peaks_increase-duration'])
    features.SCRdecrease = np.mean(peaks['GSR_SCR_peaks_recovery-duration'])
    features.SCRrate = len(peaks) / period_mins

    logger.debug('SCR features: %s', features)
    return features


from iguazu.functions.unity import VALID_SEQUENCE_KEYS


def gsr_features(cvx, peaks, events, known_sequences=None):
    known_sequences = known_sequences or VALID_SEQUENCE_KEYS

    features = []
    # for name, row in events.T.iterrows():  # transpose due to https://github.com/OpenMindInnovation/iguazu/issues/54
    for index, row in events.iterrows():
        logger.debug('Processing sequence %s at %s', row.id, index)
        if row.id not in known_sequences:
            continue

        begin = row.begin
        end = row.end
        cvx_sequence = cvx.loc[begin:end].copy()
        peaks_sequence = peaks.loc[begin:end].copy()

        # extract features on sequence
        scl_features_sequence = scl_features(cvx_sequence.GSR_SCL)
        scr_features_sequence = scr_features(cvx_sequence.GSR_SCR, peaks_sequence)

        all_features = (
            pd.concat([dataclass_to_dataframe(scl_features_sequence),
                       dataclass_to_dataframe(scr_features_sequence)],
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
