import bpy
import bmesh

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

