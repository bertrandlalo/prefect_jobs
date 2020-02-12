import functools
import itertools
from dataclasses import dataclass, asdict, field

import numpy as np
import pandas as pd
from dsu.events import extract_metas
from dsu.pandas_helpers import truncate
from dsu.space_stress import categorize_failure
from dsu.unity import extract_complete_sequences, extract_complete_sequence_times
from scipy.spatial import distance

from iguazu.core.exceptions import IguazuError
from iguazu.functions.specs import check_event_specification


@dataclass
class SpaceStressFeatures:
    performance: float = field(default=np.nan, metadata={'doc': 'Performance given by unity'})
    spatial_inaccuracy: float = field(default=np.nan,
                                      metadata={'doc': 'Number of failed actions because there were no target'})
    temporal_inaccuracy: float = field(default=np.nan, metadata={
        'doc': 'Number of failed actions because it was either too early or too late'})
    coordination_inaccuracy: float = field(default=np.nan, metadata={
        'doc': 'Number of failed actions because the button was not the right one'})
    global_inaccuracy: float = field(default=np.nan, metadata={'doc': 'Number of failed actions'})
    global_accuracy: float = field(default=np.nan, metadata={'doc': 'Number of successful actions'})
    pad_actions: float = field(default=np.nan, metadata={'doc': 'Number of pad actions'})
    trigger_actions: float = field(default=np.nan, metadata={'doc': 'Number of trigger actions'})
    switch_actions: float = field(default=np.nan, metadata={'doc': 'Number of switch between pad and trigger'})
    participant_motion_tau: float = field(default=np.nan,
                                          metadata={'doc': 'Motion tau estimated over participant actions'})
    information_motion_tau: float = field(default=np.nan,
                                          metadata={'doc': 'Motion tau estimated over game stimulations'})
    actions_transition_trace: float = field(default=np.nan, metadata={'doc': 'Trace of action transition matrix'})
    space_transition_trace: float = field(default=np.nan, metadata={'doc': 'Trace of space transition matrix'})


def estimate_transition_matrix(data, normalize='index', column='state'):
    """ Estimate transition probability  based on 'state' trajectory

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe with column `column`
    column: str
        Name of column on which to consider the transition
    normalize: bool, str, default False
            Normalize by dividing all values by the sum of values.
            If passed ‘all’ or True, will normalize over all values.
            If passed ‘index’ will normalize over each row.
            If passed ‘columns’ will normalize over each column.

    Returns
    -------
    transition_probs: pd.DataFrame
        DataFrame with states as columns and index and transition number (if normalize=False) or
        probability (if normalize='index')

    """
    data = data[[column]].assign(next=data[column].shift(+1))  # maybe +1 instead of -1 ?
    transition_probs = pd.crosstab(data[column], data.next, normalize=normalize,
                                   dropna=False)  # 🐼magic!  mind==blown, See https://stackoverflow.com/a/40839983/227103
    return transition_probs


def estimate_actions_transition_matrix(data):
    """ Estimate transition matrix of player action's nature

    Parameters
    ----------
    data: pd.DataFrame
      DataFrame with each row corresponds to one player action and columns
      button and action_succeed specifies its nature/type.

    Returns
    -------
    normalized_transition_probs: pd.DataFrame
            DataFrame with transition probability from one action type
            to an other, with all values that sums to the nb of action types.

    Examples
    --------

    >>> data
                                              button  action_succeed
        2018-02-27 09:09:03.069339126+00:00  trigger           False
        2018-02-27 09:09:04.086241246+00:00      pad           False
        2018-02-27 09:09:04.086338994+00:00      pad           False
        2018-02-27 09:09:04.946250588+00:00  trigger           False
        2018-02-27 09:09:06.096495085+00:00  trigger            True
        ...

    First, we compute a state vector based on the nature of the action,
    that is based on both button type (trigger or pad) and result (success or fail),
    which gives us 4 possible states: trigger_failed, trigger_succeed, pad_failed, pad_succeed.

    >>> data
                                             button    action_succeed          state
        2018-02-27 09:09:03.069339126+00:00  trigger         False    trigger_failed
        2018-02-27 09:09:04.086241246+00:00      pad         False        pad_failed
        2018-02-27 09:09:04.086338994+00:00      pad         False        pad_failed
        2018-02-27 09:09:04.946250588+00:00  trigger         False    trigger_failed
        2018-02-27 09:09:06.096495085+00:00  trigger         True    trigger_succeed
        ...

    Then, we estimate the transition matrix, which gives the probability to jump from one state to another and we
    normalize it to ensure that its coefficients sums to the number of states (4 here).
    The final output looks like:

    >>> normalized_transition_probs
        next_state       pad_failed  pad_succeed  trigger_failed  trigger_succeed
        state
        pad_failed           0.6875         0.00            0.25           0.0625
        pad_succeed          0.0000         0.00            1.00           0.0000
        trigger_failed       0.2000         0.05            0.70           0.0500
        trigger_succeed      0.5000         0.00            0.50           0.0000
    """
    data = data.loc[:, ['button', 'action_succeed']].dropna()

    data.action_succeed = data.action_succeed.replace({True: 'succeed', False: 'failed'})

    data['state'] = data[['button', 'action_succeed']].astype(str).apply(lambda x: '_'.join(x), axis=1)

    transition_probs = estimate_transition_matrix(data, normalize='index')

    # add missing states (0 occurence)
    # notes: since we're only considering the trace of the matrix as a feature, this step is useless,
    # still, for future analysis, I prefer ton compute the complete transition matrix, including states with no occurence.
    states = ['trigger_succeed', 'trigger_failed', 'pad_succeed', 'pad_failed']
    transition_probs = pd.concat([transition_probs, pd.DataFrame(columns=set(states) - set(transition_probs.columns),
                                                                 index=set(states) - set(transition_probs.columns))],
                                 axis=0).fillna(0.)

    # normalize the matrix so its coeff sums to the number of states
    # [this is taken from Antoine Coutrot Matlab code]
    n_states = len(states)
    normalized_transition_probs = transition_probs / transition_probs.values.sum() * n_states
    return normalized_transition_probs


def estimate_space_transition_matrix(data, x_lim=(-3, 3), num_cols=3, y_lim=(1, 4), num_rows=2):
    """ Estimate transition matrix of player action's location on the screen

    Parameters
    ----------
    data: pd.DataFrame
          DataFrame with each row corresponds to one player action and columns
          x and y specifies its normalized coordinate on the screen.
    x_lim: tuple
          Defines boundaries for x axis in screen
    num_cols: int
          Defines the number of columns in the grid partitioning of the screen
    y_lim: tuple
          Defines boundaries for y axis in screen
    num_rows: int
      Defines the number of rows in the grid partitioning of the screen
    Returns
    -------
    normalized_transition_probs: pd.DataFrame
            DataFrame with transition probability from one part of the screen
            to an other, with all values that sums to the nb of screen partitions.

    Notes
    ------
    Here is an example of how the output is computed.
    >>> data
                                                 x         y
        2018-02-27 09:09:03.069339126+00:00 -1.262700  2.015741
        2018-02-27 09:09:04.086241246+00:00 -1.170901  2.145104
        2018-02-27 09:09:04.086338994+00:00 -1.170901  2.145104
        2018-02-27 09:09:04.946250588+00:00 -1.262700  2.015741
        2018-02-27 09:09:06.096495085+00:00 -1.262700  2.015741
        ...

    First, x and y coordinates are digitized so that space is divided in 6 partitions
    (3 horizontally, 2 vertically).
    Then, we define a 'space-state' as an action done in a particular partition of the space.
    For instance, if the player shoot an enemy located in screen coordinate (1.158936, 3.091643),
    the space-state will be (3, 2).

    >>> data
                                                    x  x_digitize         y  y_digitize  state
        2018-02-27 09:09:15.032125953+00:00  1.158936           3  3.091643           2  (3, 2)
        2018-02-27 09:09:16.037933830+00:00  1.087157           3  3.250008           2  (3, 2)
        2018-02-27 09:09:22.684072199+00:00  1.181086           3  2.984251           2  (3, 2)
        2018-02-27 09:09:08.944721671+00:00 -0.739384           2  3.423615           2  (2, 2)
        2018-02-27 09:09:25.901319314+00:00  1.093362           3  2.999314           2  (3, 2)
        ...

    Then, we estimate the transition matrix, which gives the probability to jump from one state to another and we
    normalize it to ensure that its coefficients sums to the number of states (6 here).

    The output looks like:
    >>> normalized_transition_probs
                (1, 1)    (1, 2)    (1, 3)  (2, 1)    (2, 2)    (2, 3)
        (1, 2)     0.0  0.300000  0.600000     0.0  0.600000  0.000000
        (1, 3)     0.0  0.214286  0.000000     0.0  0.642857  0.642857
        (2, 2)     0.0  0.250000  0.250000     0.0  0.000000  1.000000
        (2, 3)     0.0  0.142857  0.285714     0.0  0.071429  1.000000
        (2, 1)     0.0  0.000000  0.000000     0.0  0.000000  0.000000
        (1, 1)     0.0  0.000000  0.000000     0.0  0.000000  0.000000

    This can be read as follow:
    " If this player just made an action located in screen partition  (3, 2) - right up corner-,
      the more probable is that the next action will be in the same screen partition. "
     " If this player just made an action located in screen partition  (1, 1) - left bottom corner-,
      the more probable is that the next action will be located in partition (3, 2) - right up corner-. "
    """
    # copy the data
    data = data.loc[:, ['x', 'y']].dropna()

    # select actions in defined range
    x_index = data[data.x.between(left=x_lim[0], right=x_lim[1])].index
    y_index = data[data.y.between(left=y_lim[0], right=y_lim[1])].index
    xy_index = set(x_index).intersection(set(y_index))
    data = data.loc[xy_index]

    data['x_digitize'] = np.digitize(data.x.values, np.linspace(x_lim[0], x_lim[1], num_cols + 1))
    data['y_digitize'] = np.digitize(data.y.values, np.linspace(y_lim[0], y_lim[1], num_rows + 1))

    data['state'] = list(
        map(lambda t: str(t), zip(data.x_digitize,
                                  data.y_digitize)))

    transition_probs = estimate_transition_matrix(data, normalize='index')

    # normalize the matrix so its coeff sums to the number of states
    # [this is taken from Antoine Coutrot Matlab code]
    states = [f'({i_x + 1}, {i_y + 1})' for (i_x, i_y) in itertools.product(range(num_cols), range(num_rows))]

    # add missing states (0 occurence)
    # notes: since we're only considering the trace of the matrix as a feature, this step is useless,
    # still, for future analysis, I prefer ton compute the complete transition matrix, including states with no occurence.
    transition_probs = pd.concat([transition_probs, pd.DataFrame(columns=set(states) - set(transition_probs.columns),
                                                                 index=set(states) - set(transition_probs.columns))],
                                 axis=0).fillna(0.)
    n_states = len(states)

    normalized_transition_probs = transition_probs / transition_probs.values.sum() * n_states
    return normalized_transition_probs


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

    Notes
    ------
    Here is an example of how the output should look like.

    >>> data
                                                                                         label   button         x         y         z  action_succeed failure_reason  wave  difficulty trajectory_length
        2019-04-03 08:35:21.521755333+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428315  2.280506  5.309360  False          bad_precision   1.          5.            NaN
        2019-04-03 08:35:21.775456032+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428315  2.280506  5.309360  False          bad_precision   1.          5.            0.000000
        2019-04-03 08:35:22.500084331+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428408  2.402699  5.282661  False          bad_precision   1.          5.            0.122193
        2019-04-03 08:35:22.753246430+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.428408  2.402699  5.282661  False          bad_precision   1.          5.            0.000000
        2019-04-03 08:35:22.986076530+00:00  unity_space-stress_game_participant_pushes_button  trigger -1.448533  2.439976  5.272884  False          bad_precision   1.          5.            0.042363
        ...

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

    Notes
    ------
    Here is an example of how the outputshould look like:

    >>> data
                                             id                                 label   type      x      y      z    wave  difficulty  trajectory_length
        2019-04-03 08:36:07.464509437+00:00   0  unity_space-stress_game_enemy_spawns  enemy  1.989  2.766  5.480    1.         5.                NaN
        2019-04-03 08:36:07.691995137+00:00   1  unity_space-stress_game_enemy_spawns  enemy  1.989  2.766  5.480    1.         5.                NaN
        2019-04-03 08:36:07.890431837+00:00   2  unity_space-stress_game_enemy_spawns  enemy  0.278  1.919  5.673    1.         5.           1.955187
        2019-04-03 08:36:08.142808336+00:00   3  unity_space-stress_game_enemy_spawns  enemy  1.591  4.102  4.411    1.         5.           2.547441
        2019-04-03 08:36:08.324275836+00:00   4  unity_space-stress_game_enemy_spawns  enemy -1.140  1.840  5.230    1.         5.           3.546125
        ...

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
    Dataframe with 13 columns (each corresponding to a feature) and 6 rows (each corresponding to a wave):
        - performance: Difficulty of the wave

        - information_motion_tau: Motion tau estimated with euclidean distance
        between successive stimulations from the game in plan (X,Y).
        - participant_motion_tau: Motion tau estimated with euclidean distance between
         successive actions from the participant in plan (X,Y)

        - spatial_inaccuracy: Number of failed actions because there were no target
        - temporal_inaccuracy: Number of failed actions because it was either too early or too late
        - coordination_inaccuracy: Number of failed actions because the button was not the right one
        (ie. pad on an enemy or trigger on a breach)
        - global_accuracy: Number of successful actions
        - global_inaccuracy: Number of failed actions

        - pad_actions: Number of pad actions
        - trigger_actions: Number of trigger actions
        - switch_actions: Number of switch between pad and trigger

        - space_transition_trace: Trace of space transition matrix
        - actions_transition_trace: Trace of action transition matrix
    Examples
    ________
    Output dataframe looks like:

    >>> features
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

        # trace of transition matrix of action's nature (what)
        # ----------------------------------------------------
        actions_transition_matrix = estimate_actions_transition_matrix(events_wave)
        actions_transition_trace = np.trace(actions_transition_matrix.values)
        # trace of transition matrix of action's space (where)
        # ----------------------------------------------------
        space_transition_matrix = estimate_space_transition_matrix(events_wave)
        space_transition_trace = np.trace(space_transition_matrix.values)

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
                                       'actions_transition_trace',
                                       'space_transition_trace'
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
                                      game_motion_tau,
                                      actions_transition_trace,
                                      space_transition_trace])
        scores_df.append(score_df)
    features = pd.concat(scores_df, 1, sort=True).T
    return features
