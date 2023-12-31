from typing import Any, Callable  # noqa: F401

import pandas as pd

import shot_glass.core.monad as sgm
from shot_glass.core.monad import Monad
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
        return sgm.catch(self, sgm.fmap)(func, self)

    def bind(self, func):
        return sgm.catch(self, sgm.bind)(func, self)

    def app(self, func):
        return sgm.catch(self, sgm.app)(func, self)
