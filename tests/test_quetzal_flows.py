from prefect import Flow, Parameter

from iguazu.tasks.quetzal import QueryTask


def test_query_success():
    query_task = QueryTask(url='https://localhost/api/v1',
                           username='admin',
                           password='secret',
                           insecure=True)

    with Flow('test_query_success flow') as flow:
        sql = Parameter('input_sql')
        query_task(query=sql)

    parameters = dict(
        input_sql='SELECT * FROM base',
    )
    state = flow.run(parameters=parameters)
    assert state.is_successful()
