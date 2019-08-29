import logging

import numpy as np
import pandas as pd
from dsu.pandas_helpers import estimate_rate
from scipy.integrate import simps
from scipy.signal.spectral import _spectral_helper


logger = logging.getLogger(__name__)


def bandpower(data, bands, epoch_size, epoch_overlap, relative=False): #, log=False):

    fs = int(estimate_rate(data))
    logger.debug('Calculating spectra with fs=%dHz on data shaped as %s',
                 fs, data.shape)

    x = data.values.T
    nperseg = epoch_size * fs
    noverlap = epoch_overlap * fs
    freqs, t, psd = _spectral_helper(x, x, fs=fs, window='hann',
                                     nperseg=nperseg, noverlap=noverlap,
                                     detrend='constant', return_onesided=True,
                                     scaling='density', mode='psd')  # TODO: psd or stft ???
    # To whom it may concern: according to the _spectral_helper code, the
    # difference between scaling='density' and 'spectrum' is just how the
    # window adjusts the final value. One uses the sum of squared values, the
    # other the square of the sum. The 'density' also divides by the fs (which
    # is why the units change to V^2 / Hz).
    # In my opinion, this is not very important as long as we are consistent
    index = data.index[0] + pd.to_timedelta(t, unit='s')
    n = index.shape[0]

    powers = []
    for name, (f_start, f_stop) in bands.items():
        f_start = f_start or 0
        f_stop = f_stop or fs / 2
        idx = (freqs >= f_start) & (freqs < f_stop)
        if idx.sum() == 0:
            logger.warning('Band %s is empty for fs=%d and nperseg=%d',
                           name, fs, nperseg)
            result = pd.DataFrame(data=[[np.nan] * len(data.columns)] * n,
                                  columns=data.columns,
                                  index=index)
        else:
            logger.debug('Calculating band power for %s with %d bins',
                         name, idx.sum())
            # pxx axes: (column, freq, time)
            # bp = psd[:, idx, :].sum(axis=1)
            bp = simps(psd[:, idx, :], freqs[idx], axis=1)

            if relative:
                bp /= simps(psd, freqs, axis=1)

            # power_sum axes: (column, time)
            result = pd.DataFrame(data=bp.T,  # (time, column)
                                  columns=data.columns,
                                  index=index)

        powers.append(result.add_suffix(f'_{name}'))

    return pd.concat(powers, axis='columns')
