# Generated by Django 3.2.2 on 2022-12-07 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miningapp', '0006_auto_20221206_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='location',
            field=models.CharField(blank=True, max_length=160, null=True),
        ),
    ]
