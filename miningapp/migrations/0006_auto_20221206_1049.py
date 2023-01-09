# Generated by Django 3.2.2 on 2022-12-06 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('miningapp', '0005_alter_profile_downlines'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='downlines',
            field=models.ManyToManyField(blank=True, related_name='downlines', to=settings.AUTH_USER_MODEL, verbose_name='referred'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment_address',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment_method',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(max_length=5000)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
