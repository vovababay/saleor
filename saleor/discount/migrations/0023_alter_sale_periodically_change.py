# Generated by Django 3.2.8 on 2021-11-09 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0022_auto_20211006_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='periodically_change',
            field=models.CharField(choices=[('true', 'true'), ('false', 'false')], default='false', max_length=5, verbose_name='Переодически изменять стоимость'),
        ),
    ]
