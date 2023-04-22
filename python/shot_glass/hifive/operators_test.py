from pathlib import Path
import os
from tempfile import TemporaryDirectory
import unittest

import bpy
import lunchbox.tools as lbt

from shot_glass.utils import ValidationError
import shot_glass.hifive.operators as operators
# ------------------------------------------------------------------------------


class HiFiveOperatorsTests(unittest.TestCase):
    def test_read_json(self):
        source = lbt.relative_path(__file__, '../../../resources/face.json')
        result = operators.read_json(fullpath=source, validate='all')
        expected = [
            'i_id',
            'f_id',
            'e_id',
            'v_id',
            'v_x',
            'v_y',
            'v_z'
        ]
        self.assertEqual(result.data.columns.tolist(), expected)
        self.assertEqual(result.data.v_id.tolist(), [0, 1, 1, 2, 2, 3, 3, 0])
        self.assertEqual(result.data.e_id.tolist(), [0, 0, 1, 1, 2, 2, 3, 3])
        self.assertEqual(result.data.f_id.tolist(), [0, 0, 0, 0, 0, 0, 0, 0])

    def test_write_json(self):
        source = lbt.relative_path(__file__, '../../../resources/face.json')
        data = operators.read_json(fullpath=source)
        with TemporaryDirectory() as root:
            target = os.path.join(root, 'foo.json')
            operators.write_json(data=data, fullpath=target, validate='all')

            with open(target) as f:
                result = f.read()

            with open(source) as f:
                expected = f.read()

            self.assertEqual(result, expected)

    def test_read_obj(self):
        source = lbt.relative_path(__file__, '../../../resources/face.obj')
        result = operators.read_obj(fullpath=source, validate='all')
        expected = [
            'i_id',
            'f_id',
            'e_id',
            'v_id',
            'v_x',
            'v_y',
            'v_z',
            'v_i_draw_order'
        ]
        self.assertEqual(result.data.columns.tolist(), expected)
        self.assertEqual(result.data.v_id.tolist(), [0, 0, 1, 1, 2, 2, 3, 3])
        self.assertEqual(result.data.e_id.tolist(), [0, 3, 0, 1, 1, 2, 2, 3])
        self.assertEqual(result.data.f_id.tolist(), [0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(result.data.i_id.tolist(), [0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(
            result.data.v_i_draw_order.tolist(), [0, 0, 1, 1, 2, 2, 3, 3]
        )

    def test_read_obj_2d(self):
        source = lbt.relative_path(
            __file__, '../../../resources/2d_face.obj')
        expected = f'OBJ file: {source} is missing [a-z_]+ data.'
        with self.assertRaisesRegex(ValidationError, expected):
            operators.read_obj(fullpath=source, validate='all')

    def test_write_obj(self):
        source = lbt.relative_path(__file__, '../../../resources/face.obj')
        data = operators.read_obj(fullpath=source)
        with TemporaryDirectory() as root:
            target = os.path.join(root, 'foo.obj')
            operators.write_obj(data=data, fullpath=target, validate='all')

            with open(target) as f:
                result = f.read()

            with open(source) as f:
                expected = f.read()

            self.assertEqual(result, expected)

    def test_to_blender_scene(self):
        source = lbt.relative_path(__file__, '../../../resources/face.obj')
        data = operators.read_obj(fullpath=source)
        result = operators.to_blender_scene(data=data)
        self.assertTrue(isinstance(result, bpy.types.Scene))

    def test_from_blender_scene(self):
        source = lbt.relative_path(__file__, '../../../resources/face.obj')
        expected = operators.read_obj(fullpath=source)
        scene = operators.to_blender_scene(data=expected)
        result = operators.from_blender_scene(scene=scene)
        self.assertTrue(result.is_equivalent(expected, ignore_columns=['e_id']))

    def test_to_plotly_figure(self):
        source = lbt.relative_path(__file__, '../../../resources/face.obj')
        data = operators.read_obj(fullpath=source)
        result = operators.to_plotly_figure(data=data)

        # to_plotly_figure triangulates the mesh so faces should be doubled
        # which is why i,j,k are 2 and not 1
        self.assertEqual(len(result['data'][0]['x']), 4)
        self.assertEqual(len(result['data'][0]['y']), 4)
        self.assertEqual(len(result['data'][0]['z']), 4)
        self.assertEqual(len(result['data'][0]['i']), 2)
        self.assertEqual(len(result['data'][0]['j']), 2)
        self.assertEqual(len(result['data'][0]['k']), 2)

    def test_from_file_sequence(self):
        with TemporaryDirectory() as root:
            files = []
            for i in range(3):
                filepath = f'foo_{i:04d}.txt'
                filepath = Path(root, filepath).absolute().as_posix()
                with open(filepath, 'w') as f:
                    f.write('bar')
                files.append(filepath)

            result = operators.from_file_sequence(fullpath=root)\
                .data.columns.tolist()
            self.assertIn('v_s_fullpath', result)

            result = operators.from_file_sequence(fullpath=root, infix='foo')\
                .data.columns.tolist()
            self.assertIn('v_s_foo_fullpath', result)

            result = operators.from_file_sequence(fullpath=root).data
            self.assertEqual(result.v_z.tolist(), [0, 1, 2])
            self.assertEqual(result.v_s_fullpath.tolist(), files)
