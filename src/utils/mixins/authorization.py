import re

from django.apps import apps
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class AuthorizationMixin(object):
    """Mixin for serializer AuthorizationSerializer"""

    def validate_phone(self, value):
        """Validate phone"""
        User = apps.get_model(app_label="account", model_name="User")

        qs = User.objects.filter(phone=value.as_e164)
        if not qs.exists():
            raise ValidationError(
                detail={
                    "detail": _("User with this phone number is not found")
                }
            )
        return value

    def validate_code(self, value):
        """Validate code method."""
        pattern = r"[0-9]{4}"
        if not re.fullmatch(pattern, str(value)):
            raise ValidationError(_("Invalid code"))
        return value
