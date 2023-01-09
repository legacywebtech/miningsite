# Generated by Django 3.2.2 on 2023-01-09 14:05

import cloudinary_storage.storage
import cloudinary_storage.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miningapp', '0016_lastdeposit_lastwithdraw'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyinfo',
            name='facebook_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='instagram_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='linked_in',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='twitter_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='video',
            field=models.FileField(blank=True, null=True, storage=cloudinary_storage.storage.VideoMediaCloudinaryStorage(), upload_to='videos', validators=[cloudinary_storage.validators.validate_video]),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='whatsapp_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='youtube_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companyinfo',
            name='youtube_video',
            field=models.CharField(blank=True, help_text='Youtube embedded video code', max_length=500, null=True),
        ),
    ]
