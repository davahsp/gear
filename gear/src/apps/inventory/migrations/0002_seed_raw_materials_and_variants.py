"""
Data migration: seed initial RawMaterial and ProductVariant records.

RawMaterials  : Garam Krosok (kg), Iodium (kg), Plastik (pcs), Karung (pcs)
ProductVariants:
  SOFT × [100, 200, 250, 500] g + 50 000 g (50 kg)
  HARD × [100, 150, 200, 250, 400, 500, 800, 1000] g + 50 000 g (50 kg)
"""

from django.db import migrations

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

RAW_MATERIALS = [
    {'name': 'Garam Krosok', 'unit': 'kg',  'qty_in_stock': 0},
    {'name': 'Iodium',       'unit': 'kg',  'qty_in_stock': 0},
    {'name': 'Plastik',      'unit': 'pcs', 'qty_in_stock': 0},
    {'name': 'Karung',       'unit': 'pcs', 'qty_in_stock': 0},
]

# Per-type variant sizes (in grams; 50 000 = 50 kg karung variant)
VARIANTS = [
    ('SOFT', [100, 200, 250, 500, 50_000]),
    ('HARD', [100, 150, 200, 250, 400, 500, 800, 1000, 50_000]),
]


# ---------------------------------------------------------------------------
# Forward
# ---------------------------------------------------------------------------

def seed_data(apps, schema_editor):
    RawMaterial    = apps.get_model('inventory', 'RawMaterial')
    ProductVariant = apps.get_model('inventory', 'ProductVariant')

    for rm in RAW_MATERIALS:
        RawMaterial.objects.get_or_create(
            name=rm['name'],
            defaults={'unit': rm['unit'], 'qty_in_stock': rm['qty_in_stock']},
        )

    for product_type, sizes in VARIANTS:
        for size in sizes:
            ProductVariant.objects.get_or_create(
                product_type=product_type,
                size_grams=size,
                defaults={'qty_in_stock': 0},
            )


# ---------------------------------------------------------------------------
# Reverse  (removes only the seed records if they still have stock 0)
# ---------------------------------------------------------------------------

def unseed_data(apps, schema_editor):
    RawMaterial    = apps.get_model('inventory', 'RawMaterial')
    ProductVariant = apps.get_model('inventory', 'ProductVariant')

    for rm in RAW_MATERIALS:
        RawMaterial.objects.filter(name=rm['name'], qty_in_stock=0).delete()

    for product_type, sizes in VARIANTS:
        for size in sizes:
            ProductVariant.objects.filter(
                product_type=product_type, size_grams=size, qty_in_stock=0,
            ).delete()


# ---------------------------------------------------------------------------
# Migration class
# ---------------------------------------------------------------------------

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_code=unseed_data),
    ]
