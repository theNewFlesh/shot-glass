from functools import partial
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
        result = sgm.fmap(func, monad)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_fmap_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.fmap(lambda x: x, 'foo')

    def test_app(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = sgm.Monad(lambda x: x + 2)
        result = sgm.app(func, monad)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_app_errors(self):
        expected = 'bar is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.app('bar', sgm.Monad(2))

        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.app(sgm.Monad(lambda x: x + 2), 'foo')

    def test_bind(self):
        monad = sgm.wrap(sgm.Monad, 2)
        func = lambda x: sgm.Monad(x + 2)
        result = sgm.bind(func, monad)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(sgm.unwrap(result), 4)

    def test_bind_errors(self):
        expected = 'foo is not a subclass or instance of Monad.'
        with self.assertRaisesRegex(EnforceError, expected):
            sgm.bind(lambda x: sgm.Monad(x + 2), 'foo')

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


class MonadInfixFunctionTests(unittest.TestCase):
    def test_wrap_infix(self):
        monad = sgm.Monad
        data = 99
        result = monad |sgm.wrap| data  # noqa: E225
        expected = sgm.wrap(monad, data)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(sgm.unwrap(result), sgm.unwrap(expected))

    def test_fmap_infix(self):
        func = lambda x: x + 7
        monad = sgm.Monad(14)
        result = func |sgm.fmap| monad  # noqa: E225
        expected = sgm.fmap(func, monad)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(sgm.unwrap(result), sgm.unwrap(expected))

    def test_app_infix(self):
        monad_func = sgm.Monad(lambda x: x * 2)
        monad = sgm.Monad(5)
        result = monad_func |sgm.app| monad  # noqa: E225
        expected = sgm.app(monad_func, monad)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(sgm.unwrap(result), sgm.unwrap(expected))

    def test_bind_infix(self):
        class Foo(sgm.Monad):
            pass

        func = Foo.wrap
        monad = sgm.Monad(99)
        result = func |sgm.bind| monad  # noqa: E225
        expected = sgm.bind(func, monad)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(sgm.unwrap(result), sgm.unwrap(expected))

    def test_right_infix(self):
        monad_a = sgm.Monad('a')
        monad_b = sgm.Monad('b')
        result = monad_a |sgm.right| monad_b  # noqa: E225
        expected = sgm.right(monad_a, monad_b)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(sgm.unwrap(result), sgm.unwrap(expected))

    def test_fail_infix(self):
        monad = sgm.Monad
        error = SyntaxError('foobar')
        result = monad |sgm.fail| error  # noqa: E225
        expected = sgm.fail(monad, error)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(sgm.unwrap(result), sgm.unwrap(expected))

    def test_curry(self):
        func = lambda x, y: x + y
        cur = func |sgm.curry| 'a'  # noqa: E225
        self.assertIsInstance(cur, partial)
        self.assertEqual(cur('b'), 'ab')

        result = func |sgm.curry| 1 |sgm.curry| 2  # noqa: E225
        self.assertEqual(result(), 3)


class MonadTests(unittest.TestCase):
    def test_init(self):
        result = sgm.Monad(42)
        self.assertEqual(result._data, 42)

    def test_wrap(self):
        result = sgm.Monad.wrap(42)
        self.assertIsInstance(result, sgm.Monad)

    def test_unwrap(self):
        result = sgm.Monad.wrap(42).unwrap()
        self.assertEqual(result, 42)

    def test_fmap(self):
        result = sgm.Monad.wrap(42).fmap(lambda x: x + 10)
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(result.unwrap(), 52)

    def test_app(self):
        result = sgm.Monad.wrap(42).app(sgm.Monad.wrap(lambda x: x + 10))
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(result.unwrap(), 52)

    def test_bind(self):
        result = sgm.Monad.wrap(42).bind(lambda x: sgm.Monad.wrap(x + 10))
        self.assertIsInstance(result, sgm.Monad)
        self.assertEqual(result.unwrap(), 52)

    def test_right(self):
        expected = sgm.Monad.wrap(99)
        result = sgm.Monad \
            .wrap(42) \
            .right(expected)
        self.assertIs(result, expected)
        self.assertIs(result.unwrap(), expected.unwrap())

    def test_fail(self):
        error = SyntaxError('foo')
        result = sgm.Monad.wrap(42).fail(error)
        self.assertIsInstance(result, sgm.Monad)
        self.assertIs(result.unwrap(), error)

    def test_repr(self):
        class Foo(sgm.Monad):
            pass

        result = str(Foo(99))
        self.assertEqual(result, 'Foo(99)')

    def test_and(self):
        m = sgm.Monad(99)
        func = lambda x: x + 2
        result = m & func
        expected = m.fmap(func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertIs(result.unwrap(), expected.unwrap())

    def test_xor(self):
        m = sgm.Monad.wrap(99)
        func = sgm.Monad(lambda x: x + 10)
        result = m ^ func
        expected = m.app(func)
        self.assertIsInstance(result, sgm.Monad)
        self.assertIs(result.unwrap(), expected.unwrap())

    def test_rshift(self):
        class Foo(sgm.Monad):
            pass

        m = sgm.Monad(99)
        result = m >> Foo
        expected = m.bind(Foo)
        self.assertIsInstance(result, Foo)
        self.assertIs(result.unwrap(), expected.unwrap())

    # LAWS----------------------------------------------------------------------
    def test_bind_left_identity(self):
        # Haskell: return a >>= h     =  ha
        # Python:  wrap(a).bind(func) == func(a)
        class TestMonad(sgm.Monad):
            pass

        x = 1
        func = TestMonad.wrap
        result = sgm.Monad.wrap(x).bind(func)
        expected = func(x)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(result._data, expected._data)

    def test_bind_right_identity(self):
        # Haskell: m >>= return   =  m
        # Python:  m.bind(m.wrap) == m

        m = sgm.Monad.wrap(99)
        result = m.bind(m.wrap)
        expected = m
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(result._data, expected._data)

    def test_bind_associativity(self):
        # Haskell: (m >>= g) >>= h = m >>= (\x -> g x >>= h)
        # Python: m.bind(g).bind(h) == m.bind(lambda x: g(x).bind(h))

        class TestMonad1(sgm.Monad):
            pass

        class TestMonad2(sgm.Monad):
            pass

        m = sgm.Monad(99)
        g = TestMonad1
        h = TestMonad2
        result = m.bind(g).bind(h)
        expected = m.bind(lambda x: g(x).bind(h))
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(result._data, expected._data)

    def test_fmap_identity(self):
        # Haskell: fmap id = id
        # Python:  m.fmap(lambda x: x) == lambda x: x

        identity = lambda x: x
        m = sgm.Monad.wrap(99)
        result = m.fmap(identity)
        expected = identity(m)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(result._data, expected._data)

    def test_fmap_distributivity(self):
        # Haskell: fmap (g . h) = (fmap g) . (fmap h)
        # Python:  m.fmap(lambda x: h(g(x))) == m.fmap(g).fmap(h)

        m = sgm.Monad.wrap(99)
        g = lambda x: x - 1
        h = lambda x: x * 2
        result = m.fmap(lambda x: h(g(x)))
        expected = m.fmap(g).fmap(h)
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(result._data, expected._data)

    def test_app_identity(self):
        # Haskell: pure id <*> v = v
        # Python:  m.wrap(v).app( m.wrap(lambda x: x) )

        m = sgm.Monad.wrap(99)
        result = m.app(m.wrap(lambda x: x))
        self.assertEqual(result.__class__, m.__class__)
        self.assertEqual(result._data, m._data)

    def test_app_homomorphism(self):
        # Haskell: (pure f) <*> (pure x) = pure (f x)
        # Python:  m.wrap(x).app(m.wrap(func)) == m.wrap(func(x))

        m = sgm.Monad
        func = lambda x: x + 2
        x = 2
        result = m.wrap(x).app(m.wrap(func))
        expected = m.wrap(func(x))
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(result._data, expected._data)

    def test_app_interchange(self):
        # Haskell: u <*> (pure y) = pure (\f -> f y) <*> u
        # Python:  m(y).app(m.wrap(u)) == m(u).app(m.wrap(lambda f: f(y)))
        #          u = lambda x: 42

        m = sgm.Monad
        u = lambda x: 42
        y = 5
        result = m.wrap(y).app(m.wrap(u))
        expected = m.wrap(u).app(m.wrap(lambda f: f(y)))
        self.assertEqual(result.__class__, expected.__class__)
        self.assertEqual(result._data, expected._data)
