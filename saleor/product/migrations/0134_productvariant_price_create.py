# Generated by Django 3.1.2 on 2021-10-07 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0133_remove_productvariant_price_create'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='price_create',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
