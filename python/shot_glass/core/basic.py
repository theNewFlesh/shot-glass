from typing import Any, Callable  # noqa: F401

import pandas as pd

import shot_glass.core.monad as sgm
from shot_glass.core.monad import Monad
# ------------------------------------------------------------------------------


class Maybe(Monad):
    @classmethod
    def just(cls, value):
        return cls(value)

    @classmethod
    def nothing(cls):
        return cls(None)

    def __repr__(self):
        if self.state == 'just':
            return f'Just({self._data})'
        return 'Nothing'

    @property
    def state(self):
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
        return f'{self.state.capitalize()}({self._data})'

    @property
    def state(self):
        if isinstance(self._data, Exception):
            return 'failure'
        return 'success'

    def fmap(self, func):
        return sgm.catch(self, sgm.fmap)(func, self)

    def bind(self, func):
        return sgm.catch(self, sgm.bind)(func, self)

    def app(self, func):
        return sgm.catch(self, sgm.app)(func, self)
