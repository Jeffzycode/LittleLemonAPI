# Generated by Django 4.2 on 2023-04-30 21:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0008_alter_cart_unit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='menuitem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='LittleLemonAPI.menuitem'),
        ),
    ]