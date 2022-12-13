class ValidationError(Exception):
    '''
    Error raised by all validators.
    '''
    pass


class EmptyError(Exception):
    '''
    Error raised when given object is empty.
    '''
    pass
