import unittest

from lunchbox.enforce import EnforceError

import shot_glass.core.monad as sgm
# ------------------------------------------------------------------------------


class MonadFunctionTests(unittest.TestCase):
    def test_enforce_monad(self):
        sgm.enforce_monad(sgm.Monad)
        sgm.enforce_monad(sgm.Monad(42))

        class TestMonad(sgm.Monad):
            pass

        sgm.enforce_monad(TestMonad)
        sgm.enforce_monad(TestMonad(42))

        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.enforce_monad('foo')

    def test_wrap(self):
        result = sgm.wrap(sgm.Monad, 9)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(result._data, 9)

    def test_wrap_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.wrap('foo', 9)

    def test_unwrap(self):
        monad = sgm.wrap(sgm.Monad, 9)
        result = sgm.unwrap(monad)
        self.assertEqual(result, 9)

    def test_unwrap_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.unwrap('foo')

    def test_fmap(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = lambda x: x + 2
        result = sgm.fmap(monad, func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_fmap_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.fmap('foo', lambda x: x)

    def test_app(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = sgm.Monad(lambda x: x + 2)
        result = sgm.app(monad, func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_app_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.app('foo', sgm.Monad(lambda x: x + 2))

    def test_bind(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = lambda x: sgm.Monad(x + 2)
        result = sgm.bind(monad, func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_bind_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.bind('foo', lambda x: sgm.Monad(x + 2))

    def test_right(self):
        a = sgm.wrap(sgm.Monad, 2)
        expected = sgm.wrap(sgm.Monad, 4)
        result = sgm.right(a, expected)
        self.assertIs(result, expected)

    def test_right_errors(self):
        monad = sgm.Monad(10)

        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.right('foo', monad)

        with self.assertRaisesRegex(EnforceError, expected):
            sgm.right(monad, 'foo')

    def test_fail(self):
        error = SyntaxError('foo')
        result = sgm.fail(sgm.Monad, error)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), error)

    def test_fail_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.fail('foo', SyntaxError('bar'))

        expected = 'Error must be an instance of Exception. Given value: bar'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.fail(sgm.Monad('foo'), 'bar')
