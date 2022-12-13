from functools import partial

import lunchbox.tools as lbt
import wrapt

import logging
LOGGER = logging.getLogger(__name__)
# ------------------------------------------------------------------------------


'''
Contain the HiFive operator decorator function.
'''


def operator(wrapped=None, **validators):
    '''
    A decorator for functions that faciltates validation and execution logic.

    Adds these two keyword arguments to given function:

        * execute - Whether to execute the wrapped code. Default: True.
        * validate - Whether to validate the data or parameters. Options \
        include:

            * none (validate nothing)
            * parameters (validate parameters only)
            * data (validate data only)
            * all (validate parameters and data)

    Args:
        wrapped (function): For dev use. Default: None.
        \*\*validators (dict): Keyword argument and list of validation methods. # noqa: W605
            Example: filepath=[has_obj_extension,file_exists]

    Raises:
        ValueError: If keyword arg with value of 'required' is found.

    Returns:
        operator function.
    '''
    if wrapped is None:
        return partial(operator, **validators)

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        temp = lbt.get_function_signature(wrapped)['kwargs']
        temp.update(kwargs)
        kwargs = temp
        keys = sorted(kwargs.keys())

        validate = 'all'
        if 'validate' in keys:
            validate = kwargs['validate']

            modes = ['parameters', 'data', 'all', 'none']
            if validate not in modes:
                msg = f'Validate keyword must be one of {modes}. '
                msg += f'Value provided: {validate}.'
                raise ValueError(msg)

            keys.remove('validate')

        execute = True
        if 'execute' in keys:
            execute = kwargs['execute']
            keys.remove('execute')

        params = {k: kwargs[k] for k in keys}

        if 'data' in keys:
            keys.remove('data')
            keys.append('data')

        for key in keys:
            if kwargs[key] == 'required':
                msg = f'Missing required parameter: {key}.'
                raise ValueError(msg)

        if validate == 'parameters':
            keys = list(filter(lambda x: x != 'data', keys))

        if validate == 'data':
            keys = list(filter(lambda x: x == 'data', keys))

        if validate == 'none':
            keys = []

        for key in keys:
            if key in validators.keys():
                for validator in validators[key]:
                    validator(kwargs[key])

        if execute:
            LOGGER.debug(f'{wrapped} called with {params}.')
            return wrapped(**params)
    return wrapper(wrapped)
