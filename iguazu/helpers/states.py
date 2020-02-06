from prefect.engine.signals import PrefectStateSignal
from prefect.engine.state import Success


class SkippedResult(Success):
    """Skipped state with results

    This state represents a skipped state with results, used to express that a
    task did not do most of its heavy work because the result was already
    available.

    The purpose of this class is purely cosmetic, so that our flow.visualize
    is more expressive.

    """
    color = '#cab2d6'


class GracefulFail(Success):  # TODO: revisit the need of this class
    color = '#dd1c77'


class SKIPRESULT(PrefectStateSignal):
    _state_cls = SkippedResult


class GRACEFULFAIL(PrefectStateSignal):
    _state_cls = GracefulFail
