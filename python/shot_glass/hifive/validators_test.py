import json
from pathlib import Path
import os

import bpy
from pandas import DataFrame
import pytest

from tempfile import TemporaryDirectory
from shot_glass.hifive.hifive import HiFive
from shot_glass.hifive.test_base import HiFiveTestBase
import shot_glass.hifive.validators as validators
from shot_glass.core.tools import ValidationError
# ------------------------------------------------------------------------------


class HiFiveValidatorsTests(HiFiveTestBase):
    def test_file_exists(self):
        with TemporaryDirectory() as root:
            source = os.path.join(root, 'foo.bar')
            with open(source, 'w') as f:
                f.write('bar')
            validators.file_exists(source)

        with pytest.raises(ValidationError) as e:
            validators.file_exists('/foo/bar.txt')
        self.assertEqual(str(e.value), '/foo/bar.txt does not exist.')

    def test_has_obj_extension(self):
        validators.has_obj_extension('/foo/bar.obj')

        with pytest.raises(ValidationError) as e:
            validators.has_obj_extension('/foo/bar.txt')
        result = str(e.value)
        expected = '/foo/bar.txt does not have an obj extension.'
        self.assertEqual(result, expected)

    def test_has_json_extension(self):
        validators.has_json_extension('/foo/bar.json')

        with pytest.raises(ValidationError) as e:
            validators.has_json_extension('/foo/bar.txt')
        result = str(e.value)
        expected = '/foo/bar.txt does not have a json extension.'
        self.assertEqual(result, expected)

    def test_is_hifive_instance(self):
        hi = HiFive()
        validators.is_hifive_instance(hi)

        with pytest.raises(ValidationError) as e:
            validators.is_hifive_instance(92)
        result = str(e.value)
        expected = 'int is not a HiFive instance.'
        self.assertEqual(result, expected)

        with pytest.raises(ValidationError) as e:
            validators.is_hifive_instance(HiFive)
        result = str(e.value)
        expected = 'type is not a HiFive instance.'
        self.assertEqual(result, expected)

    def test_is_records_json(self):
        with TemporaryDirectory() as root:
            source = os.path.join(root, 'foo.json')
            data = [
                dict(foo='bar', boo='far'),
                dict(foo='bar', boo='far'),
            ]
            with open(source, 'w') as f:
                json.dump(data, f)

            validators.is_records_json(source)

            with open(source, 'w') as f:
                f.write('invalid json')

            expected = f'{source} is not in valid json records format.'

            with pytest.raises(ValidationError) as e:
                validators.is_records_json(source)
            self.assertEqual(str(e.value), expected)

            data = dict(foo='bar')
            with open(source, 'w') as f:
                json.dump(data, f)
            with pytest.raises(ValidationError) as e:
                validators.is_records_json(source)
            self.assertEqual(str(e.value), expected)

            data = ['not record']
            with open(source, 'w') as f:
                json.dump(data, f)
            with pytest.raises(ValidationError) as e:
                validators.is_records_json(source)
            self.assertEqual(str(e.value), expected)

    def test_is_blender_scene(self):
        bpy.ops.scene.new()
        scene = bpy.data.scenes[0]
        validators.is_blender_scene(scene)
        with pytest.raises(ValidationError) as e:
            validators.is_blender_scene('foo')
        expected = 'foo is not a Blender Scene instance.'
        self.assertEqual(str(e.value), expected)

    def test_is_blender_object(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.data.objects[0]
        validators.is_blender_object(obj)

        cam = bpy.data.cameras.new('camera')
        obj = bpy.data.objects.new('camera', cam)
        bpy.context.collection.objects.link(obj)
        validators.is_blender_object(obj)

        with pytest.raises(ValidationError) as e:
            validators.is_blender_object('foo')
        self.assertEqual(str(e.value), 'foo is not a Blender Object.')

    def test_is_blender_mesh(self):
        cam = bpy.data.cameras.new('camera')
        obj = bpy.data.objects.new('camera', cam)
        bpy.context.collection.objects.link(obj)

        with pytest.raises(ValidationError) as e:
            validators.is_blender_mesh(obj)
        self.assertEqual(
            str(e.value), 'Object type is CAMERA. Only MESH is supported.')

    def test_has_valid_mesh_name(self):
        bpy.ops.mesh.primitive_cube_add()
        mesh = bpy.data.objects[0]
        mesh.name = str(0)
        validators.has_valid_mesh_name(mesh)

        mesh.name = str(1.0)
        with pytest.raises(ValidationError) as e:
            validators.has_valid_mesh_name(mesh)
        self.assertEqual(
            str(e.value), 'Mesh name must be coercible to int. Found: 1.0')

        mesh.name = 'foo'
        with pytest.raises(ValidationError) as e:
            validators.has_valid_mesh_name(mesh)
        self.assertEqual(
            str(e.value), 'Mesh name must be coercible to int. Found: foo')

    def test_mesh_dataframe_columns_exist(self):
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
        data = DataFrame(columns=cols)
        validators.mesh_dataframe_columns_exist(data)

        del data['i_id']
        del data['v_z']
        with pytest.raises(ValidationError) as e:
            validators.mesh_dataframe_columns_exist(data)
        self.assertEqual(str(e.value), "['i_id', 'v_z'] not found in columns.")

    def test_has_valid_columns(self):
        data = DataFrame()
        data['foo'] = [1, 2, 3]
        data['bar'] = [1, 2, 3]
        cols = ['foo', 'bar']
        func = getattr(validators, '__has_valid_columns')
        func(data, cols, 'i', 'integers')

        with pytest.raises(ValidationError) as e:
            func(data, cols, 'f', 'floats')
        expected = "Columns ['bar', 'foo'] must consist of floats only."
        expected += " Types found: ['i', 'i']"
        self.assertEqual(str(e.value), expected)

        data['bar'] = [1.0, 1.0, 1.0]
        with pytest.raises(ValidationError) as e:
            func(data, cols, 'f', 'floats')
        expected = "Columns ['foo'] must consist of floats only."
        expected += " Types found: ['i']"
        self.assertEqual(str(e.value), expected)

    def test_mesh_dataframe_columns_are_valid(self):
        data = DataFrame()
        data['v_id'] = [0, 1, 2]
        data['v_x'] = [0.0, 1.0, 2.0]
        data['v_y'] = [0.0, 1.0, 2.0]
        data['v_z'] = [0.0, 1.0, 2.0]
        data['e_id'] = [0, 1, 2]
        data['f_id'] = [0, 1, 2]
        data['v_i_draw_order'] = [0, 1, 2]
        data['i_id'] = [0, 1, 2]

        validators.mesh_dataframe_columns_are_valid(data)

        data['v_z'] = [1, 2, 3]
        with pytest.raises(ValidationError) as e:
            validators.mesh_dataframe_columns_are_valid(data)
        expected = "Columns ['v_z'] must consist of floats only."
        expected += " Types found: ['i']"
        self.assertEqual(str(e.value), expected)
        data['v_z'] = [1.0, 2.0, 3.0]

        data['v_id'] = [1.0, 2.0, 3.0]
        data['f_id'] = ['a', 'b', 'c']
        with pytest.raises(ValidationError) as e:
            validators.mesh_dataframe_columns_are_valid(data)
        expected = "Columns ['f_id', 'v_id'] must consist of integers only."
        expected += " Types found: ['O', 'f']"
        self.assertEqual(str(e.value), expected)

    def test_is_file_sequence_directory(self):
        with pytest.raises(ValidationError) as e:
            validators.is_file_sequence_directory('/foo/bar')
        expected = '/foo/bar does not exist.'
        self.assertEqual(str(e.value), expected)

        with TemporaryDirectory() as root:
            files = []
            for i in range(3):
                filepath = f'foo_{i:04d}.txt'
                filepath = Path(root, filepath).absolute().as_posix()
                with open(filepath, 'w') as f:
                    f.write('bar')
                files.append(filepath)

            validators.is_file_sequence_directory(root)

            a = Path(root, 'a_dir').absolute().as_posix()
            b = Path(root, 'b_dir').absolute().as_posix()
            os.mkdir(a)
            os.mkdir(b)
            with pytest.raises(ValidationError) as e:
                validators.is_file_sequence_directory(root)
            expected = f'{[a, b]} are not files.'
            self.assertEqual(str(e.value), expected)

            with pytest.raises(ValidationError) as e:
                validators.is_file_sequence_directory(files[0])
            expected = f'{files[0]} is not a directory.'
            self.assertEqual(str(e.value), expected)

    def test_is_file_sequence_directory_bad_files(self):
        with TemporaryDirectory() as root:
            for i in range(3):
                filepath = f'foo_{i:04d}.txt'
                filepath = Path(root, filepath).absolute().as_posix()
                with open(filepath, 'w') as f:
                    f.write('bar')

            files = []
            coords = ['pizza', 'taco']
            for i in coords:
                filepath = f'foo_{i}.txt'
                filepath = Path(root, filepath).absolute().as_posix()
                with open(filepath, 'w') as f:
                    f.write('bar')
                files.append(filepath)

            with pytest.raises(ValidationError) as e:
                validators.is_file_sequence_directory(root)
            expected = f'Directory {root} has files with bad z coordinates.'
            expected += f' Bad z coordinates: {coords}.'
            expected += f' Bad files: {files}'
            self.assertEqual(str(e.value), expected)

    def test_is_valid_column_infix(self):
        validators.is_valid_column_infix('foo')
        validators.is_valid_column_infix('bar')
        validators.is_valid_column_infix('foo_bar')

        with pytest.raises(ValidationError) as e:
            validators.is_valid_column_infix('_foo')
        expected = 'Infixes may not start with an "_". Infix given: _foo'
        self.assertEqual(str(e.value), expected)

        with pytest.raises(ValidationError) as e:
            validators.is_valid_column_infix('foo_')
        expected = 'Infixes may not end with an "_". Infix given: foo_'
        self.assertEqual(str(e.value), expected)

        with pytest.raises(ValidationError) as e:
            validators.is_valid_column_infix('ABC')
        expected = "Infix contains the illegal characters: ['A', 'B', 'C']."
        expected += ' Infix given: ABC'
        self.assertEqual(str(e.value), expected)
