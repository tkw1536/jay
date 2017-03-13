from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.contrib import admin

import json


# Create your models here.
class Admin(models.Model):
    user = models.ForeignKey(User)
    system = models.ForeignKey("settings.VotingSystem")

    class Meta():
        unique_together = (("system", "user"))

    def __str__(self):
        return u'[%s] %s' % (self.system.machine_name, self.user)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    details = models.TextField()

    def __str__(self):
        return u'[Profile] %s' % (self.user.username)

    def clean(self):
        # make sure that the details are a valid json object
        try:
            json.loads(self.details)
        except:
            raise ValidationError({
                'details': ValidationError('Details needs to be a valid JSON object', code='invalid')
            })

    def isSuperAdmin(self):
        """
            Returns if this user is a SuperAdmin.
        """
        return self.user.is_superuser

admin.site.register(Admin)
admin.site.register(UserProfile)
