from typing import Callable, TypeVar  # noqa: F401

import pandas as pd  # noqa: F401

import shot_glass.core.monad as sgm

A = TypeVar('A')
B = TypeVar('B')
# ------------------------------------------------------------------------------


class DFMonad(sgm.Monad):
    def __init__(self, data):
        # type: (pd.DataFrame) -> None
        super().__init__(data)

    @classmethod
    def wrap(cls, data):
        # type: (pd.DataFrame) -> DFMonad
        return cls(data)

    def apply(self, func):
        # type: (Callable[[A], B]) -> DFMonad
        data = self._data \
            .apply(lambda x: sgm.wrap(sgm.Monad, x)) \
            .apply(lambda x: sgm.fmap(x, func))
        return self.wrap(data)

    def applymap(self, func):
        # type: (Callable[[A], B]) -> DFMonad
        data = self._data \
            .applymap(lambda x: sgm.wrap(sgm.Monad, x)) \
            .applymap(lambda x: sgm.fmap(x, func))
        return self.wrap(data)
