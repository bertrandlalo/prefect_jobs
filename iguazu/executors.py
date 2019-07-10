import uuid
from typing import Any, Callable, List

from distributed import Future, fire_and_forget, worker_client
from prefect import context
from prefect.engine.executors import DaskExecutor as BaseDaskExecutor


# Workaround for a better dask-ui until this issue is fixed
# https://github.com/PrefectHQ/prefect/issues/1218

class DaskExecutor(BaseDaskExecutor):
    def submit(self, fn: Callable, *args: Any, **kwargs: Any) -> Future:
        if 'key' not in kwargs and 'task' in kwargs:
            kwargs['key'] = kwargs['task'].__class__.__name__ + '-' + str(uuid.uuid4())
        return super().submit(fn, *args, **kwargs)

    def map(self, fn: Callable, *args: Any) -> List[Future]:
        if not args:
            return []

        key = context.get('task_full_name', 'mapped')
        if self.is_started and hasattr(self, "client"):
            futures = self.client.map(fn, *args, key=key, pure=False)
        elif self.is_started:
            with worker_client(separate_thread=True) as client:
                futures = client.map(fn, *args, key=key, pure=False)
                return client.gather(futures)
        else:
            raise ValueError("This executor has not been started.")

        fire_and_forget(futures)
        return futures
