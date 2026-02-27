from django.db import transaction
from .models import *

from decimal import Decimal
from dateutil import parser
from datetime import date

class InventoryService:

    '''
    
    `meta` should be in form of dictionary containing information about supplier name
    delivery / receival date, and most importantly total price in Rp
    e.g. as below.
    {
        'supplier_name': 'PT JAYA MAKMUR SENTOSA',
        'delivery_date': '25-12-2025',
        'total_price': 10_000_000,
    }

    all the entries are required except for date. current date will be assumed if not provided.

    `data` should be in form of dictionary that maps the type of salt into quantity in tonnes
    e.g. as below.
    {
        'HARSH': 10,
        'SOFT': 20,
    }

    if one of the type of salt is not listed, the quantity of order is assumed zero.
    if the dictionary is empty, it will throw a ValueError
    
    '''
    @staticmethod
    @transaction.atomic
    def receive_supply(meta: dict, data: dict):

        keys = meta.keys()

        if 'supplier_name' not in keys or 'total_price' not in keys:
            raise ValueError('Insufficient data for receiving supply')
        
        if not data:
            raise ValueError('Supply data cannot be empty')
        
        supplier_name = meta['supplier_name']

        supplier, _ = Supplier.objects.get_or_create(name=supplier_name)

        delivery_date = parser.parse(meta['delivery_date']).date() \
            if 'delivery_date' in keys else date.today()
        
        total_price = int(meta['total_price'])

        purchase = Purchase.objects.create(
            supplier=supplier,
            total_price=total_price,
            delivery_date=delivery_date,
        )

        for salt_type, qty in data.items():
            try:
                raw_salt = RawSalt.objects.get(salt_type=salt_type)
            except RawSalt.DoesNotExist:
                raise ValueError(f"RawSalt type '{salt_type}' not found")
            
            raw_salt.in_stock_tonnes += qty

            raw_salt.save()

            PurchaseItem.objects.create(
                raw_salt=raw_salt,
                quantity_tonnes=qty,
                purchase=purchase,
            )

    '''
    
    `data` should be a dictionary with entries as below.

    {
        'HARSH-200': 100,
        'SOFT-300': 200,
        'SOFT-1000': 30,
    }

    the keys of `data` should in format XXXX-N with XXXX as salt_type and 
    N as the size of the pack in gram(s).

    the values of `data` is delta quantity, which means the amount of produced packs
    for a variant within a day.

    this function will yield a ValueError if the data is empty.
    
    '''
    @staticmethod
    @transaction.atomic
    def daily_pack(data: dict):

        if not data:
            raise ValueError('Daily packing data cannot be empty')
        
        daily_packing_obj = DailyPacking.objects.create()
        
        for variant, d_qty in data.items():

            # transforming variant data into PackedSalt object representation
            variant_data = str(variant).split('-')
            if len(variant_data) != 2:
                raise ValueError('Malformed variant data. One should be XXXX-N with XXXX ' + \
                                 'as salt_type and N as the size of the pack in gram(s)')
            
            salt_type = variant_data[0]
            size_grams = int(variant_data[1])

            try: 
                packed_salt = PackedSalt.objects.get(
                    salt_type=salt_type,
                    size_grams=size_grams,
                )
            except PackedSalt.DoesNotExist:
                raise ValueError(f"PackedSalt type '{salt_type}' with size {size_grams} gr(s) not found")
            
            packed_salt.in_stock_packs += int(d_qty)

            packed_salt.save()

            try:
                raw_salt = RawSalt.objects.get(
                    salt_type=salt_type
                )
            except RawSalt.DoesNotExist:
                raise ValueError(f"RawSalt type '{salt_type}' not found")
            
            # subtract used raw salts from the stock
            # use Decimal to avoid floating point problem
            raw_salt.in_stock_tonnes -= Decimal(size_grams) * Decimal(d_qty) * Decimal('1e-6')
            raw_salt.save()

            PackingItem.objects.create(
                daily_packing=daily_packing_obj,
                packed_salt=packed_salt,
                quantity_packs=d_qty,
            )