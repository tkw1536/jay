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
	user = models.OneToOneField(User, related_name="profile")
	details = models.TextField()

	def __unicode__(self):
		return u'[Profile] %s' % (self.user.username)

admin.site.register(Admin)
admin.site.register(SuperAdmin)
admin.site.register(UserProfile)
