from django.db import models
from django.contrib.auth.models import User

from settings.models import VotingSystem


# Create your models here.
class Vote(models.Model):
	system = models.ForeignKey(VotingSystem)

	name = models.CharField(max_length = 64)
	machine_name = models.SlugField(max_length = 64)

	creator = models.ForeignKey(User)

	min_votes = models.IntegerField()
	max_votes = models.IntegerField()


class Option(models.Model):
	vote = models.ForeignKey(Vote)

	number = models.IntegerField()

	name = models.CharField(max_length = 64)
	description = models.TextField()

	picture_url = models.URLField()
	personal_link = models.URLField()

	count = models.IntegerField()

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

class ActiveVote(models.Model):
	vote = models.ForeignKey(Vote)

	user = models.ForeignKey(User)

class PassiveVote(models.Model):
	vote = models.ForeignKey(Vote)

	num_voters = models.IntegerField()
	num_eligible = models.IntegerField()

