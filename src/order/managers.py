from django.db import models


class AssistanceRequestManager(models.Manager):
    """Manager for AssistanceRequest model"""

    def make(self, **kwargs):
        """Make new assistance request"""
        obj = self.model(**kwargs)
        obj.save()
        obj.send_push_notification()
        return obj


class AssistanceRequestUserReadManager(models.Manager):
    """Manager for AssistanceRequest model"""

    def make(self, **kwargs):
        """Make new assistance request"""
        obj = self.model(**kwargs)
        obj.save()
        return obj
