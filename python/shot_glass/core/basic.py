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
        '''
        Just constructor for Maybe class.

        Args:
            value (object): Non-null value.

        Returns:
            Maybe: Maybe monad of value.
        '''
        return cls(value)

    @classmethod
    def nothing(cls):
        # type: () -> Maybe
        '''
        Nothing constructor for Maybe class.

        Returns:
            Maybe: Nothing monad.
        '''
        return cls(None)

    def __repr__(self):
        # type: () -> str
        '''String representation of monad.'''
        if self.state == 'just':
            return f'Just({self._data})'
        return 'Nothing'

    @property
    def state(self):
        # type: () -> str
        '''State of monad. Either just or nothing.'''
        data = self._data
        if data is None or pd.isna(data):
            return 'nothing'
        return 'just'
# ------------------------------------------------------------------------------


class Try(Monad):
    @classmethod
    def success(cls, value):
        # type: (Any) -> Try
        '''
        Success constructor for Try class.

        Args:
            value (object): Non-error value.

        Returns:
            Maybe: Try monad of value.
        '''
        return sgm.succeed(cls, value)

    @classmethod
    def failure(cls, error):
        # type: (Exception) -> Try
        '''
        Success constructor for Try class.

        Args:
            error (Exception): Error.

        Returns:
            Maybe: Try monad of error.
        '''
        return sgm.fail(cls, error)

    def __repr__(self):
        # type: () -> str
        '''String representation of monad.'''
        return f'{self.state.capitalize()}({self._data})'

    @property
    def state(self):
        # type: () -> str
        '''State of monad. Either success or failure.'''
        if isinstance(self._data, Exception):
            return 'failure'
        return 'success'

    def fmap(self, func):
        # type: (Callable[[A], B]) -> Try
        '''
        Functor map: (A -> B) -> MB

        Given a function A to B, return a Monad of B (MB).
        Example: m.fmap(lambda x: x + 2)

        Args:
            func (function): Function (A -> B).

        Returns:
            Try[B]: Try Monad of B.
        '''
        try:
            return self.fmap(func)
        except Exception as error:
            return self.fail(error)

    def bind(self, func):
        # type: (Callable[[A], Monad[B]]) -> Try
        '''
        Bind: (A -> MB) -> MB

        Given a function A to MB, return a Monad of B (MB).

        Args:
            func (function): Function (A -> MB).

        Returns:
            Try[B]: Try Monad of B.
        '''
        try:
            return self.bind(func)
        except Exception as error:
            return self.fail(error)

    def app(self, monad_func):
        # type: (Monad[Callable[[A], B]]) -> Try
        '''
        Applicative: M(A -> B) -> MB

        Given a Monad of a function A to B, return a Monad of B (MB).

        Args:
            monad_func (Monad): Monad of function (A -> B).

        Returns:
            Try[B]: Try Monad of B.
        '''
        try:
            return self.app(monad_func)
        except Exception as error:
            return self.fail(error)
