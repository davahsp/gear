# Generated migration to revert Supplier ID back to AutoField

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_supplier_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='id',
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
            ),
        ),
    ]
