# Generated by Django 3.2 on 2021-06-28 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_checkoutaddress_zip_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutaddress',
            name='zip_code',
            field=models.CharField(default=0, max_length=10, null=True),
        ),
    ]
