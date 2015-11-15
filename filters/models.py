from django.db import models

from django.contrib import admin

from django.core.exceptions import ValidationError

from settings.models import VotingSystem

from filters.filter_ops import clean_string, evaluate_json

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
		newtree = clean_string(self.tree)

		# if it didn't work, throw an error
		if newtree == None:
			raise ValidationError({
				'tree': ValidationError('Tree object need to be a valid tree object. ', code='invalid')
			})

		# else set the property
		self.tree = newtree

	def matches(self, obj):
		"""
			Checks if this filter matches an object.
		"""
		return evaluate_json(self.tree, obj)


admin.site.register(UserFilter)
