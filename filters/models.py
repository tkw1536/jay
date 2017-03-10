import json

from django.db import models

from django.contrib import admin

from django.core.exceptions import ValidationError

from settings.models import VotingSystem

import filters.forest as forest

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
			self.tree = json.dumps(forest.parse(self.value))
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
			return forest.matches(json.loads(self.tree), obj)
		except Exception as e:
			import sys
			sys.stderr.write(e)
			return False

	def map_matches(self, objs):

		try:
			return forest.map_match(json.loads(self.tree), objs)
		except Exception as e:
			return False

	def canEdit(self, user):
		"""
			Checks if a user can edit this UserFilter.
		"""

		return self.system.isAdmin(user)

	def get_absolute_url(self):
		from django.core.urlresolvers import reverse
		return reverse('filters:edit', kwargs={'filter_id':self.id})

admin.site.register(UserFilter)
