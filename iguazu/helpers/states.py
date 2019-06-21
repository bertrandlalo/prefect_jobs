from prefect.engine.state import Skipped


class SkippedResult(Skipped):
    """Skipped state with results

    This state represents a skipped state with results, used to express that a
    task did not do most of its heavy work because the result was already
    available.

    The purpose of this class is purely cosmetic, so that our flow.visualize
    is more expressive.

    """
    color = '#cab2d6'


class GracefulFail(Skipped):
    color = '#dd1c77'

