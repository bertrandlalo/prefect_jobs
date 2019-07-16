# TODO: think about moving this module somewhere else like iguazu.prefect.cache_validators ?
#       Maybe move iguazu.executors in it as well? Maybe not?

from typing import Any, Dict

from prefect.engine.cache_validators import all_inputs, all_parameters
from prefect.engine.state import Cached


def all_validator(use_inputs=True, use_parameters=True, force=False):
    def _combine(state: Cached,
                 inputs: Dict[str, Any],
                 parameters: Dict[str, Any]) -> bool:
        print('all_validator cache verification')
        if force:
            print('Not cached - reason = forced')
            return False
        elif use_inputs and use_parameters:
            tmp = all_inputs(state, inputs, parameters) and all_parameters(state, inputs, parameters)
            if tmp:
                print('Cached - reason = same inputs and parameters')
            else:
                print('Not cached - reason = different inputs or parameters')
            return tmp
        elif use_inputs:
            tmp = all_inputs(state, inputs, parameters)
            if tmp:
                print('Cached - reason = same inputs')
            else:
                print('Not cached - reason = different inputs')
            return tmp
        elif use_parameters:
            tmp = all_parameters(state, inputs, parameters)
            if tmp:
                print('Cached - reason = same  parameters')
            else:
                print('Not cached - reason = different parameters')
            return tmp
        print('Not cached - reason: no configuration')
        return False
    return _combine
