import datetime

from django.utils import timezone

from django.db import models, transaction
from django.contrib.auth.models import User

from django.contrib import admin

from settings.models import VotingSystem
from filters.models import UserFilter

from users.ojub_auth import get_all

from jay.restricted import is_restricted_word

# Create your models here.
class Vote(models.Model):
	system = models.ForeignKey(VotingSystem)

	name = models.CharField(max_length = 64)
	machine_name = models.SlugField(max_length = 64)

	auto_open_options = models.BooleanField(default=False, null=False)

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
		return user.isAdminFor(self.system) and self.status.stage != Status.PUBLIC

	def canDelete(self, user):
		"""
			Check if a user can delete this vote.
		"""
		return user.isAdminFor(self.system) and self.status.stage == Status.INIT

	def canBeModified(self):
		"""
			Checks if this vote can still be modified.
		"""
		return self.status.stage == Status.INIT

	def update_eligibility(self, username, password):

		PassiveVote.objects.get_or_create(vote=self, defaults={'num_voters': 0, 'num_eligible': 0})

		if self.filter == None:
			raise Exception("Missing filter. ")

		# this will take really long
		everyone = get_all(username, password)

		if not everyone:
			raise Exception("Invalid password or something went wrong. ")


		check = self.filter.map_matches(everyone)
		c = 0

		for b in check:
			if b:
				c += 1

		# get or create the passive vote object
		(pv, _) = PassiveVote.objects.get_or_create(vote=self, defaults={'num_voters': 0, 'num_eligible': 0})

		# update the eligibility number
		pv.num_eligible = c

		# and save
		pv.save()


	# Touch yourself, we lack self-assurance
	def touch(self):
		status = self.status
		stage = self.status.stage
		now = timezone.now()

		if stage == Status.INIT:
			return

		if stage == Status.STAGED and status.open_time:
			if status.open_time <= now:
				self.status.stage = Status.OPEN

		if stage == Status.OPEN and status.close_time:
			if status.close_time <= now:
				self.status.stage = Status.CLOSE
				self.close()

		if stage == Status.CLOSE and status.public_time:
			if status.public_time <= now:
				self.status.stage = Status.PUBLIC

		self.status.save()



	"""

	Converts the ActiveVotes on this vote to a count on the PassiveVote of this Vote

	"""
	def close(self):
		try:
			pasv = self.passivevote
			voters = self.activevote_set

			pasv.num_voters = voters.count()
			pasv.save()

			voters.delete()

		except PassiveVote.DoesNotExist:
			pass

	@transaction.atomic
	def renumberOptions(self):
		"""
			Renumbers the options in this vote.
		"""

		# give all of them a sequential number.
		for i, v in enumerate(self.option_set.order_by("number")):
			v.number = i
			v.save()


	@transaction.atomic
	def deleteOption(self, option):
		"""
			Removes an option from this vote.
		"""

		# if the option is not in our options, something weird happened.
		if not option.id in self.option_set.values_list('id', flat=True):
			raise ValueError

		# remove the option
		option.delete()

		# get the count
		count = self.option_set.count()

		# adn check if min_votes or max_votes are too big.
		# then update accordingly.
		if self.min_votes > count:
			self.min_votes = count

		if self.max_votes > count:
			self.max_votes = count

		# and save of course
		self.save()

		# and renumber
		self.renumberOptions()

	@transaction.atomic
	def addOption(self):
		"""
			Adds a new option.
		"""

		# renumber the options to make sure we are in order
		self.renumberOptions()

		# find a number for the new option
		num = self.option_set.count()

		# create a new option
		opt = Option(vote=self, number = num, name = "Option #"+str(num + 1))

		# and save it
		opt.save()


	@transaction.atomic
	def moveDownOption(self, option):
		"""
			move an option down in the indexing.
		"""

		# if the option is not in our options, something weird happened.
		if not option.id in self.option_set.values_list('id', flat=True):
			raise ValueError

		# renumber options to make sure we are in a valid order
		self.renumberOptions()

		# if we are already at the bottom there is nothing to do.
		if option.number == 0:
			return

		# find the option right below our option
		below = self.option_set.filter(number=option.number - 1)[0]

		# switch our two number
		below.number = option.number
		option.number = option.number - 1

		# and save the options
		below.save()
		option.save()

	@transaction.atomic
	def moveUpOption(self, option):
		"""
			move an option up in the indexing.
		"""

		# if the option is not in our options, something weird happened.
		if not option.id in self.option_set.values_list('id', flat=True):
			raise ValueError

		# renumber options to make sure we are in a valid order
		self.renumberOptions()

		# if we are already at the top there is nothing to do.
		if option.number == self.option_set.count() - 1:
			return

		# find the option right above our option
		above = self.option_set.filter(number=option.number + 1)[0]

		# switch our two number
		above.number = option.number
		option.number = option.number + 1

		# and save the options
		above.save()
		option.save()



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
