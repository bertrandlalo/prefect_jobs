import pandas as pd


def item_to_feature(report):
    feature = pd.DataFrame([[report['answer_final'], 'answerFinal', 's.u'],
                            [report['answer_time'], 'answerDuration', 's']],
                           columns=['value', 'id', 'units'])

    feature['reference'] = str(report['item_index'])
    feature['name'] = report['item_text']
    return feature


def event_to_feature(event):
    event_id = event['id']
    event_data = event['data']
    survey_index = event_data.get('survey_index') - 1  # -1 to ensure it starts at 0
    reports = event_data.get('report')  # reports is a list of item answer's report
    feature = pd.concat(list(map(item_to_feature, reports)), axis='index', ignore_index=True)
    module = event_id.split('_')[1]  # todo: rather regex
    feature['reference'] = f'{module}-{survey_index}-' + feature['reference']
    return feature


def extract_report_features(events):
    events_survey_reports = events[events.id.str.contains('survey_reports')]
    # todo: raise exception if `events_survey_reports` is empty
    list_survey_features = []
    for _, survey_event in events_survey_reports.iterrows():
        list_survey_features.append(event_to_feature(survey_event))
    return pd.concat(list_survey_features, axis='index', ignore_index=True)


def extract_meta_features(survey_features, config):
    list_meta_features = []
    for meta_key, list_ref in config.items():
        meta_feature = survey_features[survey_features.reference.isin(list_ref)].groupby('id').mean().reset_index()
        meta_feature['reference'] = f'vr-meta-{meta_key}'
        list_meta_features.append(meta_feature)
    return pd.concat(list_meta_features, axis='index', ignore_index=True)

