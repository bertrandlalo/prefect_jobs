# TODO: think about moving this module somewhere else like iguazu.prefect.cache_validators ?
#       Maybe move iguazu.executors in it as well? Maybe not?

# TODO: change all logger.info to logger.debug when we are sure about this validator

from typing import Any, Dict
import logging

from prefect.engine.cache_validators import all_inputs, all_parameters
from prefect.engine.state import Cached


logger = logging.getLogger(__name__)


class ParametrizedValidator:

    def __init__(self, use_inputs=True, use_parameters=True, force=False):
        self.use_inputs = use_inputs
        self.use_parameters = use_parameters
        self.force = force

    def __call__(self, state: Cached, inputs: Dict[str, Any], parameters: Dict[str, Any]):
        # Never use cache when force is set
        if self.force:
            logger.debug('Cache miss: forced is set')
            return False

        # When caching with inputs and outputs, defer to the corresponding
        # prefect cache validators
        if self.use_inputs and self.use_parameters:
            input_cache = all_inputs(state, inputs, parameters)
            param_cache = all_parameters(state, inputs, parameters)
            logger.debug('Cache %s: inputs was %s, params was %s',
                         'hit' if input_cache and param_cache else 'miss',
                         input_cache, param_cache)
            return input_cache and param_cache

        elif self.use_inputs:
            input_cache = all_inputs(state, inputs, parameters)
            logger.debug('Cache %s: inputs was %s',
                         'hit' if input_cache else 'miss',
                         input_cache)
            return input_cache

        elif self.use_parameters:
            param_cache = all_parameters(state, inputs, parameters)
            logger.debug('Cache %s: parameters was %s',
                         'hit' if param_cache else 'miss',
                         param_cache)
            return param_cache

        logger.debug('Cache miss: no cache configuration set')
        return False


# def all_validator(use_inputs=True, use_parameters=True, force=False):
#     def _combine(state: Cached,
#                  inputs: Dict[str, Any],
#                  parameters: Dict[str, Any]) -> bool:
#         print('all_validator cache verification')
#         if force:
#             print('Not cached - reason = forced')
#             return False
#         elif use_inputs and use_parameters:
#             tmp = all_inputs(state, inputs, parameters) and all_parameters(state, inputs, parameters)
#             if tmp:
#                 print('Cached - reason = same inputs and parameters')
#             else:
#                 print('Not cached - reason = different inputs or parameters')
#             return tmp
#         elif use_inputs:
#             tmp = all_inputs(state, inputs, parameters)
#             if tmp:
#                 print('Cached - reason = same inputs')
#             else:
#                 print('Not cached - reason = different inputs')
#             return tmp
#         elif use_parameters:
#             tmp = all_parameters(state, inputs, parameters)
#             if tmp:
#                 print('Cached - reason = same  parameters')
#             else:
#                 print('Not cached - reason = different parameters')
#             return tmp
#         print('Not cached - reason: no configuration')
#         return False
#     return _combine


# def debug(*args, **kwargs):
#     import ipdb; ipdb.set_trace(context=21)
#     return all_inputs(*args, **kwargs)
