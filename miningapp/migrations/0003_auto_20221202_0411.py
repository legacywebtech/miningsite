# Generated by Django 3.2.2 on 2022-12-02 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miningapp', '0002_investment_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='amount',
            new_name='balance',
        ),
        migrations.AddField(
            model_name='investment',
            name='approved_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='investment',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='investment',
            name='returns',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='investment',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='investment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('declined', 'Declined'), ('completed', 'Completed')], default='pending', max_length=60),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('completed', 'completed')], default='pending', max_length=30),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'), ('completed', 'completed')], default='deposit', max_length=30),
        ),
    ]
