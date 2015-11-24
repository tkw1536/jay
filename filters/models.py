from django.db import models

from django.contrib import admin

from django.core.exceptions import ValidationError

from settings.models import VotingSystem

from filters.logic.operations import json_string, evaluate_tree

# Create your models here.
class UserFilter(models.Model):
	system = models.ForeignKey(VotingSystem)
	value = models.CharField(max_length=255)
	tree = models.TextField()

	def __unicode__(self):
		return u'%s %s %s' % (self.value, self.system)

	def clean(self):
		"""
			Cleans this model and maks sure the value if valid.
		"""

		# try to clean the value
		newtree = json_string(self.tree)

		# if it didn't work, throw an error
		if newtree == None:
			raise ValidationError({
				'tree': ValidationError('Value for tree is not a valid logical tree. ', code='invalid')
			})

		# else set the property
		self.tree = newtree

	def matches(self, obj):
		"""
			Checks if this filter matches an object.
		"""
		return evaluate_tree(self.tree, obj)


admin.site.register(UserFilter)
