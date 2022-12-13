from pathlib import Path
import os

import lunchbox.tools as lbt
import pandas as pd
from pandas import DataFrame

from shot_glass.hifive.hifive import HiFive
from shot_glass.hifive.operator_tools import operator
from shot_glass.utils import ValidationError
import shot_glass.blender.blender_tools as blt
import shot_glass.hifive.validators as validators
import shot_glass.obj.obj_tools as obt
import shot_glass.plotly.plotly_tools as plot

import logging
LOGGER = logging.getLogger(__name__)


# JSON-OPERATORS----------------------------------------------------------------
@operator(
    fullpath=[
        validators.has_json_extension,
        validators.file_exists,
        validators.is_records_json])
def read_json(fullpath='required'):
    '''
    Read HiFive data from JSON filepath or buffer.

    Args:
        fullpath (str): Filepath of JSON data in records format.

    Returns:
        HiFive: HiFive instance with JSON data in it.
    '''
    with open(fullpath) as f:
        data = pd.read_json(path_or_buf=f, orient='records')
    data.v_x = data.v_x.astype(float)
    data.v_y = data.v_y.astype(float)
    data.v_z = data.v_z.astype(float)

    # enforce column order
    cols = ['i_id', 'f_id', 'e_id', 'v_id', 'v_x', 'v_y', 'v_z']
    extra_cols = data.columns.tolist()
    extra_cols = sorted(list(filter(lambda x: x not in cols, extra_cols)))
    cols += extra_cols
    data = data[cols]

    hifive = HiFive()
    hifive.data = data
    return hifive


@operator(
    data=[validators.is_hifive_instance],
    fullpath=[validators.has_json_extension])
def write_json(data='required', fullpath='required'):
    '''
    Write HiFive data to JSON filepath or string in records format.

    Args:
        data (HiFive): HiFive instance to be written.
        fullpath (str): Target filepath.

    Returns:
        HiFive: HiFive instance.
    '''
    data.data.to_json(fullpath, orient='records')
    LOGGER.info(f'HiFive data written to {fullpath}')
    return data


# BLENDER-OPERATORS---------------------------------------------------------
@operator(data=[validators.is_hifive_instance])
def to_blender_scene(data='required'):
    '''
    Converts a HiFive instance into a Blender scene.

    Args:
        data (HiFive): HiFive instance.

    Returns:
        bpy.types.Scene: Blender Scene instance.
    '''
    return blt.dataframe_to_scene(data.data)


@operator(scene=[validators.is_blender_scene])
def from_blender_scene(scene='required'):
    '''
    Converts a Blender Scene instance into HiFive data.

    Args:
        scene (bpy.types.Scene): Blender Scene instance.

    Returns:
        HiFive: HiFive instance.
    '''
    data = HiFive()
    data.data = blt.scene_to_dataframe(scene)
    return data


# PLOTLY-OPERATORS----------------------------------------------------------
@operator(data=[validators.is_hifive_instance])
def to_plotly_figure(data='required'):
    '''
    Create a plotly figure of mesh data. Triangulates mesh.

    Args:
        data (HiFive): HiFive instance.

    Returns:
        dict: plotly Figure dictionary with mesh data inside.
    '''
    scene = to_blender_scene(data=data)
    blt.triangulate_all_objects()
    data = from_blender_scene(scene=scene)

    hi = data.copy()
    cols = ['v_x', 'v_y', 'v_z']
    min_ = hi.data[cols].min().min()
    max_ = hi.data[cols].max().max()

    # create mesh3d
    hi.data.sort_values(['f_id', 'v_i_draw_order'], inplace=True)
    hi = hi.map(
        'v_id',
        'f_x_vals',
        lambda x: lbt.get_ordered_unique(x.tolist())
    )
    data = hi.data.copy()

    data['f_i_i'] = data.f_x_vals.apply(lambda x: x[0])
    data['f_i_j'] = data.f_x_vals.apply(lambda x: x[1])
    data['f_i_k'] = data.f_x_vals.apply(lambda x: x[2])

    cols = ['v_x', 'v_y', 'v_z', 'f_i_i', 'f_i_j', 'f_i_k']
    verts = data.groupby('v_id').first()
    faces = data.groupby('f_id')[cols].first()

    x = verts.v_x.tolist()
    y = verts.v_y.tolist()
    z = verts.v_z.tolist()
    i = faces.f_i_i.tolist()
    j = faces.f_i_j.tolist()
    k = faces.f_i_k.tolist()

    # create figure
    fig = plot.get_mesh_plot_figure(x, y, z, i, j, k, min_, max_, 1.2)
    return fig


# OBJ-OPERATORS-----------------------------------------------------------------
@operator(
    fullpath=[
        validators.has_obj_extension,
        validators.file_exists])
def read_obj(fullpath='required'):
    '''
    Reads given OBJ file.
    Creates v_i_draw_order column which preserves draw order of face
    vertices. Only vertices and faces are currently supported.

    Args:
        fullpath (str): Fullpath to OBJ file.

    Raises:
        ValidationError: If file is missing vertex id, x, y, or z data.

    Returns:
        HiFive: HiFive instance with OBJ data.
    '''
    # currently supported components
    supported_components = ['vertex', 'face']

    # parse obj file
    data = obt.parse(fullpath)
    data = DataFrame(data)

    # filter out none component lines
    mask = data.component_type.apply(lambda x: x in supported_components)
    data = data[mask]

    # rename all the columns
    def rename(column):
        lut = dict(
            x='v_x',
            y='v_y',
            z='v_z',
            vertex_id='v_id'
        )
        if column in lut.keys():
            return lut[column]
        return column

    data.rename(rename, axis=1, inplace=True)

    cols = ['v_id', 'v_x', 'v_y', 'v_z']
    for col in cols:
        if col not in data.columns:
            msg = f'OBJ file: {fullpath} is missing {col} data.'
            raise ValidationError(msg)

    # create verts
    verts = data[data.component_type == 'vertex']
    verts.v_id = verts.v_id.apply(lambda x: lbt.try_(lambda y: int(y), x))
    verts.v_x = verts.v_x.apply(lambda x: lbt.try_(lambda y: float(y), x))
    verts.v_y = verts.v_y.apply(lambda x: lbt.try_(lambda y: float(y), x))
    verts.v_z = verts.v_z.apply(lambda x: lbt.try_(lambda y: float(y), x))

    # create faces
    faces = data[data.component_type == 'face']
    faces.parts = faces.parts.apply(lambda x: [x['vertex_id'] for x in x])
    data = faces.parts.apply(obt.obj_face_to_edges).tolist()
    data = pd.concat(data, ignore_index=True)

    f_lut = {k: i for i, k in enumerate(data.f_id.unique().tolist())}
    data.f_id = data.f_id.apply(lambda x: f_lut[x])

    e_lut = {k: i for i, k in enumerate(data.e_id.unique().tolist())}
    data.e_id = data.e_id.apply(lambda x: e_lut[x])

    # merge expanded DataFrame and original vertices
    data = data.merge(verts, on='v_id')

    # assign single item id to all components
    # TODO: add proper support for different OBJ items
    data['i_id'] = 0

    # cleanup
    cols = [
        'i_id',
        'f_id',
        'e_id',
        'v_id',
        'v_x',
        'v_y',
        'v_z',
        'v_i_draw_order'
    ]
    data = data[cols]
    data.drop_duplicates(inplace=True)
    data.reset_index(drop=True, inplace=True)

    # make vertex ids start at 0 instead of 1
    data.v_id -= 1

    hifive = HiFive()
    hifive.data = data
    return hifive


@operator(
    data=[validators.is_hifive_instance],
    fullpath=[validators.has_obj_extension])
def write_obj(data='required', fullpath='required'):
    '''
    Writes data to OBJ file.

    Currently, only faces and vertices are supported. If v_i_draw_order
    column is present in data, vertices of each face will be written in
    specified order.

    Args:
        data (HiFive): HiFive data instance.
        fullpath (str): Full path to OBJ file to be written.

    Returns:
        HiFive: HiFive instance.
    '''
    hifive = data

    cols = ['v_x', 'v_y', 'v_z']
    data = hifive.data \
        .copy() \
        .dropna(subset=['v_id'] + cols) \
        .sort_values('v_id')

    vertices = data[['v_id'] + cols] \
        .drop_duplicates() \
        .apply(lambda x: 'v {} {} {}'.format(*x[cols]), axis=1) \
        .tolist()

    faces = data \
        .dropna(subset=['f_id', 'e_id']) \
        .groupby('f_id') \
        .apply(obt.row_to_obj_face) \
        .tolist()

    header = ['# Generated from HiFive data']
    vheader = ['\n# Vertices']
    fheader = ['\n# Faces']
    output = header + vheader + vertices + fheader + faces
    output = '\n'.join(output) + '\n'

    with open(fullpath, 'w') as f:
        f.write(output)

    LOGGER.info(f'HiFive data written to {fullpath}')
    return hifive


# FILE-SEQUENCE-OPERATORS-------------------------------------------------------
@operator(
    fullpath=[validators.is_file_sequence_directory],
    prefix=[validators.is_valid_column_infix]
)
def from_file_sequence(fullpath='required', infix=''):
    '''
    Generates HiFive instance with 1 row per file in given directory.

    Columns:

        * v_s_[infix]_fullpath - Fullpath to file in given directory.
        * v_z - Z value of end digits of file.

    Args:
        fullpath (str): Absolute path to directory of files.
        infix (str, optional): String to be inserted in column name. Default: ''

    Returns:
        HiFive: HiFive instance of filenames of given directory.
    '''
    filepaths = []
    for filename in sorted(os.listdir(fullpath)):
        filepaths.append(Path(fullpath, filename).absolute().as_posix())

    hifive = HiFive()
    data = hifive.data
    column = 'v_s_fullpath'
    if infix:
        column = f'v_s_{infix}_fullpath'
    data[column] = filepaths

    # assume each file name ends in a padded number indicating its z coordinate
    # example: some_header_text_0001.png
    # TODO: expand this logic into the proper viz asset system and write
    #             asset read and write operators
    data.v_z = data[column].apply(
        lambda x: float(Path(Path(x).parts[-1]).stem.split('_')[-1])
    )
    return hifive
