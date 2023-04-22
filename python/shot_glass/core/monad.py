from typing import Any, Callable, Generic, TypeVar  # noqa: F401
A = TypeVar('A')
B = TypeVar('B')
# ------------------------------------------------------------------------------


def wrap(monad, data):
    # type: (Monad, A) -> Monad[A]
    '''
    Wrap: M -> A -> MA
    Given a Monad class or instance, create a new Monad with given data.

    Args:
        monad (Monad): Monad class or instance.
        data (Any): Data to be wrapped as Monad.

    Returns:
        Monad[A]: Monad of data.
    '''
    return monad.wrap(data)


def unwrap(monad):
    # type: (Monad[A]) -> A
    '''
    Unwrap: MA -> A
    Return the data of a given Monad instance.

    Args:
        monad (Monad): Monad instance.

    Returns:
        A: Monad data.
    '''
    return monad._data


def fmap(monad, func):
    # type: (Monad[A], Callable[[A], B]) -> Monad[B]
    '''
    Functor map: MA -> (A -> B) -> MB
    Given a Monad of A (MA) and a function A to B, return a Monad of B (MB).

    Args:
        monad (Monad): Monad of A.
        func (function): Function (A -> B).

    Returns:
        Monad[B]: Monad of B.
    '''
    return wrap(monad, func(unwrap(monad)))


def applicative(monad, monad_func):
    # type: (Monad[A], Monad[Callable[[A], B]]) -> Monad[B]
    '''
    Applicative: MA -> M(A -> B) -> MB
    Given a Monad of A (MA) and a Monad of a function A to B, return a Monad
    of B (MB).

    Args:
        monad (Monad): Monad of A.
        func (Monad): Monad of function (A -> B).

    Returns:
        Monad[B]: Monad of B.
    '''
    func = unwrap(monad_func)
    value = unwrap(monad)
    return wrap(monad, func(value))


def bind(monad, func):
    # type: (Monad[A], Callable[[A], Monad[B]]) -> Monad[B]
    '''
    Bind: MA -> (A -> MB) -> MB
    Given a Monad of A (MA) and a function A to MB, return a Monad of B (MB).

    Args:
        monad (Monad): Monad of A.
        func (function): Function (A -> MB).

    Returns:
        Monad[B]: Monad of B.
    '''
    return func(unwrap(monad))


def right(monad_a, monad_b):
    # type: (Monad[A], Monad[B]) -> Monad[B]
    '''
    Right: MA -> MB -> MB
    Given two Monads, a and b, return the right Monad b.

    Args:
        monad_a (Monad): Left monad.
        monad_b (Monad): Right monad.

    Returns:
        Monad: Right Monad.
    '''
    return monad_b


def fail(monad, error):
    # type (Monad, Exception) -> Monad[Exception]
    '''
    Fail: M -> E -> ME
    Given a Monad and error message, return a Monad of that error message.

    Args:
        monad (Monad): Monad to wrap error with.
        error (Exception): Error.

    Returns:
        Monad: Error Monad.
    '''
    return wrap(monad, error)
# ------------------------------------------------------------------------------


class Monad(Generic[A]):
    def __init__(self, data):
        # type: (A) -> None
        self._data = data

    @classmethod
    def wrap(cls, data):
        # type: (A) -> Monad[A]
        return cls(data)

    def unwrap(self):
        # type: () -> A
        return unwrap(self)

    def fmap(self, func):
        # type: (Callable[[A], B]) -> Monad[B]
        return fmap(self, func)

    def applicative(self, monad_func):
        # type: (Monad[Callable[[A], B]]) -> Monad
        return applicative(self, monad_func)

    def bind(self, func):
        # type: (Callable[[A], Monad[B]]) -> Monad[B]
        return bind(self, func)

    def right(self, monad_b):
        # type: (Monad[B]) -> Monad[B]
        return right(self, monad_b)

    def fail(self, error):
        # type (str) -> Monad[str]
        return fail(error)
