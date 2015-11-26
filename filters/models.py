from django.db import models

from django.contrib import admin

from django.core.exceptions import ValidationError

from settings.models import VotingSystem

import filters.logic_bridge as bridge

# Create your models here.
class UserFilter(models.Model):
	system = models.ForeignKey(VotingSystem)
	name = models.CharField(max_length=255)
	value = models.CharField(max_length=255)
	tree = models.TextField(blank=True)

	def __str__(self):
		return u'%s: %s' % (self.system.machine_name, self.name)

	def clean(self):
		try:
			self.tree = bridge.parse(self.value)
			self.tree = bridge.simplify(self.tree)
		except Exception as e:
			self.tree = None

		if self.tree == None:
			raise ValidationError({
	            'value': ValidationError('Value for \'value\' invalid: Can not parse into a valid logical tree. ', code='invalid')
	        })

	def matches(self, obj):
		"""
			Checks if this filter matches an object.
		"""

		try:
			return bridge.matches(self.tree, obj)
		except Exception as e:
			return False

admin.site.register(UserFilter)
