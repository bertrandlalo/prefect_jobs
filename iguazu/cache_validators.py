# TODO: think about moving this module somewhere else like iguazu.prefect.cache_validators ?
#       Maybe move iguazu.executors in it as well? Maybe not?

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
            result = input_cache and param_cache
            logger.debug('Cache %s: inputs was %s, params was %s',
                         'hit' if result else 'miss',
                         input_cache, param_cache)

        elif self.use_inputs:
            input_cache = all_inputs(state, inputs, parameters)
            result = input_cache
            logger.debug('Cache %s: inputs was %s',
                         'hit' if result else 'miss',
                         input_cache)
            return input_cache

        elif self.use_parameters:
            param_cache = all_parameters(state, inputs, parameters)
            result = param_cache
            logger.debug('Cache %s: parameters was %s',
                         'hit' if result else 'miss',
                         param_cache)
            return param_cache
        else:
            result = False
            logger.debug('Cache miss: no cache configuration set')

        if result:
            logger.info('Cache hit!')

        return result
