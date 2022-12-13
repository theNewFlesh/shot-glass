import unittest

from shot_glass.hifive.type_base import HiFiveTypeBase
from shot_glass.utils import ValidationError
# ------------------------------------------------------------------------------


class HiFiveTypeBaseTest(unittest.TestCase):
    def setUp(self):
        self.func_a = lambda x: x == 'foo'
        self.func_b = lambda x: x == 1

        class TestType(HiFiveTypeBase):
            FOO = ('foo', 'f', str, self.func_a, 0)
            BAR = ('bar', 'b', int, self.func_b, 1)
        self.test_class = TestType

    def test_is_valid_value(self):
        result = self.test_class.FOO.is_valid_value('foo')
        self.assertTrue(result)

        result = self.test_class.BAR.is_valid_value('foo')
        self.assertFalse(result)

    def test_is_valid_fullname(self):
        result = self.test_class.is_valid_fullname('foo')
        self.assertTrue(result)

        result = self.test_class.is_valid_fullname('Foo')
        self.assertFalse(result)

    def test_is_valid_indicator(self):
        result = self.test_class.is_valid_indicator('f')
        self.assertTrue(result)

        result = self.test_class.is_valid_indicator('x')
        self.assertFalse(result)

    def test_from_fullname(self):
        result = self.test_class.from_fullname('foo')
        self.assertEqual(result, self.test_class.FOO)

        result = self.test_class.from_fullname('bar')
        self.assertEqual(result, self.test_class.BAR)

        with self.assertRaisesRegex(ValidationError, 'f is not a valid fullname.'):
            self.test_class.from_fullname('f')

        with self.assertRaisesRegex(ValidationError, 'FOO is not a valid fullname.'):
            self.test_class.from_fullname('FOO')

    def test_from_indicator(self):
        result = self.test_class.from_indicator('f')
        self.assertEqual(result, self.test_class.FOO)

        result = self.test_class.from_indicator('b')
        self.assertEqual(result, self.test_class.BAR)

        with self.assertRaisesRegex(ValidationError, 'F is not a valid indicator.'):
            self.test_class.from_indicator('F')

        with self.assertRaisesRegex(ValidationError, 'FOO is not a valid indicator.'):
            self.test_class.from_indicator('FOO')

    def test_get_fullnames(self):
        result = list(sorted(self.test_class.get_fullnames()))
        self.assertEqual(result, ['bar', 'foo'])

    def test_get_indicators(self):
        result = list(sorted(self.test_class.get_indicators()))
        self.assertEqual(result, ['b', 'f'])

    def test_get_validators(self):
        result = self.test_class.get_validators()
        self.assertIn(self.func_a, result)
        self.assertIn(self.func_b, result)
