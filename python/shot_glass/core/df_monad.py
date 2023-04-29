from typing import Callable, Type, TypeVar  # noqa: F401

import pandas as pd  # noqa: F401

import shot_glass.core.monad as sgm

A = TypeVar('A')
B = TypeVar('B')
# ------------------------------------------------------------------------------


class DFMonad(sgm.Monad):
    def __init__(self, data):
        # type: (pd.DataFrame) -> None
        super().__init__(data)

    def __repr__(self):
        # type: () -> str
        '''
        String representation of DFMonad instance.
        '''
        return 'DFMonad\n' + self._data.__repr__()

    @classmethod
    def wrap(cls, data):
        # type: (pd.DataFrame) -> DFMonad
        return cls(data)

    # ELEMENTS------------------------------------------------------------------
    def applymap(self, func, monad=sgm.Monad):
        # type: (Callable[[A], B], Type[sgm.Monad]) -> DFMonad
        data = self._data.applymap(lambda x: monad.wrap(x).fmap(func).unwrap())
        return self.wrap(data)

    def wrap_elements(self, monad=sgm.Monad):
        # type: (Type[sgm.Monad]) -> DFMonad
        data = self._data.applymap(monad.wrap)
        return self.wrap(data)

    def unwrap_elements(self):
        # type: () -> DFMonad
        data = self._data.applymap(lambda x: x.unwrap())
        return self.wrap(data)

    def fmap_elements(self, func):
        # type: (Callable[[A], B]) -> DFMonad
        data = self._data.applymap(lambda x: x.fmap(func))
        return self.wrap(data)

    def app_elements(self, func):
        # type: (sgm.Monad[Callable[[A], B]]) -> DFMonad
        data = self._data.applymap(lambda x: x.app(func))
        return self.wrap(data)

    def bind_elements(self, func):
        # type: (Callable[[A], sgm.Monad[B]]) -> DFMonad
        data = self._data.applymap(lambda x: x.bind(func))
        return self.wrap(data)

    # ROWS----------------------------------------------------------------------
    def wrap_rows(self, monad=sgm.Monad, axis=0):
        # type: (Type[sgm.Monad], int) -> DFMonad
        data = self._data.apply(monad.wrap, axis=axis)
        return self.wrap(data)

    def unwrap_rows(self, axis=0):
        # type: (int) -> DFMonad
        data = self._data.apply(lambda x: x.unwrap(), axis=axis)
        return self.wrap(data)

    def fmap_rows(self, func, axis=0):
        # type: (Callable[[A], B], int) -> DFMonad
        data = self._data.apply(lambda x: x.fmap(func), axis=axis)
        return self.wrap(data)

    def app_rows(self, func, axis=0):
        # type: (sgm.Monad[Callable[[A], B]], int) -> DFMonad
        data = self._data.apply(lambda x: x.app(func), axis=axis)
        return self.wrap(data)

    def bind_rows(self, func, axis=0):
        # type: (Callable[[A], sgm.Monad[B]], int) -> DFMonad
        data = self._data.apply(lambda x: x.bind(func), axis=axis)
        return self.wrap(data)
