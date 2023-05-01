from typing import Callable, Type, TypeVar  # noqa: F401

import pandas as pd  # noqa: F401

import shot_glass.core.monad as sgm

A = TypeVar('A')
B = TypeVar('B')
# ------------------------------------------------------------------------------


class SMonad(sgm.Monad):
    def __init__(self, data):
        # type: (pd.Series) -> None
        super().__init__(data)

    def __repr__(self):
        # type: () -> str
        '''
        String representation of SMonad instance.
        '''
        return 'SMonad\n' + self._data.__repr__()

    @classmethod
    def wrap(cls, data):
        # type: (pd.Series) -> SMonad
        return cls(data)

    # ELEMENTS------------------------------------------------------------------
    def apply(self, func, monad=sgm.Monad):
        # type: (Callable[[A], B], Type[sgm.Monad]) -> SMonad
        data = self._data.apply(lambda x: monad.wrap(x).fmap(func).unwrap())
        return self.wrap(data)

    def wrap_elements(self, monad=sgm.Monad):
        # type: (Type[sgm.Monad]) -> SMonad
        data = self._data.apply(monad.wrap)
        return self.wrap(data)

    def unwrap_elements(self):
        # type: () -> SMonad
        data = self._data.apply(lambda x: x.unwrap())
        return self.wrap(data)

    def fmap_elements(self, func):
        # type: (Callable[[A], B]) -> SMonad
        data = self._data.apply(lambda x: x.fmap(func))
        return self.wrap(data)

    def app_elements(self, func):
        # type: (sgm.Monad[Callable[[A], B]]) -> SMonad
        data = self._data.apply(lambda x: x.app(func))
        return self.wrap(data)

    def bind_elements(self, func):
        # type: (Callable[[A], sgm.Monad[B]]) -> SMonad
        data = self._data.apply(lambda x: x.bind(func))
        return self.wrap(data)
