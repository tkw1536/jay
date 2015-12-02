from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

from django.contrib import admin

from settings.models import VotingSystem

import json

# Create your models here.
class Admin(models.Model):
	user = models.ForeignKey(User)
	system = models.ForeignKey(VotingSystem)

	def __str__(self):
		return u'[%s] %s' % (self.system.machine_name, self.user)

class SuperAdmin(models.Model):
	user = models.ForeignKey(User)

	def __str__(self):
		return u'%s' % (self.user)

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
		return self.user.superadmin_set.count() > 0
	def isAdminFor(self, system):
		"""
			Checks if this user can administer a certain voting system.
		"""
		return self.getAdministratedSystems().filter(system).count() == 1
	def getAdministratedSystems(self):
		"""
			Returns all voting systems this user can administer.
		"""
		# if we are a superadmin we can manage all systems
		if self.isSuperAdmin():
			return VotingSystem.objects.all()

		# else return only the systems we are an admin for.
		else:
			return self.user.admin_set.values_list('system', flat=True).distinct()
	def isElevated(self):
		"""
			Checks if this user is an elevated user. 
			
			(i. e. if they are a superadmin or admin for some voting system)
		"""
		
		# thy are a superadmin
		if self.isSuperAdmin():
			return True
		
		# they administer some voting system
		return self.user.admin_set.count() > 0

admin.site.register(Admin)
admin.site.register(SuperAdmin)
admin.site.register(UserProfile)
