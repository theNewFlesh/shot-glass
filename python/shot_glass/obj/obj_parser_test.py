import unittest

import lunchbox.tools as lbt

from shot_glass.obj.obj_parser import ObjParser
# ------------------------------------------------------------------------------


class ObjParserTest(unittest.TestCase):
    def test_vertex(self):
        parser = ObjParser()
        result = parser._ObjParser__v.parseString('v 1 2 3').asDict()
        expected = dict(
            component=dict(component_type='vertex', x=1.0, y=2.0, z=3.0)
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__v.parseString('v 1.0 2.0 3').asDict()
        self.assertEqual(result, expected)

        result = parser._ObjParser__v.parseString('v 1.0e0 2.0 3').asDict()
        self.assertEqual(result, expected)

        result = parser._ObjParser__v.parseString('v 1.0e0 2.0 3 4.1').asDict()
        expected = dict(
            component=dict(component_type='vertex', x=1.0, y=2.0, z=3.0, w=4.1)
        )
        self.assertEqual(result, expected)

    def test_vertex_normal(self):
        parser = ObjParser()
        result = parser._ObjParser__vn.parseString('vn 1 2 3').asDict()
        expected = dict(
            component=dict(component_type='vertex_normal', i=1.0, j=2.0, k=3.0)
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__vn.parseString('vn 1.0 2.0 3').asDict()
        self.assertEqual(result, expected)

        result = parser._ObjParser__vn.parseString('vn 1.0e0 2.0 3').asDict()
        self.assertEqual(result, expected)

    def test_vertex_point(self):
        parser = ObjParser()
        result = parser._ObjParser__vp.parseString('vp 1 2').asDict()
        expected = dict(
            component=dict(component_type='vertex_point', u=1.0, v=2.0, w=1.0)
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__vp.parseString('vp 1.0 2.0').asDict()
        self.assertEqual(result, expected)

        result = parser._ObjParser__vp.parseString('vp 1.0e0 2.0').asDict()
        self.assertEqual(result, expected)

        result = parser._ObjParser__vp.parseString('vp 1.0e0 2.0 4.1').asDict()
        expected = dict(
            component=dict(component_type='vertex_point', u=1.0, v=2.0, w=4.1)
        )
        self.assertEqual(result, expected)

    def test_vertex_texture(self):
        parser = ObjParser()
        result = parser._ObjParser__vt.parseString('vt 1 2').asDict()
        expected = dict(
            component=dict(component_type='vertex_texture', u=1.0, v=2.0, w=0.0)
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__vt.parseString('vt 1.0 2.0').asDict()
        self.assertEqual(result, expected)

        result = parser._ObjParser__vt.parseString('vt 1.0e0 2.0').asDict()
        self.assertEqual(result, expected)

        result = parser._ObjParser__vt.parseString('vt 1.0e0 2.0 4.1').asDict()
        expected = dict(
            component=dict(component_type='vertex_texture', u=1.0, v=2.0, w=4.1)
        )
        self.assertEqual(result, expected)

    def test_generic_vertex(self):
        parser = ObjParser()

        result = parser._ObjParser__vertex\
            .parseString('v 1e0 2e1 3e0 9.1e0')\
            .asDict()
        expected = dict(
            component=dict(component_type='vertex', x=1.0, y=20.0, z=3.0, w=9.1)
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__vertex.parseString('vn 1 2.2 3e0').asDict()
        expected = dict(
            component=dict(component_type='vertex_normal', i=1.0, j=2.2, k=3.0)
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__vertex.parseString('vp 1 2').asDict()
        expected = dict(
            component=dict(component_type='vertex_point', u=1.0, v=2.0, w=1.0)
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__vertex.parseString('vt 1.0 2.0').asDict()
        expected = dict(
            component=dict(component_type='vertex_texture', u=1.0, v=2.0, w=0.0)
        )
        self.assertEqual(result, expected)

    def test_face(self):
        parser = ObjParser()

        result = parser._ObjParser__face\
            .parseString('f 1/1/1 2/2/2 3/3/3')\
            .asDict()
        expected = dict(
            component_type='face', parts=[
                dict(vertex_id=1, vertex_texture_id=1, vertex_normal_id=1),
                dict(vertex_id=2, vertex_texture_id=2, vertex_normal_id=2),
                dict(vertex_id=3, vertex_texture_id=3, vertex_normal_id=3)
            ]
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__face\
            .parseString('f 1 2 3')\
            .asDict()
        expected = dict(
            component_type='face', parts=[
                dict(vertex_id=1, vertex_texture_id=None, vertex_normal_id=None),
                dict(vertex_id=2, vertex_texture_id=None, vertex_normal_id=None),
                dict(vertex_id=3, vertex_texture_id=None, vertex_normal_id=None)
            ]
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__face\
            .parseString('f 1/1 2/2 3/3')\
            .asDict()
        expected = dict(
            component_type='face', parts=[
                dict(vertex_id=1, vertex_texture_id=1, vertex_normal_id=None),
                dict(vertex_id=2, vertex_texture_id=2, vertex_normal_id=None),
                dict(vertex_id=3, vertex_texture_id=3, vertex_normal_id=None)
            ]
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__face\
            .parseString('f 1//1 2//2 3//3')\
            .asDict()
        expected = dict(
            component_type='face', parts=[
                dict(vertex_id=1, vertex_texture_id=None, vertex_normal_id=1),
                dict(vertex_id=2, vertex_texture_id=None, vertex_normal_id=2),
                dict(vertex_id=3, vertex_texture_id=None, vertex_normal_id=3)
            ]
        )
        self.assertEqual(result, expected)

    def test_component(self):
        parser = ObjParser()

        result = parser._ObjParser__component\
            .parseString('f 1 2 3')\
            .asDict()
        expected = dict(
            component_type='face', parts=[
                dict(vertex_id=1, vertex_texture_id=None, vertex_normal_id=None),
                dict(vertex_id=2, vertex_texture_id=None, vertex_normal_id=None),
                dict(vertex_id=3, vertex_texture_id=None, vertex_normal_id=None)
            ]
        )
        self.assertEqual(result, expected)

        result = parser._ObjParser__component.parseString('v 1 2 3 4').asDict()
        expected = dict(
            component=dict(component_type='vertex', x=1.0, y=2.0, z=3.0, w=4.0)
        )
        self.assertEqual(result, expected)

    def test_parse_line(self):
        parser = ObjParser()

        result = parser._parse_line('f 1 2 3').asDict()
        expected = dict(
            component_type='face', parts=[
                dict(vertex_id=1, vertex_texture_id=None, vertex_normal_id=None),
                dict(vertex_id=2, vertex_texture_id=None, vertex_normal_id=None),
                dict(vertex_id=3, vertex_texture_id=None, vertex_normal_id=None)
            ]
        )
        self.assertEqual(result, expected)

        result = parser._parse_line('v 1 2 3 4').asDict()
        expected = dict(
            component=dict(component_type='vertex', x=1.0, y=2.0, z=3.0, w=4.0)
        )
        self.assertEqual(result, expected)

        result = parser._parse_line('# comment').asDict()
        expected = dict(comment='comment')
        self.assertEqual(result, expected)

        result = parser._parse_line('').asDict()
        expected = {}
        self.assertEqual(result, expected)

    def test_parse(self):
        source = lbt.relative_path(__file__, '../../../resources/face.obj')
        parser = ObjParser()

        result = parser.parse(source)
        expected = dict(
            line_type='comment', comment='Generated from HiFive data'
        )
        self.assertEqual(result[0], expected)

        expected = dict(
            line_type='component',
            component_type='vertex',
            vertex_id=1,
            x=0.0,
            y=0.0,
            z=0.0
        )
        self.assertEqual(result[2], expected)

    def vertex_to_dict(self):
        tokens = ['foo', 1.0, 2.0, 3.0, 4.0]
        components = list('xyzw')
        result = ObjParser._ObjParser__vertex_to_dict(tokens, components)
        expected = dict(
            component_type='foo',
            x=1.0,
            y=2.0,
            z=3.0,
            w=4.0
        )
        self.assertEqual(result, expected)
