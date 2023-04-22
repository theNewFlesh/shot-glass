from tempfile import TemporaryDirectory
import json
import os
import re

import pandas as pd
import numpy as np
import pytest

from shot_glass.hifive.hifive import HiFive, HiFiveDataType
from shot_glass.hifive.test_base import HiFiveTestBase
from shot_glass.core.tools import ValidationError
# ------------------------------------------------------------------------------


class HiFiveTest(HiFiveTestBase):
    def test_datatype(self):
        result = HiFiveDataType.FLOAT.validator(1.0)
        self.assertTrue(result)

        result = HiFiveDataType.FLOAT.validator(1)
        self.assertFalse(result)

        result = HiFiveDataType.INTEGER.validator(1)
        self.assertTrue(result)

        result = HiFiveDataType.INTEGER.validator(1.0)
        self.assertFalse(result)

        result = HiFiveDataType.STRING.validator('foo')
        self.assertTrue(result)

        result = HiFiveDataType.STRING.validator(1)
        self.assertFalse(result)

        result = HiFiveDataType.JSON.validator('{"foo": "bar"}')
        self.assertTrue(result)

        result = HiFiveDataType.JSON.validator('foo')
        self.assertFalse(result)

        result = HiFiveDataType.OPTIONAL.validator(set(['foo', 'bar']))
        self.assertTrue(result)

    def test_init(self):
        hi = HiFive()
        result = hi.data.columns.tolist()
        expected = HiFive._HiFive__DEFAULT_COLUMNS
        self.assertEqual(result, expected)

        result = hi.data.shape[0]
        self.assertEqual(result, 0)

    def test_read_hi5(self):
        with TemporaryDirectory() as temp:
            target = os.path.join(temp, 'foo.hi5')
            data = self.fake_data
            data.to_hdf(target, 'data')

            hi = HiFive().read_hi5(target)
            for col in data.columns.tolist():
                result = hi.data[col].tolist()
                expected = data[col].tolist()
                self.assertEqual(result, expected)

    def test_read_hi5_invalid_extension(self):
        with pytest.raises(ValidationError) as e:
            HiFive().read_hi5('foo.bar')
        self.assertEqual(e.type, ValidationError)
        self.assertEqual(str(e.value), 'Expected extension: hi5, found: bar.')

    def test_write_hi5(self):
        data = self.fake_data
        hi = HiFive()
        hi.data = data

        with TemporaryDirectory() as temp:
            target = os.path.join(temp, 'foo.hi5')
            hi.write_hi5(target)

            self.assertTrue(os.path.exists(target))
            hi = HiFive().read_hi5(target)

            for col in data.columns.tolist():
                result = hi.data[col].tolist()
                expected = data[col].tolist()
                self.assertEqual(result, expected)

    def test_write_hi5_invalid_extension(self):
        with pytest.raises(ValidationError) as e:
            HiFive().write_hi5('foo.bar')
        self.assertEqual(e.type, ValidationError)
        self.assertEqual(str(e.value), 'Expected extension: hi5, found: bar.')

    def test_validate_column(self):
        hi = HiFive()
        hi.data = self.fake_data
        hi.validate_column('v_id')

        with pytest.raises(ValidationError) as e:
            hi.validate_column('v_i_foo')
        self.assertEqual(str(e.value), 'v_i_foo not found in columns.')

        hi.data['foo'] = None
        with pytest.raises(ValidationError) as e:
            hi.validate_column('foo')
            self.assertEqual(e.type, ValidationError)
        del hi.data['foo']

        hi.data['v_foo'] = None
        with pytest.raises(ValidationError) as e:
            hi.validate_column('v_foo')
            self.assertEqual(e.type, ValidationError)
        del hi.data['v_foo']

        hi.data['x_foo'] = None
        with pytest.raises(ValidationError) as e:
            hi.validate_column('x_foo')
            self.assertEqual(e.type, ValidationError)
        del hi.data['x_foo']

        hi.data['a_x_foo'] = None
        with pytest.raises(ValidationError) as e:
            hi.validate_column('a_x_foo')
            self.assertEqual(e.type, ValidationError)
        del hi.data['a_x_foo']

        hi.data['f_q_foo'] = None
        with pytest.raises(ValidationError) as e:
            hi.validate_column('f_q_foo')
            self.assertEqual(e.type, ValidationError)
        del hi.data['f_q_foo']

        hi.data['v_f_foo'] = hi.data.v_id
        with pytest.raises(TypeError) as e:
            hi.validate_column('v_f_foo')
            self.assertEqual(e.type, TypeError)
        del hi.data['v_f_foo']

        hi.data.loc[1, 'v_id'] = 'foo'
        with pytest.raises(TypeError) as e:
            hi.validate_column('v_id')
            self.assertEqual(e.type, TypeError)

        hi.data['v_f_foo'] = hi.data.v_id
        hi.data.loc[1, 'v_f_foo'] = 'foo'
        with pytest.raises(TypeError) as e:
            hi.validate_column('v_f_foo')
            self.assertEqual(e.type, TypeError)

    def test_validate(self):
        hi = HiFive()
        hi.data = self.fake_data
        hi.validate()

        hi.data['v_i_foo'] = hi.data.v_id
        hi.validate()

        hi.data.loc[1, 'v_i_foo'] = 'bar'
        with pytest.raises(TypeError) as e:
            hi.validate()
            self.assertEqual(e.type, TypeError)

    def test_get_column_attributes(self):
        hi = HiFive()
        hi.data = self.fake_data

        result = hi._get_column_attributes('v_id')
        expected = dict(
            name='v_id',
            descriptor='id',
            ctype_indicator='v',
            dtype_indicator='i',
            has_nans=False
        )
        self.assertEqual(result, expected)

        hi.data['v_i_foo'] = None
        result = hi._get_column_attributes('v_i_foo')
        expected = dict(
            name='v_i_foo',
            descriptor='foo',
            ctype_indicator='v',
            dtype_indicator='i',
            has_nans=True
        )
        self.assertEqual(result, expected)

        hi.data['foo_bar_baz'] = None
        result = hi._get_column_attributes('foo_bar_baz')
        expected = dict(
            name='foo_bar_baz',
            descriptor='baz',
            ctype_indicator='foo',
            dtype_indicator='bar',
            has_nans=True
        )
        self.assertEqual(result, expected)

    def test_validate_column_name(self):
        hi = HiFive()
        hi.data = self.fake_data

        hi.data['foo'] = None
        with pytest.raises(ValidationError) as e:
            hi._validate_column_name('foo')
        self.assertEqual(str(e.value), 'foo is not a valid column name.')

        hi.data['foo_bar'] = None
        with pytest.raises(ValidationError) as e:
            hi._validate_column_name('foo_bar')
        self.assertEqual(str(e.value), 'foo_bar is not a valid column name.')

        hi.data['foo_i_baz'] = None
        with pytest.raises(ValidationError) as e:
            hi._validate_column_name('foo_i_baz')
        self.assertEqual(str(e.value), 'foo is not a valid ctype indicator.')

        hi.data['v_foo_bar'] = None
        with pytest.raises(ValidationError) as e:
            hi._validate_column_name('v_foo_bar')
        self.assertEqual(str(e.value), 'foo is not a valid dtype indicator.')

        hi.data['v_i_foo'] = None
        hi._validate_column_name('v_i_foo')

    def test_validate_column_values(self):
        hi = HiFive()
        hi._validate_column_values('v_id')

        hi.data = self.fake_data

        hi._validate_column_values('v_id')

        hi.data['v_i_foo'] = 1
        hi._validate_column_values('v_i_foo')

        hi.data.loc[1, 'v_i_foo'] = 'bar'
        with pytest.raises(TypeError) as e:
            hi._validate_column_values('v_i_foo')
        expected = 'Non-integer value found in column v_i_foo: bar'
        self.assertEqual(str(e.value), expected)

    def test_map_has_nans(self):
        hi = HiFive()
        hi.data = self.get_quadrilateral_data()
        hi.data.loc['v_id', 2:5] = np.nan

        with pytest.raises(TypeError) as e:
            hi.map('v_id', 'v_i_foo', lambda x: 27)
        expected = 'Cannot map to column of vertex component type because v_id'
        expected += ' column contains null values.'
        self.assertEqual(str(e.value), expected)

        hi.data = self.get_quadrilateral_data()
        hi.data.loc['f_id', 2:5] = np.nan

        with pytest.raises(TypeError) as e:
            hi.map('f_id', 'v_i_foo', lambda x: 27)
        expected = 'Cannot map to column of face component type because f_id'
        expected += ' column contains null values.'
        self.assertEqual(str(e.value), expected)

    def test_map_one_to_one(self):
        hi = HiFive()
        hi.data = self.get_quadrilateral_data()

        hi.map('v_id', 'v_i_foo', lambda x: 27)
        expected = [27] * hi.data.shape[0]
        result = hi.data['v_i_foo'].tolist()
        self.assertEqual(result, expected)

        hi.map('v_id', 'v_i_foo', lambda x: x.mean())
        expected = hi.data.v_id.tolist()
        result = hi.data['v_i_foo'].tolist()
        self.assertEqual(result, expected)

        hi.map('f_id', 'f_i_foo', lambda x: x.mean())
        expected = hi.data.f_id.tolist()
        result = hi.data['f_i_foo'].tolist()
        self.assertEqual(result, expected)

    def test_map_one_to_many(self):
        hi = HiFive()
        hi.data = self.get_quadrilateral_data()

        hi.data['f_i_foo'] = hi.data.v_id
        hi.map('f_i_foo', 'v_f_bar', lambda x: x.mean())
        expected = hi.data.groupby('f_id').mean().v_f_bar.tolist()
        expected = expected * hi.data.shape[0]
        result = hi.data['v_f_bar'].tolist()
        self.assertEqual(result, expected)

    def test_map_many_to_one(self):
        hi = HiFive()
        hi.data = self.get_quadrilateral_data()

        hi.data['v_i_bar'] = hi.data.v_id
        hi.map('v_i_bar', 'v_f_foo', lambda x: x.mean())
        expected = hi.data.v_i_bar.tolist()
        result = hi.data['v_f_foo'].tolist()
        self.assertEqual(result, expected)

    def test_copy(self):
        hi = HiFive()
        hi.data = self.fake_data
        result = hi.copy()
        for col in result.data.columns.tolist():
            temp = result.data[col].tolist()
            expected = hi.data[col].tolist()
            self.assertEqual(temp, expected)

        hi.data['foo'] = 'bar'
        a = hi.data.columns.tolist()
        b = result.data.columns.tolist()
        result = list(set(a).difference(b))
        expected = ['foo']
        self.assertEqual(result, expected)

    def test_info(self):
        hi = HiFive()
        hi.data = self.fake_data
        hi.data['v_s_foo'] = ['foo'] * hi.data.shape[0]
        cols = hi.data.columns.tolist()

        info = hi.info.T

        result = info.name.tolist()
        self.assertEqual(result, cols)

        result = info.descriptor.tolist()
        expected = [re.split('_', x)[-1] for x in cols]
        self.assertEqual(result, expected)

        result = info.ctype.tolist()
        expected = ['item', 'face', 'edge'] + (['vertex'] * 5)
        self.assertEqual(result, expected)

        result = info.dtype.tolist()
        expected = (['integer'] * 4) + (['float'] * 3) + ['string']
        self.assertEqual(result, expected)

        result = info.ctype_indicator.tolist()
        expected = ['i', 'f', 'e'] + (['v'] * 5)
        self.assertEqual(result, expected)

        result = info.dtype_indicator.tolist()
        expected = (['i'] * 4) + (['f'] * 3) + ['s']
        self.assertEqual(result, expected)

        result = info[info.name == 'v_s_foo'].has_nans.item()
        expected = False
        self.assertEqual(result, expected)

    def test_item_info(self):
        hi = HiFive()
        hi.data = self.fake_data

        hi.data['i_i_foo'] = [0] * hi.data.shape[0]
        row = hi.data.tail(1).copy()
        row.i_id = 2
        row.i_i_foo = 99
        hi.data = hi.data.append(row)

        result = hi.item_info.columns.tolist()
        self.assertEqual(result, ['i_id', 'i_i_foo'])

        self.assertEqual(hi.item_info.shape[0], hi.data.i_id.nunique())

        result = hi.item_info.i_id.unique().tolist()
        self.assertEqual(result, [0, 2])

        result = hi.item_info.i_i_foo.unique().tolist()
        self.assertEqual(result, [0, 99])

    def test_face_info(self):
        hi = HiFive()
        hi.data = self.fake_data

        hi.data['f_s_foo'] = ['foo'] * hi.data.shape[0]
        row = hi.data.tail(1).copy()
        row.f_id = 2
        row.f_s_foo = 'bar'
        hi.data = hi.data.append(row)

        result = hi.face_info.columns.tolist()
        self.assertEqual(result, ['f_id', 'f_s_foo'])

        self.assertEqual(hi.face_info.shape[0], hi.data.f_id.nunique())

        result = hi.face_info.f_id.unique().tolist()
        self.assertEqual(result, [0, 2])

        result = hi.face_info.f_s_foo.unique().tolist()
        self.assertEqual(result, ['foo', 'bar'])

    def test_edge_info(self):
        hi = HiFive()
        hi.data = self.fake_data

        val0 = json.dumps({'foo': 'bar'})
        hi.data['e_j_foo'] = [val0] * hi.data.shape[0]
        row = hi.data.tail(1).copy()
        row.e_id = 4
        val1 = json.dumps({'cream': 'cheese'})
        row.e_j_foo = val1
        hi.data = hi.data.append(row)
        hi.data = hi.data.append(row)

        result = hi.edge_info.columns.tolist()
        self.assertEqual(result, ['e_id', 'e_j_foo'])

        self.assertEqual(hi.edge_info.shape[0], hi.data.e_id.nunique())

        result = hi.edge_info.e_id.unique().tolist()
        self.assertEqual(result, [0, 1, 2, 3, 4])

        result = hi.edge_info.e_j_foo.unique().tolist()
        self.assertEqual(result, [val0, val1])

    def test_vertex_info(self):
        hi = HiFive()
        hi.data = self.fake_data

        hi.data['v_f_foo'] = [99.9] * hi.data.shape[0]
        row = hi.data.tail(1).copy()
        row.v_id = 4
        row.v_f_foo = 101.1
        hi.data = hi.data.append(row)

        result = hi.vertex_info.columns.tolist()
        self.assertEqual(result, ['v_id', 'v_x', 'v_y', 'v_z', 'v_f_foo'])

        self.assertEqual(hi.vertex_info.shape[0], hi.data.v_id.nunique())

        result = hi.vertex_info.v_id.unique().tolist()
        self.assertEqual(result, [0, 1, 2, 3, 4])

        result = hi.vertex_info.v_f_foo.unique().tolist()
        self.assertEqual(result, [99.9, 101.1])

    def test_geometry_info(self):
        hi = HiFive()
        hi.data = self.fake_data
        info = hi.geometry_info

        result = info.loc['count_of', 'item']
        self.assertEqual(result, 1)

        result = info.loc['count_of', 'face']
        self.assertEqual(result, 1)

        result = info.loc['count_of', 'edge']
        self.assertEqual(result, 4)

        result = info.loc['count_of', 'vertex']
        self.assertEqual(result, 4)

        result = info.loc['faces_per', 'item']
        self.assertEqual(result, [1])

        result = info.loc['edges_per', 'item']
        self.assertEqual(result, [4])

        result = info.loc['vertices_per', 'item']
        self.assertEqual(result, [4])

        result = info.loc['edges_per', 'face']
        self.assertEqual(result, [4])

        result = info.loc['vertices_per', 'face']
        self.assertEqual(result, [4])

        result = info.loc['vertices_per', 'edge']
        self.assertEqual(result, [2])

    def test_geometry_info_invalid(self):
        hi = HiFive()
        hi.data = self.get_invalid_data()
        info = hi.geometry_info

        result = info.loc['topology_of', 'face']
        self.assertEqual(result, ['invalid'])

    def test_geometry_info_triangle(self):
        hi = HiFive()
        hi.data = self.get_triangle_data()
        info = hi.geometry_info

        result = info.loc['topology_of', 'face']
        self.assertEqual(result, ['triangle'])

    def test_geometry_info_quadrilateral(self):
        hi = HiFive()
        hi.data = self.get_quadrilateral_data()
        info = hi.geometry_info

        result = info.loc['topology_of', 'face']
        self.assertEqual(result, ['quadrilateral'])

    def test_geometry_info_ngon(self):
        hi = HiFive()
        hi.data = self.get_ngon_data()
        info = hi.geometry_info

        result = info.loc['topology_of', 'face']
        self.assertEqual(result, ['ngon'])

    def test_geometry_info_multi(self):
        hi = HiFive()
        hi.data = self.get_multi_data()
        info = hi.geometry_info

        result = info.loc['topology_of', 'face']
        self.assertEqual(result, ['invalid', 'ngon', 'triangle'])

    def test_geometry_info_no_edges_no_faces(self):
        hi = HiFive()
        hi.data = self.fake_data
        hi.data['e_id'] = np.nan
        hi.data['f_id'] = np.nan

        info = hi.geometry_info
        result = info.loc['topology_of', 'face']
        self.assertTrue(pd.isnull(result))
        result = info.loc['topology_of', 'edge']
        self.assertTrue(pd.isnull(result))

        hi.data = self.fake_data
        hi.data['e_id'] = np.nan

        info = hi.geometry_info
        result = info.loc['topology_of', 'face']
        self.assertTrue(pd.isnull(result))
        result = info.loc['topology_of', 'edge']
        self.assertTrue(pd.isnull(result))

        hi.data = self.fake_data
        hi.data['f_id'] = np.nan

        info = hi.geometry_info
        result = info.loc['topology_of', 'face']
        self.assertTrue(pd.isnull(result))
        result = info.loc['topology_of', 'edge']
        self.assertTrue(pd.isnull(result))

    def test_display_data(self):
        hi = HiFive()
        hi.data = self.fake_data

        hi.data['v_x_foo'] = None
        hi.data.v_x_foo = hi.data.v_x_foo.apply(lambda x: np.zeros(100))
        result = hi.display_data.v_x_foo.unique().tolist()
        self.assertEqual(result, ['...'])

    def test_get_unique_counts(self):
        hi = HiFive()
        hi.data = self.fake_data
        row = hi.data.tail(1).copy()
        row.v_id = 9
        row.e_id = 4
        row.f_id = 1
        hi.data = hi.data.append(row)

        result = hi._HiFive__get_unique_counts('e_id', 'f_id')
        self.assertEqual(result, [1, 4])

        row.e_id = 5
        hi.data = hi.data.append(row)
        row.e_id = 6
        hi.data = hi.data.append(row)
        row.e_id = 7
        hi.data = hi.data.append(row)
        result = hi._HiFive__get_unique_counts('e_id', 'f_id')
        self.assertEqual(result, [4])

        row.e_id = 8
        hi.data = hi.data.append(row)
        result = hi._HiFive__get_unique_counts('e_id', 'f_id', summarize=False)
        self.assertEqual(result, [4, 5])

        result = hi._HiFive__get_unique_counts('e_id', 'f_id', summarize=True)
        self.assertEqual(result, [4, 'n'])

    def test_get_nunique(self):
        hi = HiFive()
        hi.data = self.fake_data

        hi.data['foo'] = None
        hi.data.loc[0, 'foo'] = 0
        hi.data.loc[1, 'foo'] = 1

        result = hi._HiFive__get_nunique('foo')
        self.assertEqual(result, 2)

    def test_expand_row(self):
        hi = HiFive()
        hi.data = self.fake_data

        hi.data['v_x_foo'] = None
        hi.data.v_x_foo = hi.data.v_x_foo.apply(lambda x: [0, 1, 2])

        row = hi.data.loc[0, :]

        result = hi._HiFive__expand_row(row, 'v_x_foo', 'v_i_foo', lambda x: x)
        self.assertEqual(result.shape[0], 3)
        self.assertEqual(result.loc[0, 'v_i_foo'], 0)
        self.assertEqual(result.loc[1, 'v_i_foo'], 1)
        self.assertEqual(result.loc[2, 'v_i_foo'], 2)

        hi = HiFive()
        hi.data = self.fake_data
        hi.data['v_s_foo'] = None
        hi.data.v_s_foo = hi.data.v_s_foo.apply(lambda x: 'abc')

        row = hi.data.loc[0, :]

        result = hi._HiFive__expand_row(
            row, 'v_s_foo', 'v_s_foo', lambda x: list(x)
        )
        self.assertEqual(result.shape[0], 3)
        self.assertEqual(result.loc[0, 'v_s_foo'], 'a')
        self.assertEqual(result.loc[1, 'v_s_foo'], 'b')
        self.assertEqual(result.loc[2, 'v_s_foo'], 'c')

    def test_expand(self):
        hi = HiFive()
        hi.data = self.fake_data

        with pytest.raises(ValidationError) as e:
            hi.expand('bad_source', 'v_x_foo', 'v_i_foo', lambda x: x)
        self.assertEqual(e.type, ValidationError)

        with pytest.raises(ValidationError) as e:
            hi.expand('v_id', 'bad_target', 'v_i_foo', lambda x: x)
        self.assertEqual(e.type, ValidationError)

        with pytest.raises(TypeError) as e:
            hi.expand('v_id', 'v_i_foo', 'v_j_foo', lambda x: x)
        self.assertEqual(e.type, TypeError)
        msg = 'Id column must be of dtype INTEGER. Provided dtype: JSON.'
        self.assertEqual(str(e.value), msg)

        hi.data['v_x_foo'] = None
        hi.data.v_x_foo = hi.data.v_x_foo.apply(lambda x: 'abc')
        hi.data.loc[0, 'v_x_foo'] = 'qwerty'

        expected = hi.data.shape[0] * 3 + 3
        result = hi.expand(
            'v_x_foo', 'v_s_foo', 'v_i_foo_id', lambda x: list(x)
        )
        self.assertEqual(result.data.shape[0], expected)
        for i, col in enumerate('qwerty'):
            self.assertEqual(result.data.loc[i, 'v_s_foo'], col)
            self.assertEqual(result.data.loc[i, 'v_i_foo_id'], 0)

        i = result.data.shape[0] - 1
        last_id = self.fake_data.shape[0] - 1
        self.assertEqual(result.data.loc[i, 'v_s_foo'], 'c')
        self.assertEqual(result.data.loc[i, 'v_i_foo_id'], last_id)

    def test_is_equivalent(self):
        a = HiFive()
        a.data = self.fake_data

        b = a.copy()
        self.assertTrue(a.is_equivalent(b))

        b.data = b.data.T
        self.assertFalse(a.is_equivalent(b))
        b = a.copy()

        a.data.sort_values('e_id', inplace=True)
        b.data.sort_values('v_id', inplace=True)
        self.assertTrue(a.is_equivalent(b))

        b.data['foo'] = b.data.v_id
        self.assertTrue(a.is_equivalent(b, ignore_columns=['foo']))

        del b.data['v_id']
        self.assertFalse(a.is_equivalent(b))
        b = a.copy()

        b.data = pd.concat([a.data, b.data.loc[0:0, :]], ignore_index=True)
        self.assertFalse(a.is_equivalent(b))
        b = a.copy()

        a.data.sort_values('e_id', inplace=True)
        b.data.sort_values('v_id', inplace=True)
        b.data.loc[0, 'v_id'] = 42
        self.assertFalse(a.is_equivalent(b))
