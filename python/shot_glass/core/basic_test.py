import unittest

from lunchbox.enforce import EnforceError

import shot_glass.core.basic as sgb
import shot_glass.core.monad as sgm
# ------------------------------------------------------------------------------


class MaybeTests(unittest.TestCase):
    def test_just(self):
        result = sgb.Maybe.just(5)
        self.assertIsInstance(result, sgb.Maybe)
        self.assertEqual(result.unwrap(), 5)

    def test_nothing(self):
        result = sgb.Maybe.nothing()
        self.assertIsInstance(result, sgb.Maybe)

    def test_repr(self):
        result = str(sgb.Maybe.just(5))
        self.assertEqual(result, 'Just(5)')

        result = str(sgb.Maybe.nothing())
        self.assertEqual(result, 'Nothing')

    def test_state(self):
        result = sgb.Maybe.just(5).state
        self.assertEqual(result, 'just')

        result = sgb.Maybe.nothing().state
        self.assertEqual(result, 'nothing')


class TryTests(unittest.TestCase):
    def test_success(self):
        result = sgb.Try.success(5)
        self.assertIsInstance(result, sgb.Try)

        with self.assertRaises(EnforceError):
            sgb.Try.success(ValueError('foo'))

    def test_failure(self):
        result = sgb.Try.failure(ValueError('foo'))
        self.assertIsInstance(result, sgb.Try)

        with self.assertRaises(EnforceError):
            sgb.Try.failure(99)

    def test_repr(self):
        result = str(sgb.Try.success(5))
        self.assertEqual(result, 'Success(5)')

        result = str(sgb.Try.failure(ValueError('foo')))
        expected = 'Failure(' + str(ValueError('foo')) + ')'
        self.assertEqual(result, expected)

    def test_state(self):
        result = sgb.Try(5).state
        self.assertEqual(result, 'success')

        result = sgb.Try(ValueError('foo')).state
        self.assertEqual(result, 'failure')

    def test_fmap(self):
        result = sgb.Try(2).fmap(lambda x: x + 1)
        self.assertEqual(result.unwrap(), 3)

        # error
        result = sgb.Try(2).fmap(lambda x: x + 'foo')
        self.assertEqual(type(result.unwrap()), TypeError)

    def test_bind(self):
        result = sgb.Try(2).bind(lambda x: sgm.Monad(x + 1))
        self.assertEqual(result.unwrap(), 3)
        self.assertEqual(result.__class__.__name__, 'Monad')

        # error
        result = sgb.Try(2).bind(lambda x: sgm.Monad(x + 'foo'))
        self.assertEqual(type(result.unwrap()), TypeError)

    def test_app(self):
        result = sgb.Try(2).app(sgm.Monad(lambda x: x + 1))
        self.assertEqual(result.unwrap(), 3)

        # error
        result = sgb.Try(2).app(sgm.Monad(lambda x: x + 'foo'))
        self.assertEqual(type(result.unwrap()), TypeError)
