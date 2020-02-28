import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

from dsu.pandas_helpers import estimate_rate
import neurokit2 as nk  # todo: add this dependency

from dataclasses import dataclass, field
from iguazu.core.features import dataclass_to_dataframe

from iguazu.functions.unity import VALID_SEQUENCE_KEYS


# Respiration features
# --------------------
@dataclass
class PZTFeatures:
    meanPZT: float = field(default=np.nan,
                           metadata={'doc': 'Mean respiratory amplitude', 'units': 'au'})
    maxPZT: float = field(default=np.nan,
                          metadata={'doc': 'Max respiratory amplitude', 'units': 'au'})
    minPZT: float = field(default=np.nan,
                          metadata={'doc': 'Min respiratory amplitude', 'units': 'au'})
    sdPZT: float = field(default=np.nan,
                         metadata={'doc': 'Standard Deviation respiratory amplitude', 'units': 'au'})

    meanPERIOD: float = field(default=np.nan,
                              metadata={'doc': 'Mean respiratory cycle duration', 'units': 'au'})
    sdPERIOD: float = field(default=np.nan,
                            metadata={'doc': 'Standard Deviation of respiratory cycle duration', 'units': 'au'})
    meanI: float = field(default=np.nan,
                         metadata={'doc': 'Mean respiratory inspiration duration', 'units': 'au'})
    meanE: float = field(default=np.nan,
                         metadata={'doc': 'Mean respiratory expiration duration', 'units': 'au'})
    meanIE: float = field(default=np.nan,
                          metadata={'doc': 'Mean ratio between inspiration and expiration durations', 'units': 'au'})


def clean_respiration(data, column='PZT'):
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


def extract_sequence_features(data, events, column='PZT', known_sequences=None):
    # nk.rsp_peaks(pzt_signal['PZT'].values, sampling_rate=sampling_rate, method="BioSPPy")

    sampling_rate = estimate_rate(data)

    # Extract peak using neurokit BioSPPy method
    _index = data.index
    _, info = nk.rsp_peaks(data[column], sampling_rate=sampling_rate, method="BioSPPy")

    # Truncate so that first and last events are troughs
    RSP_Troughs = info['RSP_Troughs']
    RSP_Peaks = info['RSP_Peaks']
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
        import pdb;
        pdb.set_trace()
        sequence_features = dataclass_to_dataframe(extract_features(cycles_sequence)).rename_axis(
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


def extract_features(data):
    features = PZTFeatures()

    # amplitude characteristics
    amplitude = data.IE_amplitude.dropna()
    if not amplitude.empty:
        features.meanPZT = amplitude.mean()
        features.maxPZT = amplitude.max()
        features.minPZT = amplitude.min()
        features.sdPZT = amplitude.std()
    # inspiration duration
    i_duration = data.I_duration.dropna()
    if not i_duration.empty:
        features.meanI = i_duration.mean()
    # expiration duration
    e_duration = data.I_duration.dropna()
    if not e_duration.empty:
        features.meanE = e_duration.mean()
    ie_duration = data.IE_duration.dropna()

    # I/E ratio
    ie_ratio = data.IE_ratio.dropna()
    if not ie_ratio.empty:
        features.meanIE = ie_ratio.mean()

    # respiration average cycle
    if not ie_duration.empty:
        features.meanPERIOD = ie_duration.mean()
        features.sdPERIOD = ie_duration.std()
    return features
