class IguazuError(Exception):
    """Base exception for all Iguazu-related exceptions"""
    pass


class PreconditionFailed(IguazuError):
    """Use when a task's precondition is not met"""
    pass


class SoftPreconditionFailed(PreconditionFailed):
    """Use for graceful failures concerning preconditions"""
    pass


class PreviousResultsExist(SoftPreconditionFailed):
    """Use when there are previous results up-to-date"""
    pass


class PostconditionFailed(IguazuError):
    """Use when a task's postcondition is not met"""
    pass


class GracefulFailWithResults(IguazuError):
    """Use when a task can graceful fail with results"""
    # TODO: rethink: why not raise a GRACEFULFAIL prefect signal?
    #       pro signal: it is the "prefect" way
    #       con signal: consistence, we would need to change the soft preconditions
    #       pro exception: soft precondtion already implemented this way
    #       con exception: it is inconsistent to mix prefect and our exceptions

    def __init__(self, results, *args):
        super().__init__(*args)
        self.results = results
