import logging
from typing import List

import pandas as pd
from datascience_utils.unity import fix_unity_events
from dsu.unity import extract_marker_version, extract_complete_sequences, \
    extract_complete_sequence_times
from iguazu.functions.specs import empty_events, sort_standard_events

logger = logging.getLogger(__name__)


# TODO: schema xdf_validation should avoid using this ugly trick.
#       When refactoring and migrating pipeline_hdf to iguazu,
# TODO: we should diagnostic and repair the events based on the schema version.


# This is a protector against corrupted events.
VALID_SEQUENCE_KEYS = (
    "space-stress_game-tutorial_0",
    "space-stress_outro_0",
    "physio-sonification_respiration-feedback_0",
    "intro_calibration_0",
    "common_respiration-calibration_data-accumulation_0",
    "session_sequence_0",
    "physio-sonification_sequence_0",
    "space-stress_game_0",
    "space-stress_game_1",
    "physio-sonification_playground_0",
    "physio-sonification_cardiac-feedback_0",
    "cardiac-coherence_coherence-feedback_0",
    "physio-sonification_survey_0",
    "space-stress_sequence_0",
    "cardiac-coherence_score_0",
    "baseline_sequence_0",
    "baseline_sequence_1",
    "baseline_sequence_2",
    "baseline_sequence_3",
    "space-stress_game_enemy-wave_0",
    "space-stress_game_enemy-wave_1",
    "space-stress_game_enemy-wave_2",
    "space-stress_game_enemy-wave_3",
    "space-stress_game_enemy-wave_4",
    "space-stress_game_enemy-wave_5",
    "baseline_eyes-opened_0",
    "baseline_eyes-opened_1",
    "baseline_eyes-opened_2",
    "baseline_eyes-opened_3",
    "space-stress_breath-tutorial_0",
    "intro_disclaimer_0",
    "lobby_sequence_0",
    "lobby_sequence_1",
    "lobby_sequence_2",
    "physio-sonification_coherence-feedback_0",
    "space-stress_survey_0",
    "space-stress_survey_1",
    "intro_omi-logo_0",
    "cardiac-coherence_sequence_0",
    "intro_sequence_0",
    "cardiac-coherence_survey_0",
    "cardiac-coherence_survey_1",
    "space-stress_graph_0",
    "space-stress_graph_1",
    "space-stress_intro_0",
    "baseline_eyes-closed_0",
    "cardiac-coherence_data-accumulation_0",
)


def extract_sequences(events: pd.DataFrame, sequences: List[str] = None) -> pd.DataFrame:
    """ Extracts the beginning and ends of sequences from a VR session.

    Parameters
    ----------
    events: pd.DataFrame
        Dataframe with a column "label" containing 'begins|ends'.
    sequences: list
        List of strings of (sub-)sequences names to retain in the sequence report.

    Returns
    -------
    report: pd.DataFrame
        Dataframe with index = ["begins", "ends"],
        columns = [sequence-name_xx for sequence in sequences], and
        values are timestamps of beginning and end of the subsequence.

    Examples
    --------
    In this example, we have a unity_events from a VR_session and we want to extract
    timestamps of begining/end of sub-sequences.
    Note that some subsequences may occur more than once, eg: in space-stress game,
    there are 6 waves. Hence, the period names

    >>> events
                                                                     label  ... hed
        2019-03-29 13:36:17+00:00            unity_session_sequence_begins  ...
        2019-03-29 13:36:19.863029298+00:00    unity_intro_sequence_begins  ...
        2019-03-29 13:36:19.863990198+00:00    unity_intro_omi-logo_begins  ...
        2019-03-29 13:36:27.206378694+00:00      unity_intro_omi-logo_ends  ...
        2019-03-29 13:36:27.207482894+00:00  unity_intro_disclaimer_begins  ...
    >>> report = extract_sequences(events, sequences=None)
    >>> report
                 physio-sonification_playground_0  ...          cardiac-coherence_survey_1
        begin 2019-03-29 14:11:34.269554919+00:00  ... 2019-03-29 13:48:34.481497988+00:00
        end   2019-03-29 14:13:27.252203655+00:00  ... 2019-03-29 13:49:28.501953058+00:00

    ToDo: This function only works for post-legacy events.
    """

    if extract_marker_version(events) == 'legacy':
        # TODO: commit, push and PR for the small fix on this function in datascience_utils (dsu?)
        logger.warning('Sequences report for legacy events not yet implemented')
        return pd.DataFrame()

    if 'xdf_timestamps' in events:
        events.drop('xdf_timestamps', axis=1, inplace=True)

    # correct unity events # TODO : put that in the conversion xdf to hdf
    events = fix_unity_events(events)
    sequences_report = extract_complete_sequences(events)
    sequences = sequences or sequences_report
    # intersection between sequences found in events and sequences specified in the parameters
    available_sequences = [sequence for sequence in sequences_report if sequence in sequences]
    if set(available_sequences) != set(sequences):
        logger.warning('Could not find %s in the sequences.',
                       ', '.join([str(a) for a in sequences if a not in available_sequences]))

    sequence_times = {}
    for sequence_name in available_sequences:
        times = extract_complete_sequence_times(events, sequence_name, pedantic='warn')
        for k, (begin, end) in enumerate(times):
            sequence_times[sequence_name + "_" + str(k)] = {'begin': begin, 'end': end}
    # This is a protection against corrupted events, that is, we keep only the sequences keys that are
    # specified in list valid_sequences_keys
    sequence_times = {k: v for (k, v) in sequence_times.items() if k in VALID_SEQUENCE_KEYS}
    report = pd.DataFrame.from_dict(sequence_times)
    return report


def extract_standardized_events(events: pd.DataFrame) -> pd.DataFrame: #selection: List[str] = None) -> pd.DataFrame:
    """ Extract sequences that follow the standard specification

    This function is a wrapper of :py:func:`extract_sequences` that reorders
    the results to meet the
    :ref:`standard event specifications <event_specs>`.

    Parameters
    ----------
    events
        Dataframe with a column "label" containing 'begins|ends'.
        See the documentation of :py:func:`extract_sequences` for more info.

    selection
        List of strings of sequence names to retain.
        See the documentation of :py:func:`extract_sequences` for more info.

    Returns
    -------
    pd.DataFrame
        Dataframe with the sequences according to the
        :ref:`standard event specifications <event_specs>`. That is, with
        a timestamp index and id, name, begin, end and data colunns.

    See Also
    --------
    :ref:`standard event specifications <event_specs>`.
    :py:func:`extract_sequences`.

    """

    marker_version = extract_marker_version(events)
    logger.info('Detected marker version is %s', marker_version)
    if marker_version == 'legacy':
        # TODO: commit, push and PR for the small fix on this function in datascience_utils (dsu?)
        logger.warning('Sequences report for legacy events not implemented yet')
        return empty_events()

    # pyxdf adds a xdf_timestamps in case we one wants to do manual time
    # corrections. We don't need this for the events
    events.drop(columns='xdf_timestamps', inplace=True, errors='ignore')

    # correct unity events # TODO: put this in the conversion xdf to hdf
    events = fix_unity_events(events)
    complete_sequences = extract_complete_sequences(events)

    records = []
    for sequence_name in complete_sequences:
        times = extract_complete_sequence_times(events, sequence_name, pedantic='warn')
        for k, (begin, end) in enumerate(times):
            sequence_id = f'{sequence_name}_{k}'
            if sequence_id not in VALID_SEQUENCE_KEYS:
                # This is a protection against corrupted events, that is, we
                # keep only the sequences keys that are specified in the
                # VALID_SEQUENCE_KEYS list
                logger.debug('Ignoring sequence %s since it is not on the '
                             'valid sequence keys', sequence_id)
                continue
            records.append({
                'timestamp': begin,
                'id': sequence_id,
                'name': sequence_name,
                'begin': begin,
                'end': end,
                'data': None,
            })

    standard_sequences = (
        pd.DataFrame.from_records(records,
                                  # Inform on column names so that the set_index later does not fail
                                  columns=['timestamp', 'id', 'name', 'begin', 'end', 'data'])
        .set_index('timestamp')
        .rename_axis(index='index')
        .sort_index()
    )

    # Convert the existing events to standard form
    standard_events = events.copy()
    standard_events['id'] = (
        standard_events.groupby('label')
        ['label']
        .transform(lambda x: pd.Series([f'{x.name}_{i}' for i in range(x.shape[0])]))
    )
    standard_events['begin'] = standard_events.index
    standard_events['end'] = pd.NaT
    standard_events['end'] = standard_events['end'].astype(standard_events['begin'].dtype)
    standard_events.rename(columns={'label': 'name'}, inplace=True)
    standard_events = standard_events[['id', 'name', 'begin', 'end', 'data']]

    merged = pd.concat((standard_events, standard_sequences), axis='index', sort=False)
    return sort_standard_events(merged)
