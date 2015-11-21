from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin

from settings.models import VotingSystem


# Create your models here.
class Vote(models.Model):
	system = models.ForeignKey(VotingSystem)

	name = models.CharField(max_length = 64)
	machine_name = models.SlugField(max_length = 64)

	description = models.TextField()

	creator = models.ForeignKey(User)

	min_votes = models.IntegerField()
	max_votes = models.IntegerField()

	def __unicode__(self):
		return u'[%s] %s' % (self.machine_name, self.name)


class Option(models.Model):
	vote = models.ForeignKey(Vote)

	number = models.IntegerField()

	name = models.CharField(max_length = 64)
	description = models.TextField(blank = True)

	picture_url = models.URLField(blank = True)

	personal_link = models.URLField(blank = True)
	link_name = models.CharField(blank = True, max_length = 16)

	count = models.IntegerField(default = 0, blank = True)

	def __unicode__(self):
		return u'[%s] %s' % (self.number, self.name)

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

	vote = models.ForeignKey(Vote)

	open_time = models.DateTimeField(null = True)
	close_time = models.DateTimeField(null = True)
	public_time = models.DateTimeField(null = True)
	stage = models.CharField(max_length = 1, choices = STAGES, default = INIT)

	def __unicode__(self):
		return self.stage

class ActiveVote(models.Model):
	vote = models.ForeignKey(Vote)

	user = models.ForeignKey(User)

	def __unicode__(self):
		return u'%s voted for %s' % (self.user, self.vote)

class PassiveVote(models.Model):
	vote = models.OneToOneField(Vote)

	num_voters = models.IntegerField()
	num_eligible = models.IntegerField()

	def __unicode__(self):
		return u'%s of %s voted' % (self.num_voters, self.num_eligible)

admin.site.register(Vote)
admin.site.register(Option)
admin.site.register(Status)
admin.site.register(ActiveVote)
admin.site.register(PassiveVote)
