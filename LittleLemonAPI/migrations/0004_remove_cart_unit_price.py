# Generated by Django 4.2 on 2023-04-30 17:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0003_remove_cart_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='unit_price',
        ),
    ]
