# Migration to change Supplier ID from AutoField to CharField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_supplier_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='id',
            field=models.CharField(editable=False, max_length=10, primary_key=True, serialize=False),
        ),
    ]
