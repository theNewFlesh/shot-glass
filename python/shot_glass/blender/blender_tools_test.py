import unittest

import bpy
import bmesh
from pandas import DataFrame
import pytest

import shot_glass.blender.blender_tools as blt
from shot_glass.core.tools import ValidationError
# ------------------------------------------------------------------------------


class BlenderToolsTests(unittest.TestCase):
    def setup_method(self, method):
        blt.delete_all_scenes()

    def create_cube(self):
        bpy.ops.mesh.primitive_cube_add()
        bpy.data.objects[-1].name = '0'

    def test_set_scene(self):
        bpy.ops.scene.new(type='EMPTY')
        scene = bpy.data.scenes[-1]
        blt.set_scene(scene)
        self.assertEqual(bpy.context.window.scene, scene)

    def test_delete_scene(self):
        bpy.ops.scene.new(type='EMPTY')
        scene = bpy.data.scenes[-1]
        name = scene.name
        blt.delete_scene(scene)
        result = len(bpy.data.scenes)
        self.assertEqual(result, 1)

        result = bpy.data.scenes[0].name
        self.assertNotEqual(result, name)

    def test_delete_all_scenes(self):
        bpy.ops.scene.new()
        bpy.ops.mesh.primitive_cube_add()
        scene = bpy.data.scenes[-1]
        scene.name = 'foo'
        blt.delete_all_scenes()

        result = len(bpy.data.scenes)
        self.assertEqual(result, 1)

        result = bpy.data.scenes[0].name
        self.assertEqual(result, 'Scene')

        result = len(bpy.data.objects)
        self.assertEqual(result, 0)

    # def test_activate_edit_mode(self):
    #     bpy.ops.mesh.primitive_cube_add()
    #     bpy.ops.object.mode_set(mode='EDIT')
    #     blt.activate_edit_mode()
    #     result = bpy.context.objects.mode
    #     self.assertEqual(result, 'EDIT')

    #     bpy.ops.object.mode_set(mode='OBJECT')
    #     blt.activate_edit_mode()
    #     result = bpy.context.objects.mode
    #     self.assertEqual(result, 'EDIT')

    # def test_activate_object_mode(self):
    #     bpy.ops.object.mode_set(mode='OBJECT')
    #     blt.activate_object_mode()
    #     result = bpy.context.objects.mode
    #     self.assertEqual(result, 'OBJECT')

    #     bpy.ops.object.mode_set(mode='EDIT')
    #     blt.activate_object_mode()
    #     result = bpy.context.objects.mode
    #     self.assertEqual(result, 'OBJECT')

    def test_deselect_all_objects(self):
        bpy.ops.mesh.primitive_cube_add()
        result = len(list(bpy.context.selected_objects))
        self.assertEqual(result, 1)

        blt.deselect_all_objects()
        result = list(bpy.context.selected_objects)
        self.assertEqual(result, [])

    def test_select_object(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_1 = bpy.context.scene.objects[-1]

        bpy.ops.mesh.primitive_cube_add()
        cube_2 = bpy.context.scene.objects[-1]

        bpy.context.selected_objects.append(cube_1)
        bpy.context.selected_objects.append(cube_2)

        for obj in bpy.context.scene.objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = None

        blt.select_object(cube_1)
        result = list(bpy.context.selected_objects)
        expected = [cube_1]
        self.assertEqual(result, expected)

    def test_deselect_object(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.scene.objects[-1]

        bpy.ops.mesh.primitive_monkey_add()
        monkey = bpy.context.scene.objects[-1]

        for obj in bpy.context.scene.objects:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        blt.deselect_object(monkey)

        self.assertFalse(monkey.select_get())
        self.assertTrue(cube.select_get())
        result = bpy.context.view_layer.objects.active
        self.assertEqual(result, monkey)

    def test_filter_select_objects(self):
        bpy.ops.mesh.primitive_cube_add()
        cube_1 = bpy.context.scene.objects[0]
        cube_1.name = 'foo1'

        bpy.ops.mesh.primitive_cube_add()
        cube_2 = bpy.context.scene.objects[1]
        cube_2.name = 'foo2'

        bpy.ops.mesh.primitive_cube_add()
        cube_3 = bpy.context.scene.objects[2]
        cube_3.name = 'bar'

        blt.filter_select_objects('foo*')
        result = list(bpy.context.selected_objects)
        self.assertIn(cube_1, result)
        self.assertIn(cube_2, result)
        self.assertNotIn(cube_3, result)
        self.assertEqual(len(result), 2)

    def test_select_all_objects(self):
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.mesh.primitive_cube_add()
        result = len(list(bpy.context.selected_objects))
        self.assertEqual(result, 1)

        blt.select_all_objects()
        result = len(list(bpy.context.selected_objects))
        self.assertEqual(result, 3)

    def test_delete_object(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.scene.objects[-1]
        blt.delete_object(cube)
        self.assertNotIn(cube, list(bpy.context.scene.objects))
        self.assertNotIn(cube, list(bpy.data.objects))

    def test_delete_all_objects(self):
        bpy.ops.mesh.primitive_cube_add()
        blt.delete_all_objects()

        result = len(bpy.context.scene.objects)
        self.assertEqual(result, 0)

        result = len(bpy.data.objects)
        self.assertEqual(result, 0)

    def test_filter_objects(self):
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.mesh.primitive_cube_add()
        expected = list(bpy.context.scene.objects)
        bpy.ops.surface.primitive_nurbs_surface_sphere_add()
        result = blt.filter_objects('mesh')
        self.assertEqual(result, expected)

    def test_select_all_faces(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.scene.objects[-1]

        bpy.ops.mesh.primitive_monkey_add()
        monkey = bpy.context.scene.objects[-1]

        for obj in bpy.data.objects:
            obj.select_set(False)
        cube.select_set(True)
        bpy.context.view_layer.objects.active = cube

        blt.select_all_faces(cube)

        result = cube.mode
        expected = 'EDIT'
        self.assertEqual(result, expected)

        bm = bmesh.from_edit_mesh(cube.data)
        result = bm.select_mode.pop()
        expected = 'FACE'
        self.assertEqual(result, expected)

        result = [x.select for x in bm.faces]
        result = set(result)
        expected = {True}
        self.assertEqual(result, expected)

        result = monkey.mode
        expected = 'OBJECT'
        self.assertEqual(result, expected)

    def test_select_faces(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.scene.objects[-1]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='DESELECT')

        expected = [1, 2, 3]
        blt.select_faces(cube, expected)

        mesh = bmesh.from_edit_mesh(cube.data)
        mesh.faces.ensure_lookup_table()

        result = []
        for face in mesh.faces:
            if face.select:
                result.append(face.index)
        self.assertListEqual(result, expected)

        bpy.ops.object.mode_set(mode='OBJECT')

    def test_deselect_faces(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.scene.objects[-1]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='SELECT')

        expected = [1, 2, 3]
        blt.deselect_faces(cube, expected)

        mesh = bmesh.from_edit_mesh(cube.data)
        mesh.faces.ensure_lookup_table()

        result = []
        for face in mesh.faces:
            if not face.select:
                result.append(face.index)
        self.assertListEqual(result, expected)

        bpy.ops.object.mode_set(mode='OBJECT')

    def test_deselect_all_faces(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.scene.objects[-1]

        bpy.ops.mesh.primitive_monkey_add()
        monkey = bpy.context.scene.objects[-1]

        for obj in bpy.data.objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = cube

        blt.deselect_all_faces(cube)

        result = cube.mode
        expected = 'EDIT'
        self.assertEqual(result, expected)

        bm = bmesh.from_edit_mesh(cube.data)
        result = bm.select_mode.pop()
        expected = 'FACE'
        self.assertEqual(result, expected)

        result = [x.select for x in bm.faces]
        result = set(result)
        expected = {False}
        self.assertEqual(result, expected)

        result = monkey.mode
        expected = 'OBJECT'
        self.assertEqual(result, expected)

    def test_triangulate_faces(self):
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.scene.objects[-1]

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.mesh.select_all(action='DESELECT')

        mesh = bmesh.from_edit_mesh(cube.data)
        mesh.faces.ensure_lookup_table()
        for i in range(3):
            mesh.faces[i].select = True
        cube.data.update()

        blt.triangulate_faces(cube)

        result = len(cube.data.polygons)
        self.assertEqual(result, 9)

    def test_triangulate_all_objects(self):
        bpy.ops.mesh.primitive_cube_add()
        cube0 = bpy.context.scene.objects[-1]

        bpy.ops.mesh.primitive_cube_add()
        cube1 = bpy.context.scene.objects[-1]

        blt.triangulate_all_objects()

        result = len(cube0.data.polygons)
        self.assertEqual(result, 12)

        result = len(cube1.data.polygons)
        self.assertEqual(result, 12)

    def test_dataframe_to_pydata(self):
        bpy.ops.mesh.primitive_cube_add()
        mesh = bpy.context.scene.objects[0]
        mesh.name = '0'
        data0 = blt.mesh_to_dataframe(mesh)
        expected = blt.dataframe_to_pydata(data0)

        name = '1'
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)

        mesh.from_pydata(*expected)
        mesh.update()

        data1 = blt.mesh_to_dataframe(obj)
        result = blt.dataframe_to_pydata(data1)

        # verts
        self.assertEqual(result[0], expected[0])
        self.assertEqual(len(result[0]), 8)

        # edges
        self.assertEqual(result[1], expected[1])
        self.assertEqual(len(result[1]), 12)

        # faces
        self.assertEqual(result[2], expected[2])
        self.assertEqual(len(result[2]), 6)

    def test_mesh_to_pydata(self):
        bpy.ops.mesh.primitive_plane_add()
        mesh = bpy.data.objects[0]
        result = blt.mesh_to_pydata(mesh)
        expected = (
            [
                [-1.0, -1.0, 0.0],
                [1.0, -1.0, 0.0],
                [-1.0, 1.0, 0.0],
                [1.0, 1.0, 0.0]
            ],
            [
                [0, 1],
                [0, 2],
                [1, 3],
                [2, 3]
            ],
            [
                [0, 1, 3, 2]
            ]
        )
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1], expected[1])
        self.assertEqual(result[2], expected[2])

    def test_mesh_to_dataframe_to_mesh(self):
        bpy.ops.mesh.primitive_cube_add()

        mesh = bpy.data.objects[0]

        with pytest.raises(ValidationError) as e:
            blt.mesh_to_dataframe(mesh)
        expected = "Mesh name must be coercible to int. Found: Cube"
        self.assertEqual(str(e.value), expected)

        mesh.name = '0'
        data = blt.mesh_to_dataframe(mesh)

        expected = blt.mesh_to_pydata(mesh)
        result = blt.dataframe_to_mesh(data)
        result = blt.mesh_to_pydata(result)

        # verts
        self.assertEqual(result[0], expected[0])
        self.assertEqual(len(result[0]), 8)

        # edges
        self.assertEqual(result[1], expected[1])
        self.assertEqual(len(result[1]), 12)

        # faces
        self.assertEqual(result[2], expected[2])
        self.assertEqual(len(result[2]), 6)

    def test_dataframe_to_mesh_to_dataframe(self):
        data = DataFrame()
        data['v_id'] = [0, 1, 1, 2, 2, 3, 3, 0]
        data['v_x'] = [0, 1, 1, 1, 1, 0, 0, 0]
        data['v_y'] = [0, 0, 0, 1, 1, 1, 1, 0]
        data['v_z'] = [0, 0, 0, 0, 0, 0, 0, 0]
        data['e_id'] = [0, 0, 1, 1, 2, 2, 3, 3]
        data['f_id'] = [0, 0, 0, 0, 0, 0, 0, 0]
        data['i_id'] = [0, 0, 0, 0, 0, 0, 0, 0]

        data.v_x = data.v_x.astype(float)
        data.v_y = data.v_y.astype(float)
        data.v_z = data.v_z.astype(float)

        with pytest.raises(ValidationError):
            blt.dataframe_to_mesh(data)

        data.v_z = data.v_z.astype(int)
        with pytest.raises(ValidationError):
            blt.dataframe_to_mesh(data)

        data.v_z = data.v_z.astype(float)

        data['v_i_draw_order'] = [0, 1, 1, 2, 2, 3, 3, 0]
        data.v_i_draw_order = data.v_i_draw_order.astype(float)
        with pytest.raises(ValidationError):
            blt.dataframe_to_mesh(data)

        # previous calls to _dataframe to mesh have populated the scene
        blt.delete_all_scenes()

        data.v_i_draw_order = data.v_i_draw_order.astype(int)
        data.sort_values(
            ['i_id', 'f_id', 'e_id', 'v_i_draw_order'],
            inplace=True
        )
        data.reset_index(drop=True, inplace=True)

        result = blt.dataframe_to_mesh(data)
        result = blt.mesh_to_dataframe(result)

        result = blt.dataframe_to_pydata(result)
        expected = blt.dataframe_to_pydata(data)

        # verts
        self.assertEqual(result[0], expected[0])
        self.assertEqual(len(result[0]), 4)

        # edges
        self.assertEqual(result[1], expected[1])
        self.assertEqual(len(result[1]), 4)

        # faces
        self.assertEqual(result[2], expected[2])
        self.assertEqual(len(result[2]), 1)

    def test_scene_to_dataframe_to_scene(self):
        bpy.ops.mesh.primitive_plane_add()
        bpy.ops.mesh.primitive_cube_add()
        scene = bpy.context.scene
        for i, obj in enumerate(list(scene.objects)):
            obj.name = str(i)
        expected = blt.scene_to_dataframe(scene)

        # expected reflects scene
        self.assertEqual(expected.i_id.nunique(), 2)
        self.assertEqual(expected[expected.i_id == 0].v_id.nunique(), 4)
        self.assertEqual(expected[expected.i_id == 1].v_id.nunique(), 8)

        scene = blt.dataframe_to_scene(expected)
        result = blt.scene_to_dataframe(scene)

        # DataFrame
        self.assertEqual(result.shape, expected.shape)
        self.assertEqual(result.columns.tolist(), expected.columns.tolist())

        # vertices
        self.assertEqual(result.v_id.min(), expected.v_id.min())
        self.assertEqual(result.v_id.max(), expected.v_id.max())
        self.assertEqual(result.v_id.nunique(), expected.v_id.nunique())

        # edges
        self.assertEqual(result.e_id.min(), expected.e_id.min())
        self.assertEqual(result.e_id.max(), expected.e_id.max())
        self.assertEqual(result.e_id.nunique(), expected.e_id.nunique())

        # faces
        self.assertEqual(result.f_id.min(), expected.f_id.min())
        self.assertEqual(result.f_id.max(), expected.f_id.max())
        self.assertEqual(result.f_id.nunique(), expected.f_id.nunique())

        # items
        self.assertEqual(result.i_id.min(), expected.i_id.min())
        self.assertEqual(result.i_id.max(), expected.i_id.max())
        self.assertEqual(result.i_id.nunique(), expected.i_id.nunique())
        self.assertEqual(result[result.i_id == 0].v_id.nunique(), 4)
        self.assertEqual(result[result.i_id == 1].v_id.nunique(), 8)

        result = blt.dataframe_to_pydata(result)
        expected = blt.dataframe_to_pydata(expected)

        # verts
        self.assertEqual(result[0], expected[0])
        self.assertEqual(len(result[0]), 12)

        # edges
        self.assertEqual(result[1], expected[1])
        self.assertEqual(len(result[1]), 16)

        # faces
        self.assertEqual(result[2], expected[2])
        self.assertEqual(len(result[2]), 7)
