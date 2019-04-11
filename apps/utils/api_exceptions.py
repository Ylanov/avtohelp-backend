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


class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """
    def __init__(self, code):
        super().__init__(code)
        self.code = code


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


class MessagesNotFound(exceptions.APIException):
    """Message not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Message not found')
    extended_status_code = '%s.2' % status.HTTP_404_NOT_FOUND


class CityNotFound(exceptions.APIException):
    """User not found."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('City with ID %s, not found')
    extended_status_code = '%s.3' % status.HTTP_404_NOT_FOUND

    def __init__(self, city_id):
        self.default_detail = dict(detail=self.default_detail % city_id,
                                   status_code=self.extended_status_code)
        super().__init__()


class CodeIsNotAcceptedError(ValidationErrorMixin):
    """Invalid value send was sended"""
    default_detail = _('Invalid value was sended')
    extended_status_code = '%s.1' % ValidationErrorMixin.status_code


class CarBrandIsNotFound(ValidationErrorMixin):
    """Car brand is not found"""
    default_detail = _('Car brand is not found in DB')
    extended_status_code = '%s.2' % ValidationErrorMixin.status_code

    def __init__(self, brand_id):
        self.default_detail = dict(detail=self.default_detail % brand_id,
                                   status_code=self.extended_status_code)
        super().__init__()


class CarBrandModelIsNotFound(ValidationErrorMixin):
    """Model of car brand is not found"""
    default_detail = _('Model of car brand is not found in DB')
    extended_status_code = '%s.3' % ValidationErrorMixin.status_code

    def __init__(self, model_id):
        self.default_detail = dict(detail=self.default_detail % model_id,
                                   status_code=self.extended_status_code)
        super().__init__()


class CarColorNotFound(ValidationErrorMixin):
    """Car color is not found"""
    default_detail = _('Car color is not found in DB')
    extended_status_code = '%s.4' % ValidationErrorMixin.status_code

    def __init__(self, color_id):
        self.default_detail = dict(detail=self.default_detail % color_id,
                                   status_code=self.extended_status_code)
        super().__init__()


class AlreadyFriends(ValidationErrorMixin):
    """Users are already friends"""
    default_detail = _('User ID %s and User ID %s are already friends')
    extended_status_code = '%s.5' % ValidationErrorMixin.status_code

    def __init__(self, owner, user):
        self.default_detail = dict(detail=self.default_detail % (owner, user),
                                   status_code=self.extended_status_code)
        super().__init__()


class AlreadyBlacked(ValidationErrorMixin):
    """User is already in Blacklist"""
    default_detail = _('User with ID %s is already in Blacklist User ID %s')
    extended_status_code = '%s.6' % ValidationErrorMixin.status_code

    def __init__(self, owner, user):
        self.default_detail = dict(detail=self.default_detail % (user, owner),
                                   status_code=self.extended_status_code)
        super().__init__()


class FriendRequestAlreadyExists(ValidationErrorMixin):
    """Friend request already exists"""
    default_detail = _('Friend request from User %s to User %s, already exists')
    extended_status_code = '%s.7' % ValidationErrorMixin.status_code

    def __init__(self, owner, invited):
        self.default_detail = dict(detail=self.default_detail % (owner, invited),
                                   status_code=self.extended_status_code)
        super().__init__()


class EqualIDError(ValidationErrorMixin):
    """Sent IDs are the same"""
    default_detail = _('Sent IDs are the same')
    extended_status_code = '%s.8' % ValidationErrorMixin.status_code

    def __init__(self):
        self.default_detail = dict(detail=self.default_detail,
                                   status_code=self.extended_status_code)
        super().__init__()


class ArentFriendsError(ValidationErrorMixin):
    """Users aren't friends"""
    default_detail = _('User %s and User %s aren\'t friends')
    extended_status_code = '%s.9' % ValidationErrorMixin.status_code

    def __init__(self, owner, user):
        self.default_detail = dict(detail=self.default_detail % (owner, user),
                                   status_code=self.extended_status_code)
        super().__init__()


class ChatRoomAlreadyExistsError(ValidationErrorMixin):
    """Chat room already exists"""
    default_detail = _('Chat room for User %s to User %s, already exists')
    extended_status_code = '%s.10' % ValidationErrorMixin.status_code

    def __init__(self, initiator, participant):
        self.default_detail = dict(detail=self.default_detail % (initiator, participant),
                                   status_code=self.extended_status_code)
        super().__init__()


class AreFoesError(ValidationErrorMixin):
    """Users aren't foes"""
    default_detail = _('User %s and User %s are foes')
    extended_status_code = '%s.11' % ValidationErrorMixin.status_code

    def __init__(self, owner, user):
        self.default_detail = dict(detail=self.default_detail % (owner, user),
                                   status_code=self.extended_status_code)
        super().__init__()


class CarNotFound(ValidationErrorMixin):
    """Car is not found"""
    default_detail = _('Car is not found in DB')
    extended_status_code = '%s.12' % ValidationErrorMixin.status_code

    def __init__(self):
        self.default_detail = dict(detail=self.default_detail,
                                   status_code=self.extended_status_code)
        super().__init__()


