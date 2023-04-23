import bpy
import json
import os
from pathlib import Path

from shot_glass.hifive.hifive import HiFive
from shot_glass.core.tools import ValidationError
# ------------------------------------------------------------------------------


'''
The hifive validators module is a library of validation functions used by
HiFive operators, for validating HiFive data and parameters. All functions raise
ValidationError.
'''

LEGAL_COLUMN_CHARACTERS = 'abcdefghijklmnopqrstuvwxyz0123456789_'


def file_exists(fullpath):
    '''
    Args:
        fullpath (str): Full path to file on disk.

    Raises:
        ValidationError: If file does not exist.
    '''
    if not os.path.exists(fullpath):
        msg = f'{fullpath} does not exist.'
        raise ValidationError(msg)


def has_obj_extension(fullpath):
    '''
    Args:
        fullpath (str): Full path to file.

    Raises:
        ValidationError: If given filepath does not have an obj extension.
    '''
    _, ext = os.path.splitext(fullpath)
    if ext[1:] != 'obj':
        msg = f'{fullpath} does not have an obj extension.'
        raise ValidationError(msg)


def has_json_extension(fullpath):
    '''
    Args:
        fullpath (str): Full path to file.

    Raises:
        ValidationError: If given filepath does not have a json extension.
    '''
    _, ext = os.path.splitext(fullpath)
    if ext[1:] != 'json':
        msg = f'{fullpath} does not have a json extension.'
        raise ValidationError(msg)


def is_hifive_instance(item):
    '''
    Args:
        item (object): Object to be tested.

    Raises:
        ValidationError: If given item is not a HiFive instance.
    '''
    # isinstance(item, HiFive) doesn't work for some reason, so this is needed.
    if item.__class__.__name__ != HiFive.__name__:
        msg = f'{item.__class__.__name__} is not a HiFive instance.'
        raise ValidationError(msg)


def is_records_json(fullpath):
    '''
    Args:
        fullpath (str): Full path to JSON file.

    Raises:
        ValidationError: If given JSON filepath is not in records format.
    '''
    msg = f'{fullpath} is not in valid json records format.'

    with open(fullpath) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            raise ValidationError(msg)

    if not isinstance(data, list):
        raise ValidationError(msg)

    if len(data) > 0:
        if not isinstance(data[0], dict):
            raise ValidationError(msg)


def is_blender_scene(item):
    '''
    Args:
        item (object): Object to be tested.

    Raises:
        ValidationError: If given item is not a Blender scene.
    '''
    if not isinstance(item, bpy.types.Scene):
        msg = f'{item} is not a Blender Scene instance.'
        raise ValidationError(msg)


def is_blender_object(item):
    '''
    Args:
        item (object): Object to be tested.

    Raises:
        ValidationError: If given item is not a Blender object.
    '''
    if not isinstance(item, bpy.types.Object):
        msg = f'{item} is not a Blender Object.'
        raise ValidationError(msg)


def is_blender_mesh(item):
    '''
    Args:
        item (object): Object to be tested.

    Raises:
        ValidationError: If given item is not a Blender mesh object.
    '''
    is_blender_object(item)
    if item.type != 'MESH':
        msg = f'Object type is {item.type}. Only MESH is supported.'
        raise ValidationError(msg)


def has_valid_mesh_name(item):
    '''
    Args:
        item (object): Object to be tested.

    Raises:
        ValidationError: If given item's name attribute is not  coercible into
            an integer.
    '''
    try:
        int(item.name)
    except ValueError:
        msg = f'Mesh name must be coercible to int. Found: {item.name}'
        raise ValidationError(msg)


def mesh_dataframe_columns_exist(data):
    '''
    Args:
        data (DataFrame): DataFrame to be tested.

    Raises:
        ValidationError: If necessary columns for creating a Blender mesh do
        not exist within given DataFrame.
    '''
    cols = [
        'v_id',
        'v_x',
        'v_y',
        'v_z',
        'e_id',
        'f_id',
        'v_i_draw_order',
        'i_id'
    ]
    cols = sorted(list(set(cols).difference(data.columns.tolist())))
    if len(cols) != 0:
        msg = f'{cols} not found in columns.'
        raise ValidationError(msg)


def __has_valid_columns(data, columns, type_str, descriptor):
    '''
    Args:
        data (DataFrame): DataFrame.
        columns (list): Columns to be tested.
        type_str (str): String indicating type ('i', 'f').
        descriptor (str): English plural of type for error message \
            ('integers','strings').

    Raises:
        ValidationError: If given columns of given DataFrame are not of the type
            indicated by the given type_str.
    '''
    bad_cols = [(col, data[col].dtype.kind) for col in columns]
    bad_cols = list(filter(lambda x: x[1] != type_str, bad_cols))
    if len(bad_cols) != 0:
        bad_cols = sorted(bad_cols)
        types = [x[1] for x in bad_cols]
        bad_cols = [x[0] for x in bad_cols]

        msg = f'Columns {bad_cols} must consist of {descriptor} only. '
        msg += f'Types found: {types}'
        raise ValidationError(msg)


def mesh_dataframe_columns_are_valid(data):
    '''
    Args:
        data (DataFrame): DataFrame to be tested.

    Raises:
        ValidationError: If integer or float columns of given DataFrame have
            non-ints or non-floats in them respectively.
    '''
    cols = ['v_id', 'e_id', 'f_id', 'v_i_draw_order', 'i_id']
    __has_valid_columns(data, cols, 'i', 'integers')

    cols = ['v_x', 'v_y', 'v_z']
    __has_valid_columns(data, cols, 'f', 'floats')


def is_file_sequence_directory(fullpath):
    # does fullpath exist
    if not Path(fullpath).exists():
        msg = f'{fullpath} does not exist.'
        raise ValidationError(msg)

    # is fullpath a directory
    elif not Path(fullpath).is_dir():
        msg = f'{fullpath} is not a directory.'
        raise ValidationError(msg)

    # get full file names
    files = sorted(os.listdir(fullpath))
    files = map(lambda x: Path(fullpath, x), files)
    files = list(files)

    # does fullpath contain only files
    not_files = list(filter(lambda x: not x.is_file(), files))
    if len(not_files) > 0:
        files = [x.absolute().as_posix() for x in not_files]
        msg = f'{files} are not files.'
        raise ValidationError(msg)

    # do any of the fullpath files have bad z coordinates
    bad_coords = []
    bad_files = []
    for file_ in files:
        z_coord = file_.stem.split('_')[-1]
        try:
            int(z_coord)
        except ValueError:
            bad_coords.append(z_coord)
            bad_files.append(file_.absolute().as_posix())

    if len(bad_coords) > 0:
        msg = f'Directory {fullpath} has files with bad z coordinates.'
        msg += f' Bad z coordinates: {sorted(bad_coords)}. '
        msg += f'Bad files: {bad_files}'
        raise ValidationError(msg)


def is_valid_column_infix(infix):
    '''
    Args:
        infix (str): String to be tested.

    Raises:
        ValidationError: If given string is a valid infix for a HiFive object.
    '''
    if infix.startswith('_'):
        msg = f'Infixes may not start with an "_". Infix given: {infix}'
        raise ValidationError(msg)

    elif infix.endswith('_'):
        msg = f'Infixes may not end with an "_". Infix given: {infix}'
        raise ValidationError(msg)

    chars = set(infix).difference(set(LEGAL_COLUMN_CHARACTERS))
    if len(chars) > 0:
        chars = sorted(list(chars))
        msg = f'Infix contains the illegal characters: {chars}. '
        msg += f'Infix given: {infix}'
        raise ValidationError(msg)
