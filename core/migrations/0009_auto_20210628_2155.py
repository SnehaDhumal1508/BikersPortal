# Generated by Django 3.2 on 2021-06-28 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20210628_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutaddress',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='checkoutaddress',
            name='zip_code',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
