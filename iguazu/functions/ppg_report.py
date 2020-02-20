import collections
import logging
import io
from base64 import b64encode

import matplotlib.dates
import matplotlib.pyplot as plt
import numpy as np
import pendulum
import plotly.express
import plotly.graph_objects as go
import plotly.offline
import scipy.signal
from jinja2 import Environment, PackageLoader, select_autoescape

from iguazu import __version__


logger = logging.getLogger(__name__)


def render_ppg_report(raw, clean, rr, rri,
                      raw_metadata, clean_metadata, rr_metadata, rri_metadata,
                      *,
                      tz='Europe/Paris', fs=1,
                      preview_start=0, preview_length=30):

    env = Environment(
        loader=PackageLoader('iguazu', 'functions/templates'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('ppg-report.html')

    base_metadata = raw_metadata.get('base', {})
    details = (
        f'Filename: {base_metadata.get("filename", None)}'
    )

    # Signal plot variables for the template
    preview = raw_plot = pre_plot = rr_plot = None
    preview_problems = raw_plot_problems = pre_plot_problems = rr_plot_problems = dict()
    # Spectral plot variables for the template
    raw_spectrum_plot = pre_spectrum_plot = rri_spectrum_plot = None
    raw_spectrum_plot_problems = pre_spectrum_plot_problems = rri_spectrum_plot_problems = dict()

    with plt.style.context('ggplot'):  # make the signal preview look like ggplot

        # Preview plot
        try:
            preview = make_signal_preview(raw, rri, alt='PPG preview')
        except Exception as ex:
            preview_problems = _build_problem(raw_metadata, ex)

        # Signal plots: show only the first `preview_secs` seconds
        ix = np.arange(preview_start * fs, (preview_start + preview_length) * fs, dtype=int)
        try:
            raw_plot = make_interactive_signal_plot(raw.iloc[ix]) or raw_metadata
        except Exception as ex:
            raw_plot_problems = _build_problem(raw_metadata, ex)
        try:
            idx = clean.iloc[ix].index
            pre_plot = make_interactive_annotated_plot(raw.iloc[ix],
                                                       clean.loc[idx],
                                                       rr)
        except Exception as ex:
            pre_plot_problems = _build_problem((raw_metadata, clean_metadata, rr_metadata),
                                               ex)
        try:
            rr_plot = make_interactive_rr_plot(rr, rri.loc[idx])
        except Exception as ex:
            rr_plot_problems = _build_problem((rr_metadata, rri_metadata),
                                              ex)

        # Spectra plots use all data for a welch estimation
        try:
            raw_spectrum_plot = make_interactive_spectrum_plot(raw, fs)
        except Exception as ex:
            raw_spectrum_plot_problems = _build_problem(raw_metadata, ex)
        try:
            pre_spectrum_plot = make_interactive_spectrum_plot((raw, clean), fs)
        except Exception as ex:
            pre_spectrum_plot_problems = _build_problem((raw_metadata, clean_metadata),
                                                        ex)
        try:
            rri_spectrum_plot = make_interactive_cardiac_spectrum_plot(rri, fs, nperseg=fs*60, noverlap=fs)
        except Exception as ex:
            rri_spectrum_plot_problems = _build_problem(rri_metadata, ex)

    html = template.render(
        # details
        file_details=details,
        # signals
        preview=preview,
        preview_problems=preview_problems,
        raw_plot=raw_plot,
        raw_plot_problems=raw_plot_problems,
        preprocessed_signal_plot=pre_plot,
        preprocessed_signal_plot_problems=pre_plot_problems,
        rr_signal_plot=rr_plot,
        rr_signal_plot_problems=rr_plot_problems,
        # spectra
        raw_spectrum_plot=raw_spectrum_plot,
        raw_spectrum_plot_problems=raw_spectrum_plot_problems,
        preprocessed_spectrum_plot=pre_spectrum_plot,
        preprocessed_spectrum_plot_problems=pre_spectrum_plot_problems,
        rri_spectrum_plot=rri_spectrum_plot,
        rri_spectrum_plot_problems=rri_spectrum_plot_problems,
        # misc
        generator=f'Iguazu version {__version__}',
        date=pendulum.now(tz).to_day_datetime_string() + f' ({tz})',
    )
    return html


def _build_problem(references, exception):
    if references is None:
        references = []
    elif not isinstance(references, collections.Sequence):
        references = (references, )

    problem = dict()
    problem['type'] = exception.__class__.__name__
    problem['details'] = str(exception)
    for ref in references:
        if 'problem' in ref:
            problem.update(ref['problem'] or {})
            if 'status' in ref:
                problem['status'] = ref['status']
            break
    return problem


def make_signal_preview(raw, rri, width=1500, height=300, alt='preview'):
    # Handle a FutureWarning on pandas automatic datetime conversion
    from pandas.plotting import register_matplotlib_converters
    register_matplotlib_converters()

    dpi = plt.rcParams['figure.dpi']

    fig = plt.figure(figsize=(width / dpi, height / dpi))
    ax_rri = plt.gca()
    ax_raw = ax_rri.twinx()
    ax_secs = ax_rri.twiny()

    lines1 = lines2 = []
    xmin = xmax = xptp_secs = 0
    if not raw.empty:
        lines1 = ax_raw.plot(raw, color='C0', alpha=0.9, label='Raw signal')
        xmin, xmax = min(raw.index), max(raw.index)
        xptp_secs = (xmax - xmin).total_seconds()
    if not rri.empty:
        lines2 = ax_rri.plot(rri, color='C1', alpha=0.9, label='Interpolated RR')

    # Axes adjustments
    ax_rri.grid(True)
    ax_raw.grid(False)
    ax_secs.grid(False)
    ax_rri.set_xlim(xmin, xmax)
    ax_rri.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
    ax_rri.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(interval=2))
    ax_secs.set_xlim(0, xptp_secs)
    ax_secs.set_xticks(np.arange(0, xptp_secs, 60).astype(int))
    ax_secs.set_xticklabels(np.arange(0, xptp_secs, 60).astype(int), rotation='vertical')

    ax_rri.set_xlabel('Timestamp')
    ax_rri.set_ylabel('msecs', color='C1')
    ax_rri.tick_params(axis='y', colors='C1')
    ax_raw.set_ylabel('mV', color='C0')
    ax_raw.tick_params(axis='y', colors='C0')
    ax_secs.set_xlabel('Time (seconds, relative to start)')
    fig.subplots_adjust(bottom=0.2, top=0.7)

    lines = lines1 + lines2
    labels = [l.get_label() for l in lines]
    ax_raw.legend(lines, labels, loc='upper right', facecolor='white')

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=dpi)

    image = b64encode(buffer.getbuffer()).decode('ascii')
    return f'<img alt="{alt}"' \
           f' src="data:image/png;base64,{image}"/>'


def make_interactive_signal_plot(dataframe, index=None, render=True):
    if index is not None:
        dataframe = dataframe.loc[index]

    fig = go.Figure()

    # Borrow colors from matplotlib default cycle
    color_cycler = plt.rcParams['axes.prop_cycle']()

    for column in dataframe:
        color = next(color_cycler)['color']
        fig.add_trace(
            go.Scatter(x=dataframe.index, y=dataframe[column], name=column, mode='lines',
                       line=dict(color=color))
        )

    if render:
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                x=0.8,
                y=0.9,
            ),
        )
        fig.update_xaxes(range=[dataframe.index[0], dataframe.index[-1]])
        div = plotly.offline.plot(fig, output_type='div',
                                  include_plotlyjs=False)

        return div

    return fig


def make_interactive_rr_plot(rr, rri):
    fig = go.Figure()

    # Borrow colors from matplotlib default cycle
    color_cycler = plt.rcParams['axes.prop_cycle']()

    # Now show RR peaks, but only on the time domain of interest
    idx = rr.loc[(rr.index >= rri.index[0]) & (rr.index <= rri.index[-1])].index
    rr = rr.loc[idx]
    rr['cdetails'] = rr['details'].astype('category')

    color = next(color_cycler)['color']
    fig.add_trace(
        go.Scatter(x=rri.index, y=np.ravel(rri.values), name='RRi', mode='lines',
                   line=dict(color=color), hoverinfo='none')
    )

    color = next(color_cycler)['color']
    fig.add_trace(
        # go.Scatter(x=rr.index, y=np.ravel(rr.values), name='RR', mode='markers',
        #            marker=dict(color=color))
        go.Scatter(x=rr.index, y=rr.RR, text=rr.details,
                   name='RR', mode='markers',
                   marker=dict(color=rr.cdetails.cat.codes,
                               colorscale=plotly.express.colors.qualitative.T10)),
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            x=0.8,
            y=0.9,
        ),
    )
    fig.update_xaxes(range=[rri.index[0], rri.index[-1]])
    div = plotly.offline.plot(fig, output_type='div',
                              include_plotlyjs=False)

    return div


def make_interactive_annotated_plot(raw, preprocessed, rr):
    fig = go.Figure()

    if raw.shape[1] != 1:
        raise ValueError('Expected only one column on raw signal')
    if preprocessed.shape[1] != 1:
        raise ValueError('Expected only one column on preprocessed signal')

    #df = pd.merge(raw, preprocessed, left_index=True, right_index=True)
    #fig = make_interactive_signal_plot(df, render=False)

    # Borrow colors from matplotlib default cycle
    color_cycler = plt.rcParams['axes.prop_cycle']()

    color = next(color_cycler)['color']
    fig.add_trace(
        go.Scatter(x=raw.index, y=np.ravel(raw.values),
                   name='Raw signal', mode='lines',
                   line=dict(color=color))
    )

    color = next(color_cycler)['color']
    fig.add_trace(
        go.Scatter(x=preprocessed.index, y=np.ravel(preprocessed.values),
                   name='Preprocessed signal', mode='lines',
                   line=dict(color=color))
    )

    # Now show RR peaks, but only on the time domain of interest
    idx = rr.loc[(rr.index >= raw.index[0]) & (rr.index <= raw.index[-1])].index

    # Plotly is very limited for some plot use-cases. One of these are
    # plt.axvlines. This is a workaround using shapes and layout:
    shapes = []
    for i, row in rr.loc[idx].iterrows():
        if row.bad:
            color = 'red'
        else:
            color = 'blue'
        shapes.append(dict(
            type='line', xref='x', yref='paper',
            x0=i, y0=0,
            x1=i, y1=1,
            opacity=0.33,
            line=dict(color=color),
        ))

    fig.update_layout(
        shapes=shapes,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            x=0.8,
            y=0.9,
        ),
    )
    fig.update_xaxes(range=[idx[0], idx[-1]])
    div = plotly.offline.plot(fig, output_type='div',
                              include_plotlyjs=False)

    return div


def make_interactive_spectrum_plot(dataframes, fs=1.0, render=True, **kwargs):
    go = plotly.graph_objects

    if not isinstance(dataframes, (list, tuple)):
        dataframes = (dataframes, )

    fsi = int(fs)
    fig = go.Figure()

    # Borrow colors from matplotlib default cycle
    color_cycler = plt.rcParams['axes.prop_cycle']()

    for df in dataframes:
        x = np.asarray(df.values)
        if x.ndim == 1:
            x = x[:, np.newaxis]

        kwargs.setdefault('nperseg', fsi*4)
        kwargs.setdefault('noverlap', fsi//4)
        freqs, pxx = scipy.signal.welch(x, fs=fs, window='hann', scaling='density', axis=0,
                                        **kwargs)

        for i, column in enumerate(df):
            color = next(color_cycler)['color']
            fig.add_trace(
                go.Scatter(x=freqs, y=pxx[:, i], mode='lines', name=column,
                           line=dict(color=color))
            )

    if render:
        fig.update_layout(
            yaxis_type='log',
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
                x=0.5,
                y=0.9,
            ),
        )
        div = plotly.offline.plot(fig, output_type='div',
                                  include_plotlyjs=False)

        return div

    return fig


def make_interactive_cardiac_spectrum_plot(dataframe, fs=1.0, **kwargs):
    go = plotly.graph_objects

    kwargs.pop('render', None)
    fig = make_interactive_spectrum_plot(dataframe, fs=fs, render=False, **kwargs)

    # Frequency bands according to neurokit
    freq_bands = {
        #"ULF": [0.0001, 0.0033],   # Removed due to how small it is
        "VLF": [0.0033, 0.04],
        "LF": [0.04, 0.15],
        "HF": [0.15, 0.40],
        "VHF": [0.4, 0.5]
    }

    # Borrow colors from matplotlib default cycle
    color_cycler = plt.rcParams['axes.prop_cycle']()

    # Plotly is very limited for some plot use-cases. One of these are
    # plt.axvlines. This is a workaround using shapes and layout:
    shapes = []
    annotations = []
    for band, (left, right) in freq_bands.items():
        color = next(color_cycler)['color']
        shapes.append(dict(
            type='rect', xref='x', yref='paper',
            x0=left, y0=0,
            x1=right, y1=1,
            fillcolor=color,
            opacity=0.25,
            line=dict(width=0),
        ))
        annotations.append(go.layout.Annotation(
            xref='x', yref='paper',
            x=(left + right) / 2,
            y=0,
            text=band,
            showarrow=False,
            font=dict(color=color),
        ))

    fig.update_layout(
        annotations=annotations,
        shapes=shapes,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            x=0.8,
            y=0.9,
        ),
        xaxis=dict(autorange=False, range=[0, 0.5])
    )
    div = plotly.offline.plot(fig, output_type='div',
                              include_plotlyjs=False)

    return div

#
# if __name__ == '__main__':
#     from scipy.misc import electrocardiogram
#     from scipy.signal import find_peaks
#
#     signal = electrocardiogram()
#     signal = pd.DataFrame({'ppg': signal},
#                           index=np.arange(0, signal.shape[0]) / 360)
#     signal['ppg_filtered'] = signal.rolling(36)['ppg'].mean().fillna(0)
#     signal['time'] = signal.index
#
#     idx_peaks, _ = find_peaks(signal['ppg_filtered'], distance=360 // 2)
#     rr_ = (
#         pd.DataFrame(data={'rr': signal.iloc[idx_peaks].index},
#                      index=signal.iloc[idx_peaks].index)
#         .diff().dropna()
#     )
#     rr_ *= 1000
#
#     rri_ = pd.DataFrame(index=signal.index)
#     rri_['RRi'] = rr_['rr']
#     rri_ = rri_.interpolate(method='pchip').dropna()
#
#     report = render_ppg_report(signal, signal, rr_, rri_, preview_samples=360*30)
#
#     with open('ppg_report_dev.html', 'w') as f:
#         f.write(report)
