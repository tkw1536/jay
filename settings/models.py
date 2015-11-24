from django.db import models

from django.contrib import admin


class VotingSystem(models.Model):
	subdomain_name = models.SlugField(max_length = 30, unique = True, null = True)
	machine_name = models.SlugField(max_length = 50, unique = True)
	simple_name = models.CharField(max_length = 80)

	def __str__(self):
		return u'[%s] %s' % (self.machine_name, self.simple_name)

admin.site.register(VotingSystem)
