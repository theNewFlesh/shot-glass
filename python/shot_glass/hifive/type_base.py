from enum import Enum

from shot_glass.core.tools import ValidationError
# ------------------------------------------------------------------------------


class HiFiveTypeBase(Enum):
    '''
    Enum base class for HiFive enums.
    '''
    def __init__(self, fullname, indicator, type_, validator, order):
        '''
        Args:
            fullname (str): Fullname of enum item.
            indicator (str): Single character indicating enum item.
            validator (function): Function used to validate values  \
                with enum. **Must return boolean**.
        '''
        self.fullname = fullname
        self.indicator = indicator
        self.type_ = type_
        self.validator = validator
        self.order = order

    def is_valid_value(self, value):
        '''
        Args:
            value (object): Value to be tested.

        Returns:
            bool: Whether given value is valid according to its validator.
        '''
        return self.validator(value)

    @classmethod
    def is_valid_fullname(cls, fullname):
        '''
        Args:
            fullname (str): Fullname to be tested.

        Returns:
            bool: Whether given fullname is valid.
        '''
        return fullname in cls.get_fullnames()

    @classmethod
    def is_valid_indicator(cls, indicator):
        '''
        Args:
            indicator (str): Indicator to be tested.

        Returns:
            bool: Whether given indicator is valid.
        '''
        return indicator in cls.get_indicators()

    @classmethod
    def from_fullname(cls, fullname):
        '''
        Args:
            fullname (str): Fullname from which to derive enum.

        Returns:
            HiFiveTypeBase: Enum associated with given fullname.
        '''
        for dt in cls.__members__.values():
            if dt.fullname == fullname:
                return dt
        msg = f'{fullname} is not a valid fullname.'
        raise ValidationError(msg)

    @classmethod
    def from_indicator(cls, indicator):
        '''
        Args:
            indicator (str): Indicator from which to derive enum.

        Returns:
            HiFiveTypeBase: Enum  with given indicator.
        '''
        for dt in cls.__members__.values():
            if dt.indicator == indicator:
                return dt
        msg = f'{indicator} is not a valid indicator.'
        raise ValidationError(msg)

    @classmethod
    def get_fullnames(cls):
        '''
        Returns:
            list: A list of all the fullnames in the enum.
        '''
        output = list(cls.__members__.values())
        output = [x.fullname for x in output]
        return output

    @classmethod
    def get_indicators(cls):
        '''
        Returns:
            list: A list of all the indicators in the enum.
        '''
        output = list(cls.__members__.values())
        output = [x.indicator for x in output]
        return output

    @classmethod
    def get_validators(cls):
        '''
        Returns:
            list: A list of all the validators in the enum.
        '''
        output = list(cls.__members__.values())
        output = [x.validator for x in output]
        return output
