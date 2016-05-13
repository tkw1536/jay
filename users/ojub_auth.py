from django.conf import settings
from django.contrib.auth.models import User

from users.models import UserProfile

import requests

OPENJUB_BASE = "https://api.jacobs.university/"

class OjubBackend(object):
	"""
	Authenticates credentials against the OpenJUB database.

	The URL for the server is configured by OPENJUB_BASE in the settings.

	This class does not fill in user profiles, this has to be handled
	in other places
	"""
	def authenticate(self, username=None, password=None):
		r = requests.post(OPENJUB_BASE + "auth/signin",
			data = {'username':username, 'password': password})

		if r.status_code != requests.codes.ok:
			return None

		resp = r.json()

		uname = resp['user']
		token = resp['token']

		details = requests.get(OPENJUB_BASE + "user/me",
			params = {'token':token})

		if details.status_code != requests.codes.ok:
			print("Could not get user details")
			return None

		try:
			user = User.objects.get(username=uname)
		except User.DoesNotExist:
			user = User(username=uname)

			user.set_unusable_password()

			# TODO Don't hardcode this
			if user.username in ["lkuboschek", "twiesing", "jinzhang", "rdeliallis"]:
				user.is_staff = True
				user.is_superuser = True

			data = details.json()

			user.first_name = data['firstName']
			user.last_name = data['lastName']
			user.email = data['email']

			user.save()

		# Make a user profile if there isn't one already
		try:
			profile = UserProfile.objects.get(user=user)
		except UserProfile.DoesNotExist:
			profile = UserProfile(user=user)

		profile.details = details.text
		profile.save()

		return user

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None

def get_all(username, password):
	r = requests.post(OPENJUB_BASE + "auth/signin",
		data = {'username':username, 'password': password})

	if r.status_code != requests.codes.ok:
		return None

	resp = r.json()

	uname = resp['user']
	token = resp['token']

	users = []

	TIMEOUT = 60

	request = requests.get(OPENJUB_BASE + "query",
		params = {'token':token, 'limit': 20000}, timeout = TIMEOUT)

	while True:
		if request.status_code != requests.codes.ok:
			return None
		else:
			# read json
			resjson = request.json()

			# load all the users
			users += resjson["data"]

			# if there was no data or no next field, continue
			if len(resjson["data"]) == 0 or not resjson["next"]:
				return users
			else:
				request = requests.get(resjson["next"], timeout = TIMEOUT)
