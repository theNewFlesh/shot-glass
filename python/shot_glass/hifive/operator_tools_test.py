import unittest

import pytest

import shot_glass.hifive.operator_tools as hfops
from shot_glass.utils import ValidationError
# ------------------------------------------------------------------------------


def is_foo(item):
    if item != 'foo':
        raise ValidationError('not foo')


def is_bar(item):
    if item != 'bar':
        raise ValidationError('not bar')


@hfops.operator(
    data=[is_foo],
    bar=[is_bar]
)
def func(data='required', bar='required', baz='baz'):
    return data + bar + baz


class HiFiveOperatorsToolsTests(unittest.TestCase):
    def test_operator(self):
        result = func(data='foo', bar='bar')
        self.assertEqual(result, 'foobarbaz')

        result = func(data='foo', bar='bar', baz='taco')
        self.assertEqual(result, 'foobartaco')

        result = func(data='foo', bar='bar', execute=False)
        self.assertEqual(result, None)

    def test_operator_bad_validate_mode(self):
        with pytest.raises(ValueError) as e:
            func(data='foo', validate='bad mode')
        expected = 'Validate keyword must be one of'
        expected += " ['parameters', 'data', 'all', 'none']."
        expected += ' Value provided: bad mode.'
        self.assertEqual(str(e.value), expected)

    def test_operator_validate(self):
        result = func(data='foo', bar='kiwi', validate='data')
        self.assertEqual(result, 'fookiwibaz')

        with pytest.raises(ValidationError) as e:
            func(data='not foo', bar='bar', validate='data')
        self.assertEqual(str(e.value), 'not foo')

        result = func(data='pizza', bar='bar', validate='parameters')
        self.assertEqual(result, 'pizzabarbaz')

        with pytest.raises(ValidationError) as e:
            func(data='foo', bar='not bar', validate='parameters')
        self.assertEqual(str(e.value), 'not bar')

        with pytest.raises(ValidationError) as e:
            func(data='not foo', bar='bar', validate='all')
        self.assertEqual(str(e.value), 'not foo')

        with pytest.raises(ValidationError) as e:
            func(data='foo', bar='not bar', validate='all')
        self.assertEqual(str(e.value), 'not bar')

        func(data='not foo', bar='not bar', validate='none')

    def test_operator_required(self):
        with pytest.raises(ValueError) as e:
            func(data='foo', validate='all')
        self.assertEqual(str(e.value), 'Missing required parameter: bar.')
