from django.db import models
from django.core.validators import MinValueValidator
from datetime import date
from django.conf import settings

class EntryType(models.TextChoices):

    INCOME = 'INCOME', 'Income'
    EXPENSE = 'EXPENSE', 'Expense'

class EntryCategory(models.Model):

    name = models.CharField(max_length=31)
    type = models.CharField(max_length=7, choices=EntryType.choices)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['name', 'type'],
                name='uniqueness of name within the same entry type'
            ),
        ]

    def __str__(self):
        return f'[{self.type}] {self.name}'

class FinanceEntry(models.Model):

    nominal = models.IntegerField(validators=[MinValueValidator(1)])
    category = models.ForeignKey(to='EntryCategory',
                                 on_delete=models.PROTECT,
                                 related_name='entries')

    description = models.TextField(null=True)
    transaction_date = models.DateField(default=date.today)

    who_inputs = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='entry_inputs')

