import pandas as pd


class NoSurveyReport(Exception):
    pass

def item_to_feature(report):
    """ Extract final answer and duration from survey report data and make a feature

    Parameters
    ----------
    report: dict
        Data from an event '*_survey_report'

    Returns
    -------
    feature: pd.DataFrame()
        Standard feature with final answer and answer time

    Example:
    --------
    > report

    {'item_time': 0.011092239059507847,
     'item_index': 0,
     'item_key': 'survey-coherence-question-1',
     'item_text': 'Comment vous sentez-vous maintenant ?',
     'answer_default': 0.5,
     'answer_ticks': [{'time': 12.464340209960938, 'value': 0.955794095993042},
      {'time': 12.475440979003906, 'value': 0.9557375907897949},
      {'time': 12.487258911132812, 'value': 0.9548861980438232},
        ...                         ...
        ...                         ...
      {'time': 12.849480628967285, 'value': 0.9511183500289917},
      {'time': 12.860608100891113, 'value': 0.9490364193916321}],
     'answer_final': 0.9490364193916321,
     'answer_time': 14.89667797088623,
     'answer_completion': True}

    > feature = item_to_feature(report)
    > feature

             value     id               units                    name                              reference
        0   0.949036  answerFinal       s.u    Comment vous sentez-vous maintenant ?       cardiac-coherence-0-0
        1  14.896678  answerDuration    s      Comment vous sentez-vous maintenant ?       cardiac-coherence-0-0

    """
    feature = pd.DataFrame([[report['answer_final'], 'answerFinal', 's.u'],
                            [report['answer_time'], 'answerDuration', 's']],
                           columns=['value', 'id', 'units'])

    feature['reference'] = str(report['item_index'])
    feature['name'] = report['item_text']
    return feature


def event_to_feature(event):
    """ Extract a survey report from an event row and convert it into a standard feature

    Parameters
    ----------
    event: pd.Series
        a row from unity events with label `*_survey_reports`
        and data the report
    Returns
    -------
    feature: pd.DataFrame
        the extracted report as a standard feature

    Example
    -------
    > event

            id                unity_cardiac-coherence_survey_reports_0
        name                unity_cardiac-coherence_survey_reports
        begin                        2019-03-13 13:26:19.973074149
        end                                                    NaT
        data     {'survey_index': 1, 'report': [{'item_time': 0...
        Name: 2019-03-13 13:26:19.973074149+00:00, dtype: object

    > feature = event_to_feature(event)
    > feature

             value     id               units                    name                              reference
        0   0.949036  answerFinal       s.u    Comment vous sentez-vous maintenant ?       cardiac-coherence-0-0
        1  14.896678  answerDuration    s      Comment vous sentez-vous maintenant ?       cardiac-coherence-0-0

    """
    event_id = event['id']
    event_data = event['data']
    survey_index = event_data.get('survey_index') - 1  # -1 to ensure it starts at 0
    reports = event_data.get('report')  # reports is a list of item answer's report
    feature = pd.concat(list(map(item_to_feature, reports)), axis='index', ignore_index=True)
    module = event_id.split('_')[1]  # todo: rather regex
    feature['reference'] = f'{module}-{survey_index}-' + feature['reference']
    return feature


def extract_report_features(events):
    """ Extract survey reports as features from events

    Parameters
    ----------
    events: pd.Dataframe
        Standardized unity events

    Returns
    -------
    features: pd.DataFrame
        Standard features with survey reports (ie. final answer and duration) of each survey of the
        VR experiment (`reference` columns corresponds to the survey module and index) .

    Example :
    ---------
     > events.head()

                                                                           id  ...                                               data
        2019-03-13 13:20:29+00:00                          session_sequence_0  ...                                               None
        2019-03-13 13:20:29+00:00             unity_session_sequence_begins_0  ...  {'selected_language': 'french', 'is_linear': T...
        2019-03-13 13:20:29.268545723+00:00  unity_setup_marker_has_version_0  ...                              {'version': '0.11.1'}
        2019-03-13 13:20:29.268567667+00:00   unity_setup_build_has_version_0  ...          {'version': '1.1.6.04122018.393.8c0aa7f'}
        2019-03-13 13:20:31.893913131+00:00                  intro_sequence_0  ...                                               None

     > survey_features = extract_report_features(events)
     > survey_features.head()

             value     id               units                    name                                   reference
        0   0.949036  answerFinal       s.u    Comment vous sentez-vous maintenant ?             cardiac-coherence-0-0
        1  14.896678  answerDuration    s      Comment vous sentez-vous maintenant ?             cardiac-coherence-0-0
        2   0.702862  answerFinal       s.u    Comment vous sentez-vous maintenant ?             cardiac-coherence-1-0
        3  17.460850  answerDuration    s      Comment vous sentez-vous maintenant ?             cardiac-coherence-1-0
        4   0.263636  answerFinal       s.u    Avez-vous trouvé cet entraînement agréable ?      cardiac-coherence-1-1

    """
    events_survey_reports = events[events.id.str.contains('survey_reports')]
    if events_survey_reports.empty:
        raise NoSurveyReport('No `survey_reports` found in events')
    list_survey_features = []
    for _, survey_event in events_survey_reports.iterrows():
        list_survey_features.append(event_to_feature(survey_event))
    return pd.concat(list_survey_features, axis='index', ignore_index=True)


def extract_meta_features(survey_features, config):
    """

    Parameters
    ----------
    survey_features
    config

    Returns
    -------

    """
    list_meta_features = []
    for meta_key, list_ref in config.items():
        meta_feature = survey_features[survey_features.reference.isin(list_ref)].groupby('id').mean().reset_index()
        meta_feature['reference'] = f'vr-meta-{meta_key}'
        list_meta_features.append(meta_feature)
    return pd.concat(list_meta_features, axis='index', ignore_index=True)

