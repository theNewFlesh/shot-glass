import json
import os
import re

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
