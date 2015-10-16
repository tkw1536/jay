from django.db import models



# Create your models here.
class PrimitiveFilter(models.Model):
	EQUALS = 'EQ'
	CONTAINS = 'IN'
	REGEX = 'RE'
	GREATER = 'GT'
	SMALLER = 'LT'
	FALSE = 'FL'
	TRUE = 'TR'

	OPERATION_CHOICES = (
		(EQUALS, 'Equals'),
		(CONTAINS, 'Contains'),
		(REGEX, 'Regular Expression'),
		(GREATER, 'Greater than'),
		(SMALLER, 'Less than'),
		(FALSE, 'False'),
		(TRUE, 'True')
	)

	field = models.CharField(max_length = 64)
	operation = models.CharField(max_length = 2, choices = OPERATION_CHOICES)
	value = models.CharField(max_length = 64)

class ComplexFilter(models.Model):
	AND = 'AND'
	OR = 'OR'
	XOR = 'XOR'
	NAND = 'NAND'
	NONE = 'NONE'

	L_OPERATION_CHOICES = (
		(AND, 'And'),
		(OR, 'Or'),
		(XOR, 'Exclusive Or'),
		(NAND, 'Not And'),
		(NONE, 'No operation')
	)

	operation = models.CharField(max_length = 4, choices = L_OPERATION_CHOICES)

	# This is a simple filter if the operation is none. Otherwise left
	# and right are used to link to more logic filters
	simple_filter = models.ForeignKey(PrimitiveFilter, null=True)

	# This is used unless the operation is none, and the primitve filter is set
	left = models.ForeignKey('self', related_name='parent_left', null=True)
	right = models.ForeignKey('self', related_name='parent_right', null=True)

