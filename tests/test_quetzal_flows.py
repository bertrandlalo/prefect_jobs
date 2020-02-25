import collections
import uuid

from prefect import Flow, Parameter
from prefect.utilities.tasks import unmapped
from quetzal.client.helpers import get_client
import prefect

from iguazu.core.files import FileAdapter
from iguazu.tasks.quetzal import CreateWorkspace, ConvertToFileAdapter, DeleteWorkspace, Query, ScanWorkspace


def test_query_success(mocker):
    query_mock = mocker.patch('quetzal.client.helpers.query')
    query_mock.return_value = [{'id': str(uuid.uuid4())}], 1

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
    query_mock.assert_called()


def test_query_connect_fail():
    query_task = Query(url='https://localhost/not/a/real/url',
                       username='bad_user',
                       password='bad_password',
                       insecure=True)

    with Flow('test_query_connect_fail flow') as flow:
        sql = Parameter('input_sql')
        query_task(query=sql)

    parameters = dict(
        input_sql='SELECT * FROM base',
    )
    state = flow.run(parameters=parameters)

    assert state.is_failed()


def test_query_convert(mocker):
    ids = {str(uuid.uuid4()) for _ in range(5)}
    query_mock = mocker.patch('quetzal.client.helpers.query')
    query_mock.return_value = [{'id': i} for i in ids], len(ids)

    query_task = Query(url='https://localhost/api/v1',
                       username='user',
                       password='password',
                       insecure=True)
    convert_task = ConvertToFileAdapter('id')

    with Flow('test_query_success flow') as flow:
        sql = Parameter('input_sql')
        rows = query_task(query=sql)
        adapters = convert_task(rows, workspace_id=None)
        adapters_map = convert_task.map(rows, workspace_id=unmapped(None))

    parameters = dict(
        input_sql='SELECT * FROM base LIMIT 5',
    )
    state = flow.run(parameters=parameters)

    assert state.is_successful()
    assert all([isinstance(p, FileAdapter) for p in state.result[adapters].result])
    assert all([isinstance(p, FileAdapter) for p in state.result[adapters_map].result])
    assert {p.id for p in state.result[adapters_map].result} == ids


def test_create_workspace(mocker):
    list_mock = mocker.patch('quetzal.client.helpers.workspace.list_')
    list_mock.return_value = [], 0
    create_mock = mocker.patch('quetzal.client.helpers.workspace.create')
    create_mock.return_value = collections.namedtuple('Workspace', ['id', 'status'])(1, 'READY')

    create_task = CreateWorkspace(url='https://localhost/api/v1',
                                  username='admin',
                                  password='secret',
                                  insecure=True,
                                  exist_ok=True)
    with Flow('test_create_workspace flow') as flow:
        create_task(temporary=True)

    state = flow.run()

    assert state.is_successful()
    create_mock.assert_called_once()


def test_retrieve_workspace(mocker):
    list_mock = mocker.patch('quetzal.client.helpers.workspace.list_')
    list_mock.return_value = [{'id': 1, 'status': 'READY', 'name': 'iguazu-unit-test'}], 1

    create_task = CreateWorkspace(url='https://localhost/api/v1',
                                  username='admin',
                                  password='secret',
                                  insecure=True,
                                  exist_ok=True)
    with Flow('test_retrieve_workspace flow') as flow:
        id1 = create_task(workspace_name='iguazu-unit-tests', temporary=True)

    state = flow.run()
    assert state.is_successful()

    # Obtain and verify that the retrieved id is the expected one
    assert state.result[id1].result == 1
    list_mock.assert_called_once()


def test_create_duplicate_workspace(mocker):
    list_mock = mocker.patch('quetzal.client.helpers.workspace.list_')
    list_mock.return_value = [{'id': 1, 'status': 'READY', 'name': 'iguazu-unit-test'}], 1
    create_mock = mocker.patch('quetzal.client.helpers.workspace.create')

    create_task = CreateWorkspace(url='https://localhost/api/v1',
                                  username='admin',
                                  password='secret',
                                  insecure=True,
                                  exist_ok=True)
    with Flow('test_create_duplicate_workspace flow') as flow:
        create_task(workspace_name='iguazu-unit-tests', temporary=True)

    state = flow.run()

    assert state.is_successful()
    list_mock.assert_called_once()
    create_mock.assert_not_called()


# def test_create_and_scan_workspace():
#     client = get_client(url='https://localhost/api/v1',
#                         username='admin',
#                         password='secret',
#                         insecure=True)
#     create_task = CreateWorkspace(exist_ok=True)
#     scan_task = ScanWorkspace()
#
#     with prefect.context(quetzal_client=client):
#         with Flow('test_create_and_scan_workspace flow') as flow:
#             wid1 = create_task(name='iguazu-unit-tests', temporary=True)
#             wid2 = scan_task(wid1)
#
#         from prefect.utilities.debug import raise_on_exception
#         with raise_on_exception():
#             state = flow.run()
#         assert state.is_successful()
#         assert state.result[wid1].result == state.result[wid2].result
#
#
# def test_create_and_delete_workspace():
#     client = get_client(url='https://localhost/api/v1',
#                         username='admin',
#                         password='secret',
#                         insecure=True)
#     create_task = CreateWorkspace(exist_ok=True)
#     delete_task = DeleteWorkspace()
#
#     with prefect.context(quetzal_client=client):
#         with Flow('test_create_and_scan_workspace flow') as flow:
#             wid1 = create_task(temporary=True)
#             wid2 = delete_task(wid1)
#
#         from prefect.utilities.debug import raise_on_exception
#         with raise_on_exception():
#             state = flow.run()
#         assert state.is_successful()
#         assert state.result[wid1].result == state.result[wid2].result

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
