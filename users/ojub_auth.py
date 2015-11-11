from django.conf import settings
from django.contrib.auth.models import User

import requests

OPENJUB_BASE = "https://api.jacobs-cs.club/"

class OjubBackend(object):
	"""
	Authenticates credentials against the OpenJUB database.

	The URL for the server is configured by OPENJUB_BASE in the settings.

	This class does not fill in user profiles, this has to be handled
	in other 
	"""
	def authenticate(self, username=None, password=None):
		r = requests.post(OPENJUB_BASE + "auth/signin", 
			data = {'username':username, 'password': password})

		if r.status_code != requests.codes.ok:
			return None

		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = User(username=username, password="this does not matter")

			if user.username in ["lkuboschek", "twiesing"]:
				user.is_staff = True
				user.is_superuser = True

			user.save()

		return user

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None

