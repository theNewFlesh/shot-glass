from typing import Any, Callable, Generic, Type, TypeVar, Union  # noqa: F401

from lunchbox.enforce import Enforce, EnforceError

A = TypeVar('A')
B = TypeVar('B')
# ------------------------------------------------------------------------------


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


def fmap(monad, func):
    # type: (Monad[A], Callable[[A], B]) -> Monad[B]
    '''
    Functor map: MA -> (A -> B) -> MB

    .. image:: resources/fmap.png

    Given a Monad of A (MA) and a function A to B, return a Monad of B (MB).

    Args:
        monad (Monad): Monad of A.
        func (function): Function (A -> B).

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad[B]: Monad of B.
    '''
    enforce_monad(monad)
    return wrap(monad, func(unwrap(monad)))


def app(monad, monad_func):
    # type: (Monad[A], Monad[Callable[[A], B]]) -> Monad[B]
    '''
    Applicative: MA -> M(A -> B) -> MB

    .. image:: resources/app.png

    Given a Monad of A (MA) and a Monad of a function A to B, return a Monad
    of B (MB).

    Args:
        monad (Monad): Monad of A.
        func (Monad): Monad of function (A -> B).

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad[B]: Monad of B.
    '''
    enforce_monad(monad)
    func = unwrap(monad_func)
    value = unwrap(monad)
    return wrap(monad, func(value))


def bind(monad, func):
    # type: (Monad[A], Callable[[A], Monad[B]]) -> Monad[B]
    '''
    Bind: MA -> (A -> MB) -> MB

    .. image:: resources/bind.png

    Given a Monad of A (MA) and a function A to MB, return a Monad of B (MB).

    Args:
        monad (Monad): Monad of A.
        func (function): Function (A -> MB).

    Raises:
        EnforceError: If monad is not Monad subclass or instance.

    Returns:
        Monad[B]: Monad of B.
    '''
    enforce_monad(monad)
    return func(unwrap(monad))


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
    msg = 'Error must be an instance of Exception. Given value: {a}'
    Enforce(error, 'instance of', Exception, message=msg)
    return wrap(monad, error)
# ------------------------------------------------------------------------------


class Monad(Generic[A]):
    '''
    Monad is a generic base class for monads. It implements all the monad
    functions as methods which take itself as the first argument.
    '''

    def __init__(self, data):
        # type: (A) -> None
        '''
        Constructs monad instance.

        Args:
            data (object): Data to be wrapped with Monad.
        '''
        self._data = data

    @classmethod
    def wrap(cls, data):
        # type: (A) -> Monad[A]
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
        # type: (Callable[[A], B]) -> Monad[B]
        '''
        Functor map: (A -> B) -> MB

        Given a function A to B, return a Monad of B (MB).

        Args:
            func (function): Function (A -> B).

        Returns:
            Monad[B]: Monad of B.
        '''
        return fmap(self, func)

    def app(self, monad_func):
        # type: (Monad[Callable[[A], B]]) -> Monad
        '''
        Applicative: M(A -> B) -> MB

        Given a Monad of a function A to B, return a Monad of B (MB).

        Args:
            func (Monad): Monad of function (A -> B).

        Returns:
            Monad[B]: Monad of B.
        '''
        return app(self, monad_func)

    def bind(self, func):
        # type: (Callable[[A], Monad[B]]) -> Monad[B]
        '''
        Bind: (A -> MB) -> MB

        Given a function A to MB, return a Monad of B (MB).

        Args:
            func (function): Function (A -> MB).

        Returns:
            Monad[B]: Monad of B.
        '''
        return bind(self, func)

    def right(self, monad):
        # type: (Monad[B]) -> Monad[B]
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


Monadlike = Union[Monad, Type[Monad]]
