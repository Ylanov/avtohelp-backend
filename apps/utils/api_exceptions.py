from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework import status

from utils.custom_statuses import HTTP_420_ENHACE_YOUR_CALM


"""
MIXINS
"""


class ValidationErrorMixin(exceptions.APIException):
    """Validation mixin"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Validation error.')


"""
EXCEPTIONS
"""


class TooOftenTriedError(exceptions.APIException):
    """Too often tried to enter the code."""
    status_code = HTTP_420_ENHACE_YOUR_CALM
    default_detail = _('Too often tried to request the code, try to request the code after %s seconds.'
                       % settings.SMS_SEND_DELAY)


class TemporaryLockError(exceptions.APIException):
    """Temporary Lock Error."""
    status_code = status.HTTP_423_LOCKED
    default_detail = _('Temporary Lock')


class UserNotFound(exceptions.APIException):
    """User not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('User not found')
    extended_status_code = '%s.1' % status.HTTP_404_NOT_FOUND


class CodeIsNotAcceptedError(ValidationErrorMixin):
    """Invalid value send was sended"""
    default_detail = _('Invalid value was sended')
    extended_status_code = '%s.2' % ValidationErrorMixin.status_code
