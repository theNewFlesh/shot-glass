from typing import Callable, Generic, TypeVar  # noqa: F401
A = TypeVar('A')
B = TypeVar('B')
# ------------------------------------------------------------------------------


def wrap(monad, data):
    # type: (Monad, A) -> Monad[A]
    return monad.wrap(data)


def unwrap(monad):
    # type: (Monad[A]) -> A
    return monad._data


def fmap(monad, func):
    # type: (Monad[A], Callable[[A], B]) -> Monad[B]
    return wrap(monad, func(unwrap(monad)))


def applicative(monad, monad_func):
    # type: (Monad[A], Monad[Callable[[A], B]]) -> Monad
    func = unwrap(monad_func)
    value = unwrap(monad)
    return wrap(monad, func(value))


def bind(monad, func):
    # type: (Monad[A], Callable[[A], Monad[B]]) -> Monad[B]
    return func(unwrap(monad))


def right(monad_a, monad_b):
    # type: (Monad[A], Monad[B]) -> Monad[B]
    return monad_b


def fail(monad, error):
    # type (Monad, str) -> Monad[str]
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
