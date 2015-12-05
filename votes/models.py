from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin

from settings.models import VotingSystem
from filters.models import UserFilter

from jay.restricted import is_restricted_word

# Create your models here.
class Vote(models.Model):
	system = models.ForeignKey(VotingSystem)

	name = models.CharField(max_length = 64)
	machine_name = models.SlugField(max_length = 64)

	filter = models.ForeignKey(UserFilter, null=True)
	status = models.OneToOneField('Status')

	description = models.TextField()

	creator = models.ForeignKey(User)

	min_votes = models.IntegerField()
	max_votes = models.IntegerField()

	class Meta():
		unique_together = (("system", "machine_name"))

	def __str__(self):
		return u'[%s] %s' % (self.machine_name, self.name)

	def clean(self):
		is_restricted_word('machine_name', self.machine_name)

	def canEdit(self, user):
		"""
			Checks if a user can edit this vote.
		"""
		return user.isAdminFor(self.system)

	def canBeModified(self):
		"""
			Checks if this vote can still be modified.
		"""
		return self.status.stage == "I"
class Option(models.Model):
	vote = models.ForeignKey(Vote)

	number = models.IntegerField()

	name = models.CharField(max_length = 64)
	description = models.TextField(blank = True)

	picture_url = models.URLField(blank = True)

	personal_link = models.URLField(blank = True)
	link_name = models.CharField(blank = True, max_length = 16)

	count = models.IntegerField(default = 0, blank = True)
	
	class Meta():
		unique_together = (("vote", "number"))

	def __str__(self):
		return u'[%s] %s' % (self.number, self.name)

	def canEdit(self, user):
		"""
			Checks if a user can edit this option.
		"""
		return self.vote.canEdit(user)

class Status(models.Model):
	INIT = 'I'
	STAGED = 'S'
	OPEN = 'O'
	CLOSE = 'C'
	PUBLIC = 'P'

	STAGES = (
		(INIT, 'Init'),
		(STAGED, 'Staged'),
		(OPEN, 'Open'),
		(CLOSE, 'Close'),
		(PUBLIC, 'Results public')
	)

	open_time = models.DateTimeField(blank = True, null = True)
	close_time = models.DateTimeField(blank = True, null = True)
	public_time = models.DateTimeField(blank = True, null = True)
	stage = models.CharField(max_length = 1, choices = STAGES, default = INIT)

	def __str__(self):
		return self.stage

class ActiveVote(models.Model):
	vote = models.ForeignKey(Vote)

	user = models.ForeignKey(User)

	def __str__(self):
		return u'%s voted for %s' % (self.user, self.vote)

class PassiveVote(models.Model):
	vote = models.OneToOneField(Vote)

	num_voters = models.IntegerField()
	num_eligible = models.IntegerField()

	def __str__(self):
		return u'%s of %s voted' % (self.num_voters, self.num_eligible)

admin.site.register(Vote)
admin.site.register(Option)
admin.site.register(Status)
admin.site.register(ActiveVote)
admin.site.register(PassiveVote)
