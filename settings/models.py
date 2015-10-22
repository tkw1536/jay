from django.db import models

from django.contrib import admin

# Create your models here.
class GlobalSettings(models.Model):
	DOMAIN_NAME = 'FQDN'
	FORCE_HTTPS = 'HTTPS'
	ADMIN_MAIL  = 'ADM_MAIL'
	ADMIN_NAME  = 'ADM_NAME'

	KEY_CHOICES = (
		(DOMAIN_NAME, 'Domain Name'),
		(FORCE_HTTPS, 'Force HTTPS'),
		(ADMIN_MAIL, 'Admin de-mail'),
		(ADMIN_NAME, 'Admin name')
	)

	key = models.CharField(max_length = 8, choices = KEY_CHOICES)
	value = models.CharField(max_length = 256)

class VotingSystem(models.Model):
	subdomain_name = models.SlugField(max_length = 30, unique = True, null = True)
	machine_name = models.SlugField(max_length = 50, unique = True)
	simple_name = models.CharField(max_length = 80)

admin.site.register(GlobalSettings)
admin.site.register(VotingSystem)
