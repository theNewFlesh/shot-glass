import unittest

import shot_glass.core.monad as sgm
# ------------------------------------------------------------------------------


class MonadFunctionTests(unittest.TestCase):
    def test_wrap(self):
        result = sgm.wrap(sgm.Monad, 9)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(result._data, 9)

    def test_unwrap(self):
        monad = sgm.wrap(sgm.Monad, 9)
        result = sgm.unwrap(monad)
        self.assertEqual(result, 9)

    def test_fmap(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = lambda x: x + 2
        result = sgm.fmap(monad, func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_app(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = sgm.Monad(lambda x: x + 2)
        result = sgm.app(monad, func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_bind(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = lambda x: sgm.Monad(x + 2)
        result = sgm.bind(monad, func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_right(self):
        a = sgm.wrap(sgm.Monad, 2)
        expected = sgm.wrap(sgm.Monad, 4)
        result = sgm.right(a, expected)
        self.assertIs(result, expected)

    def test_fail(self):
        error = SyntaxError('foo')
        result = sgm.fail(sgm.Monad, error)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), error)
