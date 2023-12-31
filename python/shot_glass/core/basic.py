from typing import Any, Callable, TypeVar  # noqa: F401

import pandas as pd

import shot_glass.core.monad as sgm
from shot_glass.core.monad import Monad

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
# ------------------------------------------------------------------------------


class Maybe(Monad):
    @classmethod
    def just(cls, value):
        # type: (Any) -> Maybe
        return cls(value)

    @classmethod
    def nothing(cls):
        # type: () -> Maybe
        return cls(None)

    def __repr__(self):
        # type: () -> str
        if self.state == 'just':
            return f'Just({self._data})'
        return 'Nothing'

    @property
    def state(self):
        # type: () -> str
        data = self._data
        if data is None or pd.isna(data):
            return 'nothing'
        return 'just'


class Try(Monad):
    @classmethod
    def success(cls, value):
        # type: (Any) -> Try
        return sgm.succeed(cls, value)

    @classmethod
    def failure(cls, error):
        # type: (Exception) -> Try
        return sgm.fail(cls, error)

    def __repr__(self):
        # type: () -> str
        return f'{self.state.capitalize()}({self._data})'

    @property
    def state(self):
        # type: () -> str
        if isinstance(self._data, Exception):
            return 'failure'
        return 'success'

    def fmap(self, func):
        # type: (Callable[[A], B]) -> Try[B | Exception]
        '''
        Functor map: (A -> B) -> MB

        Given a function A to B, return a Monad of B (MB).
        Example: m.fmap(lambda x: x + 2)

        Args:
            func (function): Function (A -> B).

        Returns:
            Try[B]: Try Monad of B.
        '''
        return sgm.catch(self, sgm.fmap)(func, self)

    def bind(self, func):
        # type: (Callable[[A], Monad[B]]) -> Try[B | Exception]
        '''
        Bind: (A -> MB) -> MB

        Given a function A to MB, return a Monad of B (MB).

        Args:
            func (function): Function (A -> MB).

        Returns:
            Try[B]: Try Monad of B.
        '''
        return sgm.catch(self, sgm.bind)(func, self)

    def app(self, monad_func):
        # type: (Monad[Callable[[A], B]]) -> Try[B | Exception]
        '''
        Applicative: M(A -> B) -> MB

        Given a Monad of a function A to B, return a Monad of B (MB).

        Args:
            monad_func (Monad): Monad of function (A -> B).

        Returns:
            Try[B]: Try Monad of B.
        '''
        return sgm.catch(self, sgm.app)(monad_func, self)
