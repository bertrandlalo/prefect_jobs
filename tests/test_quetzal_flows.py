from prefect import Flow, Parameter
from quetzal.client.helpers import get_client
import prefect

from iguazu.tasks.quetzal import CreateWorkspace, DeleteWorkspace, Query, ScanWorkspace


def test_query_success():
    query_task = Query(url='https://localhost/api/v1',
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
    query_task = Query(url='https://localhost/api/v1',
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
    create_task = CreateWorkspace(url='https://localhost/api/v1',
                                  username='admin',
                                  password='secret',
                                  insecure=True,
                                  exist_ok=True)
    with Flow('test_create_workspace flow') as flow:
        create_task(temporary=True)

    state = flow.run()
    assert state.is_successful()


def test_retrieve_workspace():
    create_task = CreateWorkspace(url='https://localhost/api/v1',
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
    create_task = CreateWorkspace(url='https://localhost/api/v1',
                                  username='admin',
                                  password='secret',
                                  insecure=True,
                                  exist_ok=False)
    with Flow('test_create_duplicate_workspace flow') as flow:
        id1 = create_task(name='iguazu-unit-tests', temporary=True)
        id2 = create_task(name='iguazu-unit-tests', temporary=True)

    state = flow.run()
    assert state.is_failed()


def test_create_and_scan_workspace():
    client = get_client(url='https://localhost/api/v1',
                        username='admin',
                        password='secret',
                        insecure=True)
    create_task = CreateWorkspace(exist_ok=True)
    scan_task = ScanWorkspace()

    with prefect.context(quetzal_client=client):
        with Flow('test_create_and_scan_workspace flow') as flow:
            wid1 = create_task(name='iguazu-unit-tests', temporary=True)
            wid2 = scan_task(wid1)

        from prefect.utilities.debug import raise_on_exception
        with raise_on_exception():
            state = flow.run()
        assert state.is_successful()
        assert state.result[wid1].result == state.result[wid2].result


def test_create_and_delete_workspace():
    client = get_client(url='https://localhost/api/v1',
                        username='admin',
                        password='secret',
                        insecure=True)
    create_task = CreateWorkspace(exist_ok=True)
    delete_task = DeleteWorkspace()

    with prefect.context(quetzal_client=client):
        with Flow('test_create_and_scan_workspace flow') as flow:
            wid1 = create_task(temporary=True)
            wid2 = delete_task(wid1)

        from prefect.utilities.debug import raise_on_exception
        with raise_on_exception():
            state = flow.run()
        assert state.is_successful()
        assert state.result[wid1].result == state.result[wid2].result


# def test_download():
#     import prefect
#
#     @prefect.task
#     def process_file(file):
#         from iguazu.unnamed import QuetzalFile, LocalFile
#         if isinstance(file, str):
#             file_obj = LocalFile(file)
#         else:
#             file_obj = QuetzalFile(file)
#         f = file_obj.file
#         print(f)
#
#     @prefect.task
#     def list_local_files():
#         import pathlib
#         files = [
#             str(f.resolve())
#             for f in pathlib.Path('/Users/david/temp/').glob('*')
#             if f.is_file()
#         ]
#         return files[:3]
#
#     query_task = Query(url='https://localhost/api/v1',
#                            username='admin',
#                            password='secret',
#                            insecure=True)
#
#     with prefect.context(a=1, b=2, quetzal_client=query_task.client) as ctx:
#         print(list(prefect.context))
#         with Flow('test_query_success flow') as flow:
#             sql = Parameter('input_sql')
#             dataset = query_task(query=sql)
#             process_file.map(dataset)
#             local_dataset = list_local_files()
#             process_file.map(local_dataset)
#
#         parameters = dict(
#             input_sql='SELECT * FROM base',
#         )
#         state = flow.run(parameters=parameters)
#         assert state.is_successful()
