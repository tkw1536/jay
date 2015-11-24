from django.db import models

from django.contrib import admin

from jay.restricted import is_restricted_word


class VotingSystem(models.Model):
	subdomain_name = models.SlugField(max_length = 30, unique = True, null = True)
	machine_name = models.SlugField(max_length = 50, unique = True)
	simple_name = models.CharField(max_length = 80)

	def __str__(self):
		return u'[%s] %s' % (self.machine_name, self.simple_name)

	def clean(self):
		is_restricted_word('machine_name', self.machine_name)

admin.site.register(VotingSystem)
