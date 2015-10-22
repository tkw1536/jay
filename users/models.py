from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin

from settings.models import VotingSystem

# Create your models here.
class Admin(models.Model):
	user = models.ForeignKey(User)
	system = models.ForeignKey(VotingSystem)

    def __unicode__(self):
        return u'[%s] %s' % (self.system.machine_name, self.user)

class SuperAdmin(models.Model):
	user = models.ForeignKey(User)

    def __unicode__(self):
        return u'%s' % (self.user)

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	username = models.CharField(max_length = 32, unique = True)
	fullname = models.CharField(max_length = 128)
	eid = models.IntegerField()

    def __unicode__(self):
        return u'[%s] %s' % (self.eid, self.fullname)

admin.site.register(Admin)
admin.site.register(SuperAdmin)
admin.site.register(UserProfile)
