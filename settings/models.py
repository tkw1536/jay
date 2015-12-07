from django.db import models

from django.contrib import admin

from jay.restricted import is_restricted_word


class VotingSystem(models.Model):
	machine_name = models.SlugField(max_length = 50, unique = True)
	simple_name = models.CharField(max_length = 80)

	def __str__(self):
		return u'[%s] %s' % (self.machine_name, self.simple_name)

	def clean(self):
		is_restricted_word('machine_name', self.machine_name)

	def canEdit(self, user):
		"""
			Checks if a user can edit this voting system.
		"""
		return user.isSuperAdmin()

	def isAdmin(self, user):
		"""
			Checks if a user is an administrator for this voting system.
		"""
		return user.isAdminFor(self)

admin.site.register(VotingSystem)
