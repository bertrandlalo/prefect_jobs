import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

from dsu.pandas_helpers import estimate_rate
import neurokit2 as nk  # todo: add this dependency

from dataclasses import dataclass, field
from iguazu.core.features import dataclass_to_dataframe

from iguazu.functions.unity import VALID_SEQUENCE_KEYS


class NoRespirationPeaks(Exception):
    pass

# Respiration features
# --------------------
@dataclass
class PZTFeatures:
    AMPmean: float = field(default=np.nan,
                           metadata={'doc': 'Mean respiratory amplitude', 'units': 'au'})
    AMPmax: float = field(default=np.nan,
                          metadata={'doc': 'Max respiratory amplitude', 'units': 'au'})
    AMPmin: float = field(default=np.nan,
                          metadata={'doc': 'Min respiratory amplitude', 'units': 'au'})
    AMPsd: float = field(default=np.nan,
                         metadata={'doc': 'Standard Deviation respiratory amplitude', 'units': 'au'})

    PERIODmean: float = field(default=np.nan,
                              metadata={'doc': 'Mean respiratory cycle duration', 'units': 's'})
    PERIODsd: float = field(default=np.nan,
                            metadata={'doc': 'Standard Deviation of respiratory cycle duration', 'units': 's'})
    INSPImean: float = field(default=np.nan,
                             metadata={'doc': 'Mean respiratory inspiration duration', 'units': 's'})
    EXPImean: float = field(default=np.nan,
                            metadata={'doc': 'Mean respiratory expiration duration', 'units': 's'})
    IEmean: float = field(default=np.nan,
                          metadata={'doc': 'Mean ratio between inspiration and expiration durations', 'units': 'au'})


def respiration_clean(data, column='PZT'):
    '''
    # todo: does this function belong to dsu?
    Parameters
    ----------
    data
    column

    Returns
    -------

    '''
    sampling_rate = estimate_rate(data)
    data.loc[:, column] = nk.rsp_clean(data[column], sampling_rate, method='BioSPPy')
    return data


def respiration_sequence_features(data, events, column='PZT', known_sequences=None):
    # nk.rsp_peaks(pzt_signal['PZT'].values, sampling_rate=sampling_rate, method="BioSPPy")

    sampling_rate = estimate_rate(data)

    # Extract peak using neurokit BioSPPy method
    _index = data.index
    _, info = nk.rsp_peaks(data[column], sampling_rate=sampling_rate, method="BioSPPy")
    # Truncate so that first and last events are troughs
    RSP_Troughs = info['RSP_Troughs']
    RSP_Peaks = info['RSP_Peaks']
    # at this point, check that there are some peaks/trough
    if RSP_Troughs.size == 0 or RSP_Peaks.size == 0:
        raise NoRespirationPeaks('No peaks/trough could be detected in PZT signal. ')

    RSP_Peaks = RSP_Peaks[(RSP_Peaks > RSP_Troughs[0]) & (RSP_Peaks <= RSP_Troughs[-1])]

    # Estimate Inspiration and Expiration durations, cycle (I+E) durations and amplitude
    I_duration = (RSP_Peaks - RSP_Troughs[:-1]) / sampling_rate
    E_duration = (RSP_Troughs[1:] - RSP_Peaks) / sampling_rate
    IE_duration = np.ediff1d(RSP_Troughs) / sampling_rate
    amplitude = data.iloc[RSP_Peaks].values - data.iloc[RSP_Troughs[:-1]].values
    IE_ratio = I_duration / E_duration

    # Back to Dataframe format to allow extracting feature between events
    I_duration_df = pd.DataFrame(index=_index[RSP_Peaks], columns=['I_duration'], data=I_duration)
    E_duration_df = pd.DataFrame(index=_index[RSP_Troughs[1:]], columns=['E_duration'], data=E_duration)
    IE_duration_df = pd.DataFrame(index=_index[RSP_Troughs[1:]], columns=['IE_duration'], data=IE_duration)
    amplitude_df = pd.DataFrame(index=_index[RSP_Peaks], columns=['IE_amplitude'], data=amplitude)
    IE_ratio_df = pd.DataFrame(index=_index[RSP_Peaks], columns=['IE_ratio'], data=IE_ratio)

    cycles_df = pd.concat([I_duration_df, E_duration_df, IE_duration_df, amplitude_df, IE_ratio_df], axis=1)

    known_sequences = known_sequences or VALID_SEQUENCE_KEYS

    features = []
    # for name, row in events.T.iterrows():  # transpose due to https://github.com/OpenMindInnovation/iguazu/issues/54
    for index, row in events.iterrows():
        logger.debug('Processing sequence %s at %s', row.id, index)
        if row.id not in known_sequences:
            continue

        begin = row.begin
        end = row.end
        cycles_sequence = cycles_df.loc[begin:end].copy()

        # extract features on sequence
        sequence_features = dataclass_to_dataframe(respiration_features(cycles_sequence)).rename_axis(
            index='id').reset_index()

        sequence_features.insert(0, 'reference', row.id)
        features.append(sequence_features)

    if len(features) > 0:
        features = pd.concat(features, axis='index', ignore_index=True, sort=False)
        logger.info('Generated a feature dataframe of shape %s', features.shape)
    else:
        logger.info('No features were generated')
        features = pd.DataFrame(columns=['id', 'reference', 'value'])

    return features


def respiration_features(data):
    features = PZTFeatures()

    # amplitude characteristics
    amplitude = data.IE_amplitude.dropna()
    if not amplitude.empty:
        features.AMPmean = amplitude.mean()
        features.AMPmax = amplitude.max()
        features.AMPmin = amplitude.min()
        features.AMPsd = amplitude.std()
    # inspiration duration
    i_duration = data.I_duration.dropna()
    if not i_duration.empty:
        features.INSPImean = i_duration.mean()
    # expiration duration
    e_duration = data.E_duration.dropna()
    if not e_duration.empty:
        features.EXPImean = e_duration.mean()
    ie_duration = data.IE_duration.dropna()

    # I/E ratio
    ie_ratio = data.IE_ratio.dropna()
    if not ie_ratio.empty:
        features.IEmean = ie_ratio.mean()

    # respiration average cycle
    if not ie_duration.empty:
        features.PERIODmean = ie_duration.mean()
        features.PERIODsd = ie_duration.std()
    return features
