from shot_glass.core.types import Filepath  # noqa F401

from pathlib import Path
from tempfile import TemporaryDirectory

import bpy
import bmesh
import lunchbox.tools as lbt
import mathutils
import pandas as pd
from pandas import DataFrame

import shot_glass.hifive.validators as validators

import logging
LOGGER = logging.getLogger(__name__)


# SCENE-FUNCTIONS---------------------------------------------------------------
def set_scene(scene):
    '''
    Set's Blender's scene context ot given scene

    scene - Blender scene object.
    '''
    bpy.context.window.scene = scene


def delete_scene(scene):
    '''
    Deletes given scene from Blender.

    scene - Blender scene.
    '''
    set_scene(scene)
    bpy.ops.scene.delete()
    LOGGER.debug('Scene deleted.')


def delete_all_scenes():
    '''
    Destroys all Blender scenes and creates a new empty one.
    '''
    for scene in bpy.data.scenes[:-1]:
        set_scene(scene)
        delete_all_objects()
        delete_scene(scene)

    old_scene = bpy.data.scenes[0]
    set_scene(old_scene)
    delete_all_objects()

    bpy.ops.scene.new(type='EMPTY')
    scene = bpy.data.scenes[-1]
    set_scene(scene)
    delete_all_objects()

    set_scene(old_scene)
    delete_all_objects()
    delete_scene(old_scene)

    bpy.data.scenes[0].name = 'Scene'
    LOGGER.debug('All scenes deleted.')


# MODE-FUNCTIONS----------------------------------------------------------------
def activate_edit_mode():
    '''
    Set Blender interaction mode to edit.
    '''
    bpy.ops.object.mode_set(mode='EDIT')
    LOGGER.debug('Edit mode active.')


def activate_object_mode():
    '''
    Set Blender interaction mode to object.
    '''
    bpy.ops.object.mode_set(mode='OBJECT')
    LOGGER.debug('Object mode active.')


# OBJECT-FUNCTIONS-----------------------------------------------------------
def select_object(object_):
    '''
    Selects given Blender object.

    Args:
        object_ (bpy object): Blender object to be selected.
    '''
    object_.select_set(True)
    bpy.context.view_layer.objects.active = object_


def deselect_object(object_):
    '''
    Deselect given Blender object.

    Args:
        object_ (bpy object): Blender object to be deselecoted.
    '''
    object_.select_set(False)


def select_all_objects():
    '''
    Selects all objects within current Blender scene.
    '''
    for obj in bpy.context.scene.objects:
        select_object(obj)


def deselect_all_objects():
    '''
    Deselect all objects within current Blender scene.
    '''
    for obj in bpy.context.scene.objects:
        deselect_object(obj)
    bpy.context.view_layer.objects.active = None


def filter_select_objects(pattern):
    '''
    Clears selected objects and then selects Blender objects according to given
    pattern.

    Args:
        pattern (str): Glob pattern of object name.
    '''
    deselect_all_objects()
    bpy.ops.object.select_pattern(pattern=pattern, case_sensitive=True)


def delete_object(object_):
    '''
    Deletes given object_.

    Args:
        object_ (bpy.types.Object): Blender object to be deleted.
    '''
    deselect_all_objects()
    select_object(object_)
    bpy.ops.object.delete()


def delete_all_objects():
    '''
    Deletes all objects within current scene.
    '''
    deselect_all_objects()
    select_all_objects()
    bpy.ops.object.delete()


def filter_objects(object_type):
    '''
    Filters Blender objects by object type.

    Args:
        object_type (str): Type of Blender object.

    Returns:
        list: List of all Blender objects of given type.
    '''
    return list(filter(
        lambda x: x.type == object_type.upper(), bpy.context.scene.objects
    ))


# FACE-FUNCTIONS---------------------------------------------------------------
def select_faces(object_, indices):
    '''
    Select faces on given Blender mesh object according to according to given
    face indices.

    Args:
        object_ (bpy object): Blender object with faces to be selected.
        indices (list): List of integers.
    '''
    deselect_all_objects()
    select_object(object_)
    activate_edit_mode()
    bpy.ops.mesh.select_mode(type='FACE')
    mesh = bmesh.from_edit_mesh(object_.data)
    mesh.faces.ensure_lookup_table()
    for i in indices:
        mesh.faces[i].select = True
    object_.data.update()


def deselect_faces(object_, indices):
    '''
    Deselect faces on given Blender mesh object according to according to given
    face indices.

    Args:
        object_ (bpy object): Blender object with faces to be deselected.
        indices (list): List of integers.
    '''
    deselect_all_objects()
    select_object(object_)
    activate_edit_mode()
    bpy.ops.mesh.select_mode(type='FACE')
    mesh = bmesh.from_edit_mesh(object_.data)
    mesh.faces.ensure_lookup_table()
    for i in indices:
        mesh.faces[i].select = False
    object_.data.update()


def select_all_faces(object_):
    '''
    Select all faces of the given Blender mesh object.

    Args:
        object_ (bpy object): Blender object with faces to be selected.
    '''
    deselect_all_objects()
    select_object(object_)
    activate_edit_mode()
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='SELECT')


def deselect_all_faces(object_):
    '''
    Deselect all faces of the given Blender mesh object.

    Args:
        object_ (bpy object): Blender object with faces to be selected.
    '''
    deselect_all_objects()
    select_object(object_)
    activate_edit_mode()
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.select_all(action='DESELECT')


def triangulate_faces(object_):
    '''
    Triangulate currenly selected faces of given Blender mesh object.

    Args:
        object_ (bpy object): Blender object with faces preselected for
            triangulation.
    '''
    activate_edit_mode()
    bpy.ops.mesh.quads_convert_to_tris()
    activate_object_mode()


def triangulate_all_objects():
    '''
    Triangulates all faces of all objects with current Blender scene.
    '''
    for obj in filter_objects('mesh'):
        select_object(obj)
        triangulate_faces(obj)


# DATAFRAME-FUNCTIONS-----------------------------------------------------------
def mesh_to_dataframe(mesh):
    '''
    Converts a given Blender mesh object into a DataFrame.

    Args:
        mesh (bpy mesh): Blender object of type MESH.

    Raises:
        ValidationError: If given mesh is not of object type MESH.
        ValidationError: If given mesh.name is not coercible to int.

    Returns:
        DataFrame: DataFrame of mesh data.
    '''
    validators.is_blender_mesh(mesh)
    validators.has_valid_mesh_name(mesh)

    # vertices
    verts = []
    for vert in mesh.data.vertices:
        # convert vertex coordinates to worldspace
        val = (mesh.matrix_world @ vert.co).xyz
        verts.append([vert.index, val[0], val[1], val[2]])
    verts = DataFrame(verts, columns=['v_id', 'v_x', 'v_y', 'v_z'])

    # edges
    edges = []
    for edge in mesh.data.edges:
        for vert in edge.vertices:
            edges.append([edge.index, vert])
    edges = DataFrame(edges, columns=['e_id', 'v_id'])

    # faces
    faces = []
    for face in mesh.data.polygons:
        for order, vert in enumerate(face.vertices):
            faces.append([face.index, vert, order])
    faces = DataFrame(faces, columns=['f_id', 'v_id', 'v_i_draw_order'])

    # data
    data = pd.merge(verts, edges, on='v_id')
    data = pd.merge(data, faces, on='v_id')
    data['i_id'] = int(mesh.name)

    # enforce row order
    data.sort_values(
        ['i_id', 'f_id', 'e_id', 'v_i_draw_order'],
        inplace=True
    )
    data.reset_index(drop=True, inplace=True)

    return data


def scene_to_dataframe(scene):
    '''
    Converts given Blender scene into a DataFrame.

    Args:
        scene (bpy.types.Scene): Blender scene object.

    Returns:
        DataFrame: DataFrame of all mesh data of scene.
    '''
    set_scene(scene)

    data = []
    for mesh in filter_objects('MESH'):
        datum = mesh_to_dataframe(mesh)
        data.append(datum)
    data = pd.concat(data)

    # faces, edges and vertices are indexed relative to objects (objects) in
    # blender the following makes them unique to all objects
    # assumes unique ids of objects
    i_lut = sorted(data.i_id.unique().tolist())
    i_lut = {k: i for i, k in enumerate(i_lut)}
    data.i_id = data.i_id.apply(lambda x: i_lut[x])

    data.f_id = data.i_id.astype(str) + data.f_id.astype(str)
    f_lut = sorted(data.f_id.unique().tolist())
    f_lut = {k: i for i, k in enumerate(f_lut)}
    data.f_id = data.f_id.apply(lambda x: f_lut[x])

    data.e_id = data.i_id.astype(str) + data.e_id.astype(str)
    e_lut = sorted(data.e_id.unique().tolist())
    e_lut = {k: i for i, k in enumerate(e_lut)}
    data.e_id = data.e_id.apply(lambda x: e_lut[x])

    data.v_id = data.i_id.astype(str) + data.v_id.astype(str)
    v_lut = sorted(data.v_id.unique().tolist())
    v_lut = {k: i for i, k in enumerate(v_lut)}
    data.v_id = data.v_id.apply(lambda x: v_lut[x])

    # enforce row order
    data.sort_values(
        ['i_id', 'f_id', 'e_id', 'v_i_draw_order'],
        inplace=True
    )
    data.reset_index(drop=True, inplace=True)

    return data


def mesh_to_pydata(mesh):
    '''
    Converts a given Blender mesh in to a tuple of vertices, edges and faces.

    Args:
        mesh (bpy mesh): Blender mesh object.

    Returns:
        tuple: (vertices, edges, faces).
    '''
    verts = list(map(lambda x: list(x.co), mesh.data.vertices.values()))

    edges = mesh.data.edge_keys
    edges = sorted([sorted(list(x)) for x in edges])

    faces = list(map(lambda x: list(x.vertices), mesh.data.polygons.values()))

    return (verts, edges, faces)


def dataframe_to_pydata(data):
    '''
    Converts a DataFrame into a tuple of vertices, edges and faces consumed by the
    Blender mesh from_pydata method.

    Args:
        data (DataFrame): DataFrame of single mesh data.

    Raises:
        ValidationError: If required columns are do not exist or are invalid.

    Returns:
        tuple: (vertices, edges, faces).
    '''
    validators.mesh_dataframe_columns_exist(data)
    validators.mesh_dataframe_columns_are_valid(data)
    data = data.copy()

    # index face, edge and vertex ids relative to mesh
    f_lut = sorted(data.f_id.unique().tolist())
    f_lut = {k: i for i, k in enumerate(f_lut)}
    data.f_id = data.f_id.apply(lambda x: f_lut[x])

    e_lut = sorted(data.e_id.unique().tolist())
    e_lut = {k: i for i, k in enumerate(e_lut)}
    data.e_id = data.e_id.apply(lambda x: e_lut[x])

    v_lut = sorted(data.v_id.unique().tolist())
    v_lut = {k: i for i, k in enumerate(v_lut)}
    data.v_id = data.v_id.apply(lambda x: v_lut[x])

    verts = data \
        .sort_values('v_id') \
        .drop_duplicates(subset=['v_id']) \
        .apply(lambda x: mathutils.Vector([x.v_x, x.v_y, x.v_z]), axis=1) \
        .tolist()

    edges = data \
        .sort_values('e_id') \
        .groupby('e_id') \
        .v_id.agg(lambda x: sorted(x.unique().tolist())) \
        .tolist()
    edges = sorted(edges)

    faces = data \
        .sort_values(['f_id', 'v_i_draw_order']) \
        .groupby('f_id') \
        .v_id.agg(lambda x: lbt.get_ordered_unique(x.tolist())) \
        .tolist()

    return (verts, edges, faces)


def dataframe_to_mesh(data):
    '''
    Converts a DataFrame for a single mesh into a Blender mesh object.

    Args:
        data (DataFrame): DataFrame of single mesh data.

    Raises:
        ValidationError: If required columns are do not exist or are invalid.

    Returns:
        bpy mesh: Blender mesh object.
    '''
    # create object
    name = str(data.i_id.astype(int).head(1).item())
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    obj.show_name = True

    # link object to collection
    # without this the object cannot be deleted
    bpy.context.collection.objects.link(obj)

    # add mesh data to object
    pydata = dataframe_to_pydata(data)

    # TODO: fix this degenerate edge problem.
    # Seemingly correct pydata produces degenerate geometry missing one edge
    # faces. Faces seems to compete with edges in some way. So, leaving out
    # edges for now.
    verts, edges, faces = pydata

    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj


def dataframe_to_scene(data):
    '''
    Converts a DataFrame of mesh data of a Blender scene into a Blender scene.

    Args:
        data (DataFrame): DataFrame of mesh data.

    Returns:
        bpy.types.Scene: Blender scene.
    '''
    delete_all_scenes()
    for i_id in data.i_id.unique().tolist():
        item = data[data.i_id == i_id]
        dataframe_to_mesh(item)
    return bpy.context.scene


# IO-FUNCTIONS------------------------------------------------------------------
def read_mesh(filepath):
    # type: (Filepath) -> None
    '''
    Read mesh from given filepath.
    The following formats are supported:

        * abc
        * dae
        * fbx
        * glb
        * obj
        * stl
        * usd
        * usdc
        * usdz

    Args:
        filepath (str): Path to mesh file.

    Raises:
        AssertionError: If file is not found.
        ValueError: If file extension is unknown.
    '''
    source = Path(filepath).as_posix()
    assert Path(source).is_file(), f'File not found: {source}'

    ext = Path(source).suffix[1:]
    match ext:
        case 'abc':
            bpy.ops.wm.alembic_import(filepath=source, filter_glob='*.abc')
        case 'dae':
            bpy.ops.wm.collada_import(filepath=source, filter_glob='*.dae')
        case 'fbx':
            bpy.ops.import_scene.fbx(filepath=source, filter_glob='*.fbx')
        case 'glb':
            bpy.ops.import_scene.gltf(filepath=source, filter_glob='*.glb')
        case 'obj':
            bpy.ops.wm.obj_import(filepath=source, filter_glob='*.obj')
        case 'stl':
            bpy.ops.wm.stl_import(filepath=source, filter_glob='*.stl')
        case 'usd' | 'usdc' | 'usdz':
            bpy.ops.wm.usd_import(filepath=source, filter_glob='*.usd')
        case _:
            raise ValueError(f'Unknown file extension: {ext}.')

    LOGGER.debug(f'Read: {source}')


def write_mesh(filepath):
    # type: (Filepath) -> None
    '''
    Write scene to mesh file.
    The following formats are supported:

        * abc
        * fbx
        * glb
        * obj
        * stl
        * usd
        * usdc
        * usdz

       Args:
           filepath (str): Target filepath.

       Raises:
           ValueError: If file extension is unknown.
    '''
    target = Path(filepath).as_posix()
    ext = Path(target).suffix[1:]
    match ext:
        case 'abc':
            bpy.ops.wm.alembic_export(filepath=target)
        case 'fbx':
            bpy.ops.export_scene.fbx(filepath=target)
        case 'glb':
            bpy.ops.export_scene.gltf(filepath=target, export_materials='PLACEHOLDER')
        case 'obj':
            bpy.ops.wm.obj_export(filepath=target, export_materials=False)
        case 'stl':
            bpy.ops.wm.stl_export(filepath=target)
        case 'usd' | 'usdc' | 'usdz':
            bpy.ops.wm.usd_export(filepath=target, export_materials=False)
        case _:
            raise ValueError(f'Unknown file extension: {ext}.')

    LOGGER.debug(f'Wrote: {target}')


def convert_mesh(content, source_format, target_format):
    # type: (bytes, str, str) -> bytes
    '''
    Converts a given mesh from a source format to a target format.
    The following formats are supported:

        * abc
        * dae
        * fbx
        * glb
        * obj
        * stl
        * usd
        * usdc
        * usdz

    Args:
        content (bytes): File content.
        source_format (str): Source file format.
        target_format (str): Target file format.

    Returns:
        bytes: Target file as bytes.
    '''
    delete_all_scenes()

    with TemporaryDirectory(prefix='shot-glass_') as root:
        source = Path(root, f'source.{source_format}')
        with open(source, 'wb') as f:
            f.write(content)
        read_mesh(source)

        target = Path(root, f'target.{target_format}')
        write_mesh(target)
        with open(target, 'rb') as f:
            output = f.read()

    return output
