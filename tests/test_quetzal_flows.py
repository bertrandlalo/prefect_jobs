from prefect import Flow, Parameter

from iguazu.tasks.quetzal import CreateWorkspaceTask, QueryTask


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


def test_query_auth_fail():
    query_task = QueryTask(url='https://localhost/api/v1',
                           username='bad_user',
                           password='bad_password',
                           insecure=True)

    with Flow('test_query_auth_fail flow') as flow:
        sql = Parameter('input_sql')
        query_task(query=sql)

    parameters = dict(
        input_sql='SELECT * FROM base',
    )
    state = flow.run(parameters=parameters)
    assert state.is_failed()


def test_create_workspace():
    create_task = CreateWorkspaceTask(url='https://localhost/api/v1',
                                      username='admin',
                                      password='secret',
                                      insecure=True,
                                      exist_ok=True)
    with Flow('test_create_workspace flow') as flow:
        create_task(temporary=True)

    state = flow.run()
    assert state.is_successful()


def test_retrieve_workspace():
    create_task = CreateWorkspaceTask(url='https://localhost/api/v1',
                                      username='admin',
                                      password='secret',
                                      insecure=True,
                                      exist_ok=True)
    with Flow('test_retrieve_workspace flow') as flow:
        id1 = create_task(name='iguazu-unit-tests', temporary=True)
        id2 = create_task(name='iguazu-unit-tests', temporary=True)

    state = flow.run()
    assert state.is_successful()

    # Obtain and verify that the resulting workspace id is the same!
    assert state.result[id1].result == state.result[id2].result


def test_create_duplicate_workspace():
    create_task = CreateWorkspaceTask(url='https://localhost/api/v1',
                                      username='admin',
                                      password='secret',
                                      insecure=True,
                                      exist_ok=False)
    with Flow('test_create_duplicate_workspace flow') as flow:
        id1 = create_task(name='iguazu-unit-tests', temporary=True)
        id2 = create_task(name='iguazu-unit-tests', temporary=True)

    state = flow.run()
    assert state.is_failed()
