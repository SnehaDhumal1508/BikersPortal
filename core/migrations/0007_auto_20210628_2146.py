# Generated by Django 3.2 on 2021-06-28 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_checkoutaddress_zip_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutaddress',
            name='apartment_address',
            field=models.CharField(default=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='checkoutaddress',
            name='street_address',
            field=models.CharField(default=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='checkoutaddress',
            name='zip_code',
            field=models.CharField(default=True, max_length=15),
        ),
    ]
