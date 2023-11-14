from typing import Dict, List, Union

import json
import os
import re

from lunchbox.enforce import Enforce
import pandas as pd

from shot_glass.core.tools import ValidationError
# ------------------------------------------------------------------------------

'''
A module that contains various functions for use with the HiFive class.
Importantly, it does not contain HiFive operators.
'''


def to_snakecase(string):
    '''
    Converts a string with upper case letters, such as camelCase, to a
    snake_case string.

    Args:
        string (str): String to be converted.

    Returns:
        str: snake_case string.
    '''
    output = re.sub('([^_])([A-Z][a-z]+)', r'\1_\2', string)
    output = re.sub('([a-z0-9])([A-Z])', r'\1_\2', output).lower()
    output = re.sub(r'\.', '_', output)
    output = re.sub(' +', '_', output)
    output = re.sub('__+', '_', output)
    return output
# ------------------------------------------------------------------------------


def is_string(value):
    '''
    Tests whether or not a given value is a string or is null.

    Args:
        value (object): Value to be tested.

    Returns:
        bool: Result.
    '''
    if pd.isnull(value):
        return True
    return isinstance(value, str)


def is_json(value):
    '''
    Tests whether or not a given value is a valid json string or is null.

    Args:
        value (object): Value to be tested.

    Returns:
        bool: Result.
    '''
    if pd.isnull(value):
        return True
    try:
        json.loads(value)
        return True
    except Exception:
        return False


def is_float(value):
    '''
    Tests whether or not a given value is a float or is null.

    Args:
        value (object): Value to be tested.

    Returns:
        bool: Result.
    '''
    if pd.isnull(value):
        return True
    return isinstance(value, float)


def is_integer(value):
    '''
    Tests whether or not a given value is an integer or is null.

    Args:
        value (object): Value to be tested.

    Returns:
        bool: Result.
    '''
    if pd.isnull(value):
        return True
    return isinstance(value, int)


def is_natural_number(value):
    '''
    Tests whether or not a given value is a natural number or is null.

    Args:
        value (object): Value to be tested.

    Returns:
        bool: Result.
    '''
    if pd.isnull(value):
        return True
    if is_integer(value):
        return value >= 0
    return False


def get_nunique_a_per_b(data, a, b):
    '''
    Gets the number of unique elements in column a per column b.

    Args:
        data (DataFrame): DataFrame with column a and b.
        a (str): Name of column a.
        b (str): Name of column b.

    Returns:
        int: Count of unique elements.
    '''
    return data[[a, b]] \
        .dropna() \
        .groupby(b)[a] \
        .agg(lambda x: x.nunique()) \
        .tolist()


def validate_file_extension(filepath, extension):
    '''
    Validates given file path extension according to given extension.

    Args:
        filepath (str): Path to a file.
        extension (str): File extension.

    Raises:
        ValidationError: If file extension does not match.
    '''
    _, ext = os.path.splitext(filepath)
    ext = ext[1:]
    if ext != extension:
        msg = f'Expected extension: {extension}, found: {ext}.'
        raise ValidationError(msg)


# GEOMETRY----------------------------------------------------------------------
def fold_vertex(vertex_ids, components):
    # type: (List[int], Union[list, dict]) -> Dict[int, dict]
    '''
    Combine vertex id and components into a single dictionary object.

    Args:
        vertex_ids (list[int]): List of vertex ids
        components (list): Vertex compoenents.

    Raises:
        EnforceError: If vertex_ids is not a list of a single integer.
        EnforceError: If components is not a dictionary or list.

    Returns:
        dict: Vertex dictionary.
    '''
    # vertex_ids
    msg = 'vertex_ids must be a list containing a single integer. '
    msg += f'Given value: {vertex_ids}.'
    Enforce(vertex_ids, 'instance of', list, message=msg)
    Enforce(len(vertex_ids), '==', 1, message=msg)
    Enforce(vertex_ids[0], 'instance of', int, message=msg)

    # components
    if isinstance(components, tuple):
        components = list(components)
    if isinstance(components, list):
        components = dict(zip(list('xyz'), components))
    Enforce(components, 'instance of', dict)
    # --------------------------------------------------------------------------

    return {vertex_ids[0]: components}


def fold(ids, components):
    # type: (List[int], list) -> Dict[int, dict]
    '''
    Combine id and components into a single dictionary object.

    Args:
        ids (list[int]): List of ids
        components (list): Vertex compoenents.

    Raises:
        EnforceError: If ids is not a list of a single integer.
        EnforceError: If components is not a dictionary or list.

    Returns:
        dict: Vertex dictionary.
    '''
    # ids
    msg = 'ids must be a list containing a single integer. '
    msg += f'Given value: {ids}.'
    Enforce(ids, 'instance of', list, message=msg)
    Enforce(len(ids), '==', 1, message=msg)
    Enforce(ids[0], 'instance of', int, message=msg)

    # components
    if isinstance(components, tuple):
        components = list(components)
    if isinstance(components, list):
        components = dict(zip(list('xyz'), components))
    Enforce(components, 'instance of', dict)
    # --------------------------------------------------------------------------

    return {ids[0]: components}
