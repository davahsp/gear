from django.contrib import admin
from .models import *

admin.site.register([Purchase, 
                     PurchaseItem, 
                     Supplier, 
                     RawMaterial, 
                     DailyProduction, 
                     DailyProductionItem, 
                     DailyProductionRawItem,
                     ProductVariant,
                     ])
