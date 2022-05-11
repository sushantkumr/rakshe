"""Collection of common exceptions."""


class UserError(Exception):
    """Raised to return an error to users."""


def bootbox_error(func):
    """Function decorator to convert UserErrors to bootbox errors.

    Warning:
    All user errors raised by the wrapped function will become bootbox errors.

    It is probably better to subclass UserError and throw different kinds of
    errors using its subclasses. Eg: BootboxError, BootboxInfo etc.
    """
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UserError as e:
            raise UserError({
                'type': 'alert-error',
                'message': e.args[0]
            })
    return func_wrapper
