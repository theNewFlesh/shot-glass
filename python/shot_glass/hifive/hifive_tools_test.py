import json
import unittest

from pandas import DataFrame
import numpy as np
import pytest

from shot_glass.utils import ValidationError
import shot_glass.hifive.hifive_tools as hft
# ------------------------------------------------------------------------------


class HiFiveToolsTests(unittest.TestCase):
    def test_to_snakecase(self):
        result = hft.to_snakecase('fooBar')
        self.assertEqual(result, 'foo_bar')

        result = hft.to_snakecase('fooBar_Baz')
        self.assertEqual(result, 'foo_bar_baz')

    def test_is_string(self):
        result = hft.is_string(np.nan)
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_string('foo')
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_string(1)
        expected = False
        self.assertEqual(result, expected)

    def test_is_json(self):
        result = hft.is_json(np.nan)
        expected = True
        self.assertEqual(result, expected)

        valid = json.dumps({'foo': 'bar'})
        result = hft.is_json(valid)
        expected = True
        self.assertEqual(result, expected)

        invalid = 'foobar'
        result = hft.is_json(invalid)
        expected = False
        self.assertEqual(result, expected)

        result = hft.is_json(1)
        expected = False
        self.assertEqual(result, expected)

    def test_is_float(self):
        result = hft.is_float(np.nan)
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_float(1.0)
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_float(1)
        expected = False
        self.assertEqual(result, expected)

    def test_is_integer(self):
        result = hft.is_integer(np.nan)
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_integer(1)
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_integer(1.0)
        expected = False
        self.assertEqual(result, expected)

    def test_is_natural(self):
        result = hft.is_natural_number(np.nan)
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_natural_number(1)
        expected = True
        self.assertEqual(result, expected)

        result = hft.is_natural_number(-1)
        expected = False
        self.assertEqual(result, expected)

        result = hft.is_natural_number(1.0)
        expected = False
        self.assertEqual(result, expected)

    def test_get_nunique_a_per_b(self):
        data = DataFrame()
        data['a'] = ['q', 'q', 'x', 'y']
        data['b'] = [0, 0, 1, 1]

        result = hft.get_nunique_a_per_b(data, 'a', 'b')
        self.assertEqual(result, [1, 2])

    def test_validate_file_extension(self):
        hft.validate_file_extension('foo.bar', 'bar')
        hft.validate_file_extension('foo.foo.bar', 'bar')

        with pytest.raises(ValidationError) as e:
            hft.validate_file_extension('foo.txt', 'bar')
        self.assertEqual(str(e.value), 'Expected extension: bar, found: txt.')
