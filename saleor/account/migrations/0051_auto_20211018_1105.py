# Generated by Django 3.2.8 on 2021-10-18 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0050_auto_20211018_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='addresses',
        ),
        migrations.AddField(
            model_name='user',
            name='addresses',
            field=models.ManyToManyField(blank=True, null=True, related_name='user_addresses', to='account.Address'),
        ),
    ]
