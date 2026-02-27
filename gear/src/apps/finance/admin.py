from django.contrib import admin
from .models import FinanceEntry, EntryCategory

admin.site.register([FinanceEntry, EntryCategory])
