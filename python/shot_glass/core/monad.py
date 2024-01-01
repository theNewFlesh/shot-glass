from typing import Any, Callable, Generic, Type, TypeVar, Union  # noqa: F401

from functools import partial

from lunchbox.enforce import Enforce, EnforceError
import infix

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
# ------------------------------------------------------------------------------


'''
Monad is a library containing the Monad class and a library of monadic
functions it calls.

Haskell equivalence table:

    =========== ======== ====== ===== ================ ================================
    **Python**           **Haskell**  **Haskell Type Signature**
    -------------------- ------------ -------------------------------------------------
    prefix      infix    prefix infix implication      signature
    =========== ======== ====== ===== ================ ================================
    app         │iapp│          <*>   Applicative f => f (a -> b) -> fa -> fb
    bind        │ibind│         >>=   Monad m       => m a -> (a -> m b) -> m b
    fail        │ifail│  fail         Monad m       => String -> m a
    fmap        │ifmap│  fmap   <$>   Functor f     => (a -> b) -> fa -> fb
    right       │iright│        >>    Monad m       => m a -> m b -> m b
    unwrap                            Monad m       => m a -> a
    wrap        │iwrap│  pure         Applicative f => a -> f a
    wrap        │iwrap│  return       Monad m       => a -> m a
    curry       │icurry│
    dot         │idot│   .      .                      (b -> c) -> (a -> b) -> (a -> c)
    partial_dot          .      .                      (b -> c) -> (a -> b) -> (a -> c)
    =========== ======== ====== ===== ================ ================================
'''


def enforce_monad(item):
    # type: (Any) -> None
    '''
    Enforces item being a Monad subclass or instance.

    Args:
        item (object): Item to be tested.

    Raises:
        EnforceError: If item is not Monad subclass or instance.
    '''
    pred = isinstance  # type: Any
    if item.__class__ is type:
        pred = issubclass
    if not pred(item, Monad):
        raise EnforceError(f'{item} is not a subclass or instance of Monad.')


@infix.or_infix
def iwrap(*args, **kwargs):
    return wrap(*args, **kwargs)


def wrap(monad, data):
    # type: (Monadlike, A) -> Monad[A]
    '''
    Wrap: M -> A -> MA

    .. image:: resources/wrap.png

    Given a Monad class or instance, create a new Monad with given data.

    Args:
        monad (Monad): Monad class or instance.
        data (Any): Data to be wrapped as Monad.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad[A]: Monad of data.
    '''
    enforce_monad(monad)
    return monad.wrap(data)


def unwrap(monad):
    # type: (Monad[A]) -> A
    '''
    Unwrap: MA -> A

    .. image:: resources/unwrap.png

    Return the data of a given Monad instance.

    Args:
        monad (Monad): Monad instance.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        A: Monad data.
    '''
    enforce_monad(monad)
    return monad._data


@infix.or_infix
def ifmap(*args, **kwargs):
    return fmap(*args, **kwargs)


def fmap(func, monad):
    # type: (Callable[[A], B], Monad[A]) -> Monad[B]
    '''
    Functor map: (A -> B) -> MA -> MB

    .. image:: resources/fmap.png

    Given a Monad of A (MA) and a function A to B, return a Monad of B (MB).

    Args:
        func (function): Function (A -> B).
        monad (Monad): Monad of A.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad[B]: Monad of B.
    '''
    enforce_monad(monad)
    return wrap(monad, func(unwrap(monad)))


@infix.or_infix
def iapp(*args, **kwargs):
    return app(*args, **kwargs)


def app(monad_func, monad):
    # type: (Monad[Callable[[A], B]], Monad[A]) -> Monad[B]
    '''
    Applicative: M(A -> B) -> MA -> MB

    .. image:: resources/app.png

    Given a Monad of A (MA) and a Monad of a function A to B, return a Monad
    of B (MB).

    Args:
        monad_func (Monad): Monad of function (A -> B).
        monad (Monad): Monad of A.

    Raises:
        EnforceError: If monad_func is not instance of Monad.
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad[B]: Monad of B.
    '''
    enforce_monad(monad_func)
    enforce_monad(monad)
    func = unwrap(monad_func)
    value = unwrap(monad)
    return wrap(monad, func(value))


@infix.or_infix
def ibind(*args, **kwargs):
    return bind(*args, **kwargs)


def bind(func, monad):
    # type: (Callable[[A], Monad[B]], Monad[A]) -> Monad[B]
    '''
    Bind: (A -> MB) -> MA -> MB

    .. image:: resources/bind.png

    Given a Monad of A (MA) and a function A to MB, return a Monad of B (MB).

    Args:
        func (function): Function (A -> MB).
        monad (Monad): Monad of A.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad[B]: Monad of B.
    '''
    enforce_monad(monad)
    return func(unwrap(monad))


@infix.or_infix
def iright(*args, **kwargs):
    return right(*args, **kwargs)


def right(monad_a, monad_b):
    # type: (Monad[A], Monad[B]) -> Monad[B]
    '''
    Right: MA -> MB -> MB

    .. image:: resources/right.png

    Given two Monads, a and b, return the right Monad b.

    Args:
        monad_a (Monad): Left monad.
        monad_b (Monad): Right monad.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad: Right Monad.
    '''
    enforce_monad(monad_a)
    enforce_monad(monad_b)
    return monad_b


@infix.or_infix
def ifail(*args, **kwargs):
    return fail(*args, **kwargs)


def fail(monad, error):
    # type (Monad, Exception) -> Monad[Exception]
    '''
    Fail: M -> E -> ME

    .. image:: resources/fail.png

    Given a Monad and Exception, return a Monad of that Exception.

    Args:
        monad (Monad): Monad to wrap error with.
        error (Exception): Error.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.
        EnforceError: If error is not an instance of Exception.

    Returns:
        Monad: Error Monad.
    '''
    enforce_monad(monad)
    msg = 'Error must be an instance of Exception. Given value: {a}.'
    Enforce(error, 'instance of', Exception, message=msg)
    return wrap(monad, error)


def succeed(monad, value):
    # type (Monad, A) -> Monad[A]
    '''
    Succed: M -> A -> MA

    .. image:: resources/wrap.png

    Given a Monad and a value, return a Monad of that value.

    Args:
        monad (Monad): Monad to wrap value with.
        value (object): Value.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.
        EnforceError: If value is an instance of Exception.

    Returns:
        Monad: Monad of value.
    '''
    enforce_monad(monad)
    msg = 'Error must not be an instance of Exception. Given value: {a}.'
    Enforce(value, 'not instance of', Exception, message=msg)
    return wrap(monad, value)


@infix.or_infix
def icurry(*args, **kwargs):
    return curry(*args, **kwargs)


def curry(func, *args, **kwargs):
    # type: (Callable, Any, Any) -> Callable
    '''
    Infix notation for functools.partial.

    Args:
        func (function): Function to be curried.
        args (optional): Arguments.
        kwargs (optional): Keyword arguments.

    Returns:
        function: Curried function.
    '''
    return partial(func, *args, **kwargs)


@infix.or_infix
def idot(*args, **kwargs):
    return dot(*args, **kwargs)


def dot(func_b, func_a):
    # type: (Callable[[B], C], Callable[[A], B]) -> Callable[[A], C]
    '''
    Dot: (b -> c) -> (a -> b) -> (a -> c)
         fb |idot| fa == fb(fa)

    Composes two functions.

    Example:
        ```
        fa = lambda x: x + 'a'
        fb = lambda x: x + 'b'
        dot(fb, fa)('x') == 'xab'
        (fb |idot| fa)('x') == 'xab'
        ```

    Args:
        func_b (function): Outer function.
        func_a (function): Inner function.

    Returns:
        partial: Function composition.
    '''
    def of(b, a, *args, **kwargs):
        return b(a(*args, **kwargs))
    return partial(of, func_b, func_a)


def partial_dot(func):
    # type: (Callable[[B], C]) -> partial[Callable[[A], B]]
    '''
    Partial Dot: (b -> c) -> (a -> b)

    Partial version of dot function.

    Example:
        ```
        app = sgm.app
        u = Monad(lambda x: x + 1)
        v = Monad(lambda x: x + 2)
        w = Monad(3)
        Monad(partial_dot) |iapp| u |iapp| v |iapp| w
        ```

    Args:
        func (function): Outer composition function.

    Returns:
        partial: Function composition.
    '''
    return partial(dot, func)


def catch(monad, func):
    # type: (MA, Callable[[A], B]) -> Callable[[A], Union[B, Exception]]
    '''
    Catch: MA -> (A -> B) -> (MB | ME)

    Catches exception and returns it rather then raising an error.

    Args:
        monad (Monad): Monad.
        func (function): Function to attempt.

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        object: Partial function with catch logic.
    '''
    enforce_monad(monad)

    def catch_(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            return fail(monad, error)
    return partial(catch_, func)
# ------------------------------------------------------------------------------


class Monad(Generic[A]):
    '''
    Monad is a generic base class for monads. It implements all the monad
    functions as methods which take itself as the first argument.

    Haskell equivalence table:

    ====== ===== ====== ===== ================ ========================
    **Python**   **Haskell**  **Haskell Type Signature**
    ------------ ------------ -----------------------------------------
    prefix infix prefix infix implication      signature
    ====== ===== ====== ===== ================ ========================
    app    ^            <*>   Applicative f => f (a -> b) -> fa -> fb
    bind   >>           >>=   Monad m       => m a -> (a -> m b) -> m b
    fail         fail         Monad m       => String -> m a
    fmap   &     fmap   <$>   Functor f     => (a -> b) -> fa -> fb
    right               >>    Monad m       => m a -> m b -> m b
    unwrap                    Monad m       => m a -> a
    wrap         pure         Applicative f => a -> f a
    wrap         return       Monad m       => a -> m a
    ====== ===== ====== ===== ================ ========================
    '''

    def __init__(self, data):
        # type: (A) -> None
        '''
        Constructs monad instance.

        Args:
            data (object): Data to be wrapped with Monad.
        '''
        self._data = data

    def __repr__(self):
        # type: () -> str
        '''
        String representation of Monad instance.
        '''
        return f'{self.__class__.__name__}({self._data.__repr__()})'

    @classmethod
    def wrap(cls, data):
        # type: (A) -> MA
        '''
        Wrap: A -> MA

        Create a new Monad with given data.

        Args:
            data (Any): Data to be wrapped as Monad.

        Returns:
            Monad[A]: Monad of data.
        '''
        return cls(data)

    def unwrap(self):
        # type: () -> A
        '''
        Unwrap: () -> A

        Return self._data.

        Returns:
            A: Monad data.
        '''
        return unwrap(self)

    def fmap(self, func):
        # type: (Callable[[A], B]) -> MB
        '''
        Functor map: (A -> B) -> MB

        Given a function A to B, return a Monad of B (MB).
        Example: m.fmap(lambda x: x + 2)

        Args:
            func (function): Function (A -> B).

        Returns:
            Monad[B]: Monad of B.
        '''
        return fmap(func, self)

    def app(self, monad_func):
        # type: (Monad[Callable[[A], B]]) -> MB
        '''
        Applicative: M(A -> B) -> MB

        Given a Monad of a function A to B, return a Monad of B (MB).

        Args:
            monad_func (Monad): Monad of function (A -> B).

        Returns:
            Monad[B]: Monad of B.
        '''
        return app(monad_func, self)

    def bind(self, func):
        # type: (Callable[[A], MB]) -> MB
        '''
        Bind: (A -> MB) -> MB

        Given a function A to MB, return a Monad of B (MB).

        Args:
            func (function): Function (A -> MB).

        Returns:
            Monad[B]: Monad of B.
        '''
        return bind(func, self)

    def right(self, monad):
        # type: (MB) -> MB
        '''
        Right: MB -> MB

        Return given monad (self is left, given monad is right).

        Args:
            monad (Monad): Right monad.

        Returns:
            Monad: Right Monad.
        '''
        return right(self, monad)

    def fail(self, error):
        # type (Exception) -> Monad[Exception]
        '''
        Fail: E -> ME

        Return a Monad of given Exception.

        Args:
            error (Exception): Error.

        Returns:
            Monad: Error Monad.
        '''
        return fail(self, error)

    def __and__(self, func):
        # type: (Callable[[A], B]) -> MB
        '''
        Functor map: (A -> B) -> MB

        Given a function A to B, return a Monad of B (MB).
        Example: m & (lambda x: x + 2)

        Args:
            func (function): Function (A -> B).

        Returns:
            Monad[B]: Monad of B.
        '''
        return self.fmap(func)

    def __xor__(self, monad_func):
        # type: (MA, Monad[Callable[[A], B]]) -> MB
        '''
        Applicative: MA -> M(A -> B) -> MB

        .. image:: resources/app.png

        Given a Monad of A (MA) and a Monad of a function A to B, return a Monad
        of B (MB).
        Example: m ^ Monad.wrap(lambda x: x + 2)

        Args:
            monad (Monad): Monad of A.
            func (Monad): Monad of function (A -> B).

        Raises:
            EnforceError: If monad is not Monad subclass or instance.

        Returns:
            Monad[B]: Monad of B.
        '''
        return self.app(monad_func)

    def __rshift__(self, func):
        # type: (Callable[[A], MB]) -> MB
        '''
        Bind: (A -> MB) -> MB

        Given a function A to MB, return a Monad of B (MB).
        Example: m >> Monad

        Args:
            func (function): Function (A -> MB).

        Returns:
            Monad[B]: Monad of B.
        '''
        return self.bind(func)


Monadlike = Union[Monad, Type[Monad]]
MA = Monad[A]
MB = Monad[B]
MC = Monad[C]
