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

    def wrap_rows(self, monad=sgm.Monad):
        # type: (Type[sgm.Monad]) -> DFMonad
        data = self._data.apply(monad.wrap)
        return self.wrap(data)

    def unwrap_rows(self):
        # type: () -> DFMonad
        data = self._data.apply(sgm.unwrap)
        return self.wrap(data)

    def wrap_elements(self, monad=sgm.Monad):
        # type: (Type[sgm.Monad]) -> DFMonad
        data = self._data.applymap(monad.wrap)
        return self.wrap(data)

    def unwrap_elements(self):
        # type: () -> DFMonad
        data = self._data.applymap(sgm.unwrap)
        return self.wrap(data)

    def fmap_rows(self, func):
        # type: (Callable[[A], B]) -> DFMonad
        data = self._data \
            .apply(lambda x: sgm.fmap(x, func))
        return self.wrap(data)

    def fmap_elements(self, func):
        # type: (Callable[[A], B]) -> DFMonad
        data = self._data \
            .applymap(lambda x: sgm.fmap(x, func))
        return self.wrap(data)

    def app_rows(self, func):
        # type: (sgm.Monad[Callable[[A], B]]) -> DFMonad
        data = self._data \
            .apply(lambda x: sgm.app(x, func))
        return self.wrap(data)

    def app_elements(self, func):
        # type: (sgm.Monad[Callable[[A], B]]) -> DFMonad
        data = self._data \
            .applymap(lambda x: sgm.app(x, func))
        return self.wrap(data)

    def bind_rows(self, func):
        # type: (Callable[[A], sgm.Monad[B]]) -> DFMonad
        data = self._data \
            .apply(lambda x: sgm.bind(x, func))
        return self.wrap(data)

    def bind_elements(self, func):
        # type: (Callable[[A], sgm.Monad[B]]) -> DFMonad
        data = self._data \
            .applymap(lambda x: sgm.bind(x, func))
        return self.wrap(data)
