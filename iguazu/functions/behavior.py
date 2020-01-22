import functools

import numpy as np
import pandas as pd
from dsu.events import extract_metas
from dsu.pandas_helpers import truncate
from dsu.space_stress import categorize_failure
from dsu.unity import extract_complete_sequences, extract_complete_sequence_times
from scipy.spatial import distance

from iguazu.core.exceptions import IguazuError
from iguazu.functions.specs import check_event_specification


def estimate_trajectory_length(data, columns):
    """Estimate euclidean distance between successive space coordinates.

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe with spatio-temporal ie. index are TimeStamps and columns are
        euclidean space coordinates (eg. X,Y, Z)
    columns: list
        List of columns with space coordinates
    """
    if not set(columns).issubset(data.columns):
        raise ValueError('Columns should be a subset of data columns')
    coordinate_data = data[columns]
    out = data.copy()
    dists = [np.NaN]  # First distance is NaN
    for i in range(1, len(coordinate_data)):
        dists.append(distance.euclidean(coordinate_data.iloc[i - 1].values, coordinate_data.iloc[i].values))
    out['trajectory_length'] = dists
    return out


def extract_space_stress_participant_actions(events):
    """ Extract information about participant controller actions from space stress events

    This function extracts events with label "unity_space-stress_game_participant_pushes_button" and construct a table
    with interesting features associated to the action (cursor position, context, results .. ).

    Parameters
    ----------
    events: pd.DataFrame
        Dataframe with columns 'label' and 'data', containing events sent by
        unity during VR session.

    Returns
    -------
    A dataframe with each row corresponding to one action from the participant
    and columns are the following:
        - label: "unity_space-stress_game_participant_pushes_button"
        - button: Button pressed by the participant (trigger or pad).
        - x: Coordinate x of the cursor position.
        - y: Coordinate y of the cursor position.
        - z: Coordinate z of the cursor position.
        - action_succeed: Boolean giving action output (True if success, False if fail).
        - failure_reason: string ("finger_confusion"|"bad_precision"|"bad_planification") or None if there is no failure.
        - wave: Index of the wave.
        - difficulty: Difficulty of the wave
        - trajectory_length: Euclidean distance between successive actions in plan (X,Y).

    Examples
    --------
    Output looks like:
                                                                                      label   button         x         y         z  action_succeed failure_reason  wave  difficulty trajectory_length
      2019-04-03 08:35:21.521755333+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428315  2.280506  5.309360  False          bad_precision   1.          5.            NaN
      2019-04-03 08:35:21.775456032+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428315  2.280506  5.309360  False          bad_precision   1.          5.            0.000000
      2019-04-03 08:35:22.500084331+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428408  2.402699  5.282661  False          bad_precision   1.          5.            0.122193
      2019-04-03 08:35:22.753246430+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428408  2.402699  5.282661  False          bad_precision   1.          5.            0.000000
      2019-04-03 08:35:22.986076530+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.448533  2.439976  5.272884  False          bad_precision   1.          5.            0.042363

    Notes:
    ------
    See the documentation of :py:func:dsu.space_stress.classify_failures

    """
    # check that the input meets the events standard specifications
    check_event_specification(events)

    if 'space-stress_sequence' not in extract_complete_sequences(events, label_column='name'):
        raise IguazuError('Could not find "space-stress_sequence".')

    space_stress_times = extract_complete_sequence_times(events, 'space-stress_sequence', pedantic='warn',
                                                         label_column='name')
    begins, ends = space_stress_times[0]

    out = truncate(extract_metas(events,
                                 labels=['unity_space-stress_game_participant_pushes_button'],
                                 meta_keys=['button', 'x', 'y', 'z', 'result'], label_column='name'),
                   begins=begins, ends=ends)
    out.loc[:, 'action_succeed'] = out.result.apply(lambda x: 'succeed' in x['action'])
    out = out.drop(out.loc[(out.button == 'pad') & (
            out.result == {'action': 'action_failed'})].index)

    for button in ['pad', 'trigger']:
        # classify failure reason depending on button type
        idx_button = (out.button == button)
        func_button = functools.partial(categorize_failure, button=button)
        out.loc[idx_button, 'failure_reason'] = out.loc[idx_button, 'result'].apply(func_button)

    sequence_times = extract_complete_sequence_times(events, 'space-stress_game_enemy-wave', pedantic='warn',
                                                     label_column='name')
    for k_wave, (wave_begins, wave_ends) in enumerate(sequence_times):
        # add a column with wave index and difficulty
        out.loc[wave_begins:wave_ends, 'wave'] = k_wave
        out.loc[wave_begins:wave_ends, 'difficulty'] = \
            events.loc[events.name.str.contains('unity_space-stress_game_enemy-wave_end'), 'data'][k_wave]['report'][
                'difficulty']
    # estimate trajectory length of participant actions in X,Y plan.
    out = estimate_trajectory_length(data=out, columns=['x', 'y'])
    return out.drop(['result', 'name'], axis=1)


def extract_space_stress_spawns_stimulations(events):
    """ Extract information about spawns in space stress events
    This function extracts events with label "unity_space-stress_game_breach_spawns" and
    "unity_space-stress_game_enemy_spawns". It returns a dataframe with interesting features
    associated to these actions (spawn position, type, id ).

    Parameters
    ----------
    events: pd.DataFrame
        Dataframe with columns 'label' and 'data', containing events sent by
        unity during VR session.

    Returns
    -------
    A dataframe with each row corresponding to a stimulation from the game and
    columns are the following:
        - id: id of the breach or enemy
        - label: unity_space-stress_game_breach_spawns.
        - type: Type of spawner (enemy or breach).
        - x: Coordinate x of the spawn.
        - y: Coordinate y of the spawn.
        - z: Coordinate z of the spawn.
        - wave: Index of the wave.
        - difficulty: Difficulty of the wave.
        - trajectory_length: Euclidean distance between successive spawns in plan (X,Y).

    Examples
    --------
    Output looks like:

                                         id                                 label   type      x      y      z
    2019-04-03 08:36:07.464509437+00:00   0  unity_space-stress_game_enemy_spawns  enemy  1.989  2.766  5.480
    2019-04-03 08:36:07.691995137+00:00   1  unity_space-stress_game_enemy_spawns  enemy  1.989  2.766  5.480
    2019-04-03 08:36:07.890431837+00:00   2  unity_space-stress_game_enemy_spawns  enemy  0.278  1.919  5.673
    2019-04-03 08:36:08.142808336+00:00   3  unity_space-stress_game_enemy_spawns  enemy  1.591  4.102  4.411
    2019-04-03 08:36:08.324275836+00:00   4  unity_space-stress_game_enemy_spawns  enemy -1.140  1.840  5.230

                                      type      x      y      z  wave  difficulty  trajectory_length
2019-04-03 08:36:07.464509437+00:00  enemy  1.989  2.766  5.480    1.         5.                NaN
2019-04-03 08:36:07.691995137+00:00  enemy  1.989  2.766  5.480    1.         5.           3.132597
2019-04-03 08:36:07.890431837+00:00  enemy  0.278  1.919  5.673    1.         5.           1.955187
2019-04-03 08:36:08.142808336+00:00  enemy  1.591  4.102  4.411    1.         5.           2.547441
2019-04-03 08:36:08.324275836+00:00  enemy -1.140  1.840  5.230    1.         5.           3.546125

    """
    # check that the input meets the events standard specifications
    check_event_specification(events)

    if 'space-stress_sequence' not in extract_complete_sequences(events, label_column='name'):
        raise IguazuError('Could not find "space-stress_sequence".')

    enemy_spawns = extract_metas(events, labels=['unity_space-stress_game_enemy_spawns'],
                                 meta_keys=['enemy_id', 'x', 'y', 'z'],
                                 label_column='name').rename(columns={'enemy_id': 'id'})
    enemy_spawns['type'] = 'enemy'

    breach_spawns = extract_metas(events, labels=['unity_space-stress_game_breach_spawns'],
                                  meta_keys=['breach_id', 'x', 'y', 'z'],
                                  label_column='name').rename(columns={'breach_id': 'id'})
    breach_spawns['type'] = 'breach'

    out = pd.concat([breach_spawns, enemy_spawns], sort=True).sort_index()

    for k_wave, (wave_begins, wave_ends) in enumerate(
            extract_complete_sequence_times(events, 'space-stress_game_enemy-wave',
                                            label_column='name', pedantic='warn')):
        # add a column with wave index and difficulty
        out.loc[wave_begins:wave_ends, 'wave'] = k_wave
        out.loc[wave_begins:wave_ends, 'difficulty'] = \
            events.loc[events.name.str.contains('unity_space-stress_game_enemy-wave_ends'),
                       'data'][k_wave]["report"]["difficulty"]
    # estimate trajectory length of spawns events in X,Y plan.
    out = estimate_trajectory_length(data=out, columns=['x', 'y'])
    return out.drop(['name', 'id'], axis=1)


def extract_space_stress_scores(spawns_stimulations, participant_actions):
    """ Computes space stress scores from preprocessed events.
    This function extracts "scores" per waves, based on the number of action of a particular kind
    (failure, reason for failure, button type) and the motion tau from spawns events and from participant events.

    Parameters
    ----------
    participant_actions: pd.DataFrame
        Dataframe resulting from function :py:func:space_stress_participant_actions
    spawns_stimulations: pd.DataFrame
        Dataframe resulting from function :py:func:space_stress_spawns_stimulations

    Returns
    -------
    Dataframe with the following columns:
        - performance: Difficulty of the wave

        - information_motion_tau: Motion tau estimated with euclidean distance
        between successive stimulations from the game in plan (X,Y).
        - participant_motion_tau: Motion tau estimated with euclidean distance between
         successive actions from the participant in plan (X,Y)

        - spatial_inaccuracy: Number of failed actions because there were no target
        - temporal_inaccuracy: Number of failed actions because it was either too early or too late.
        - global_accuracy: Number of successfull actions
        - global_inaccuracy: Number of failed actions

        - pad_actions: Number of pad actions
        - trigger_actions: Number of trigger actions
        - switch_actions: Number of switch between pad and trigger

    Examples
    ________
    Output dataframe looks like:

                   coordination_inaccuracy  ...  trigger_actions
        wave0                      2.0  ...              7.0
        wave1                      2.0  ...              7.0
        wave2                      0.0  ...              6.0
        wave3                      0.0  ...              5.0
        wave4                      1.0  ...              2.0
        wave5                      1.0  ...             21.0

    """
    scores_df = []
    waves = np.unique(participant_actions.wave.dropna().values)
    # loop amongst waves
    for wave in waves:
        index_wave = ['wave' + str(int(wave))]
        events_wave = participant_actions.loc[(participant_actions.wave == wave)]
        game_events_wave = spawns_stimulations.loc[(spawns_stimulations.wave == wave)]
        duration = (events_wave.index[-1] - events_wave.index[0]) / np.timedelta64(1, 's')

        # count number of events based on action_succeed result
        N_success = len(events_wave.loc[events_wave.action_succeed == True])
        N_bad = len(events_wave.loc[events_wave.action_succeed == False])
        # count number of events based on failure_reason result
        N_bad_spatial = len(events_wave.loc[events_wave.failure_reason == 'bad_precision'])
        N_bad_temporal = len(events_wave.loc[events_wave.failure_reason == 'bad_planification'])
        N_bad_coordination = len(events_wave.loc[events_wave.failure_reason == 'finger_confusion'])
        # count number of events based on button type
        N_pad = len(events_wave.loc[events_wave.button == 'pad'])
        N_trigger = len(events_wave.loc[events_wave.button == 'trigger'])

        # count number of switch from button,ie. when previous != actual
        # eg. ["pad", "trigger", "pad", "pad"] => [2, 1, 2, 2] => [None, True, True, False] => N_switch=2
        N_switch = (events_wave.button.replace('trigger', 1).replace('pad', 2).diff() > 0).sum()

        # estimate the trajectory lengths divided by wave duration
        participant_motion_tau = events_wave.trajectory_length.sum() / duration
        game_motion_tau = game_events_wave.trajectory_length.sum() / duration

        # difficulty is rated on 100, scale it to 1 for consistency purpose with other scores.
        score_performance = events_wave.difficulty.values[0] / 100

        score_df = pd.DataFrame(columns=index_wave,
                                index=['performance',
                                       'spatial_inaccuracy',
                                       'temporal_inaccuracy',
                                       'coordination_inaccuracy',
                                       'global_inaccuracy',
                                       'global_accuracy',
                                       'pad_actions',
                                       'trigger_actions',
                                       'switch_actions',
                                       'participant_motion_tau',
                                       'information_motion_tau',
                                       ],
                                data=[score_performance,
                                      N_bad_spatial,
                                      N_bad_temporal,
                                      N_bad_coordination,
                                      N_bad,
                                      N_success,
                                      N_pad,
                                      N_trigger,
                                      N_switch,
                                      participant_motion_tau,
                                      game_motion_tau])
        scores_df.append(score_df)
    out = pd.concat(scores_df, 1, sort=True).T
    return out
