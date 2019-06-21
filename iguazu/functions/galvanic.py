import pandas as pd
import numpy as np
from datascience_utils.signal_quality import label_bad_from_amplitude
from datascience_utils.filters import scipy_filter_signal, scipy_scale_signal
from datascience_utils.cvxEDA import apply_cvxEDA
from datascience_utils.peaks import OfflinePeak
from sklearn.preprocessing import RobustScaler


def galvanic_clean(data, events, column, warmup_duration, glitch_kwargs, interpolation_kwargs, filter_kwargs,
                   scaling_kwargs, corrupted_maxratio):
    """
     Preprocess the galvanic data and detect bad quality samples.
     It should be noted that some steps here are specific to the device we use, ie. Nexus from MindMedia.
     Eg. When the amplifier saturates (ie. Voltage above 2V, ie. resistance too low), Nexus will return 0.0, but other
     devices might have different behaviors.

    The pipeline will:

        - detect bad samples calling :py:func:dsu.quality.detect_bad_from_amplitude with `glitch_kwargs`
        - remove the bad samples and evaluate the corruption ratio. If too high, then raise an error.
        - interpolate the missing signal e calling :py:meth:pandas.Series.interpolat with `interpolation_kwargs`.
        - inverse the signal to access galvanic conductance (G=1/R)
        - lowpass the resulting signal using :py:func:dsu.filters.dsp.bandpass_signal with `filter_kwargs`
        - scale the signal on the whole session using using :py:func:dsu.filters.dsp.scale_signal with `scaling_kwargs`

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the raw GSR in channel given by column_name.
    events: pd.DataFrame
        Dataframe with 2 columns: [label, data], containing string labels and serialized meta giving the context of the labels.
    column: str
        Name of column where the data of interest are located.
    warmup_duration: float
        Duration (in s) to select before and after the vr session (to avoid side effects in the future
    processing steps, ie. that we can then set to bad ).
    glitch_kwargs:
        Kkeywords arguments to detect bad samples.
    interpolation_kwargs:
        Keywords arguments to interpolate the missing (bad) samples.
    filter_kwargs:
        Keywords arguments to lowpass the data.
    scaling_kwargs:
        Keywords arguments to scale the data.
    corrupted_maxratio: float
        Maximum acceptable ratio of corrupted (bad) samples.

    Returns
    -------
    data: pd.DataFrame
          Dataframe with columns 'F', 'F_clean', 'F_clean_inversed', 'F_clean_inversed_lowpassed', 'F_clean_inversed_lowpassed_zscored', 'bad'

    Examples
    --------

        .. image:: ../source/_static/examples/galvanic_functions/io_clean.png

    """
    assert events.index.is_monotonic  # TODO: think about raising an exception here

    begins = events.index[0] - np.timedelta64(1, 's') * warmup_duration  # begin 30 seconds before the beginning of the session
    ends = events.index[-1] + np.timedelta64(1, 's') * warmup_duration  # end 30 seconds after the beginning of the session


    # troncate dataframe on session times
    data = data[begins:ends]
    data = data.loc[:, [column]]

    # label 0.0 values as bad
    data.loc[data.loc[:, column] == 0.0, "bad"] = True

    # add a column "bad" with rejection boolean on amplitude criteria
    label_bad_from_amplitude(data, column_name=column, output_column="bad", inplace=True,
                             **glitch_kwargs)



    # make a copy of the signal with suffix "_clean", mask bad samples
    data_clean = data[[column]].copy().add_suffix('_clean')
    data_clean.mask(data.bad, inplace=True)

    # estimate the corrupted ratio
    # if too many samples were dropped, raise an error
    corrupted_ratio = data.bad.mean()
    if corrupted_ratio > corrupted_maxratio:
        raise Exception("AO saturation of {corrupted_ratio} exceeds {maxratio}.".format(corrupted_ratio=corrupted_ratio, maxratio=corrupted_maxratio))

    # interpolate the signal
    begins = data_clean.first_valid_index()
    ends = data_clean.last_valid_index()
    data_clean = data_clean[begins:ends]

    # take inverse to have the SKIN CONDUCTANCE G = 1/R = I/U
    data_clean_inversed = 1 / data_clean.copy().add_suffix("_inversed")


    data_clean_inversed.interpolate(**interpolation_kwargs, inplace=True)

    # lowpass filter signal
    scipy_filter_signal(data_clean_inversed, columns=[column + "_clean_inversed"], btype='lowpass',
                        **filter_kwargs, suffix="lowpassed", inplace=True)

    # scale signal on the all session
    scipy_scale_signal(data_clean_inversed, columns=[column + "_clean_inversed_lowpassed"], suffix="zscored",
                       inplace=True, **scaling_kwargs)

    # return preprocessed data
    data = pd.concat([data, data_clean, data_clean_inversed], axis=1)
    return data

def galvanic_cvx(data, column, warmup_duration, glitch_params, cvxeda_params=None):
    """ Separate phasic (SCR) and tonic (SCL) galvanic components using a convexe deconvolution.

    Parameters
    ----------
    data: pd.ataFrame
        Dataframe containing the preprocessed GSR in channel given by column_name.
    column: str
        Name of column where the data of interest are located.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    glitch_params:
        Keywords arguments to detect bad samples.
    cvxeda_params:
        Keywords arguments to apply cvxEDA algorithm.

    Returns
    -------
    data: pd.DataFrame
          Dataframe with columns: ['F_clean_inversed_lowpassed_zscored_SCR', 'F_clean_inversed_lowpassed_zscored°SCL', 'bad']

    Examples
    --------

      .. image:: ../source/_static/examples/galvanic_functions/io_deconvolution.png

    """
    cvxeda_params = cvxeda_params or {}
    # extract SCR and SCL component using deconvolution toolbox cvxEDA

    data = apply_cvxEDA(data[[column]].dropna(), column_name=column, kwargs=cvxeda_params)

    # add a column "bad" with rejection boolean on amplitude criteria
    label_bad_from_amplitude(data, column_name=column + "_SCR",
                             output_column="bad", inplace=True, **glitch_params)
    # set warmup period to "bad"
    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')
    # TODO: this does not do what it's supposed to do; it should be a slice!
    data.loc[:data.index[0] + warm_up_timedelta, "bad"] = True
    data.loc[data.index[-1] - warm_up_timedelta:, "bad"] = True
    return data


def galvanic_scrpeaks(data, column, warmup_duration, peaks_kwargs, glitch_kwargs):
    """ Detect peaks of SCR component and estimate their characteristics.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe containing the deconvoluted GSR in channel given by column_name.
    column: str
        Name of column where the data of interest are located.
    warmup_duration: float
        Duration at beginning and end of the data to label as 'bad'==True.
    peaks_kwargs:
        Keywords arguments to detect peaks and define their characteristics.
    glitch_kwargs:
        Keywords arguments to detect false detected peaks.

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
    warm_up_timedelta = warmup_duration * np.timedelta64(1, 's')
    data = data.loc[:, [column]]
    data = data[data.index[0]+warm_up_timedelta:data.index[-1]-warm_up_timedelta]
    data.columns = ["SCR"]  # rename the column for simplicity purpose
    scaler = RobustScaler(with_centering=True, quantile_range=(5, 95.0))
    peakdetector = OfflinePeak(data, column_name="SCR", scaler=scaler, **peaks_kwargs)
    peakdetector.simulation()

    data = peakdetector._data.loc[:,
                       ['SCR', 'peaks', 'peaks_left_locals', 'peaks_left_prominences', 'peaks_width_heights']].loc[
                       peakdetector.peaks[0], :]
    data.columns = ['SCR', 'SCR_peaks_detected', 'SCR_peaks_increase-duration',
                                'SCR_peaks_increase-amplitude',
                                'SCR_peaks_recovery-duration']

    label_bad_from_amplitude(data, column_name="SCR_peaks_increase-duration", output_column="bad",
                             inplace=True, **glitch_kwargs)
    return data
