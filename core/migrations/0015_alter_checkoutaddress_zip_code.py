# Generated by Django 3.2 on 2021-06-28 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_checkoutaddress_zip_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutaddress',
            name='zip_code',
            field=models.IntegerField(default=0, max_length=6, null=True, verbose_name='zipcode'),
        ),
    ]