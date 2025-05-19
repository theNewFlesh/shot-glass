import unittest

import bpy
import bmesh

import baas.blender.blender_tools as blt
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
