# Generated by Django 3.2.2 on 2023-01-09 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miningapp', '0015_auto_20221226_0030'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastDeposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('name', models.CharField(max_length=150)),
                ('amount', models.PositiveSmallIntegerField()),
                ('currency', models.CharField(choices=[('USD', 'USD'), ('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'), ('Binance', 'Binance'), ('Ripple', 'Ripple'), ('Dogecoin', 'Dogecoin'), ('Litecoin', 'Litecoin'), ('Bitcoin cash', 'Bitcoin cash'), ('Dash', 'Dash'), ('USDT', 'USDT'), ('BUSD', 'BUSD'), ('Tron', 'Tron'), ('Solana', 'Solana'), ('Cardano', 'Cardano')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LastWithdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('name', models.CharField(max_length=150)),
                ('amount', models.PositiveSmallIntegerField()),
                ('currency', models.CharField(choices=[('USD', 'USD'), ('Bitcoin', 'Bitcoin'), ('Ethereum', 'Ethereum'), ('Binance', 'Binance'), ('Ripple', 'Ripple'), ('Dogecoin', 'Dogecoin'), ('Litecoin', 'Litecoin'), ('Bitcoin cash', 'Bitcoin cash'), ('Dash', 'Dash'), ('USDT', 'USDT'), ('BUSD', 'BUSD'), ('Tron', 'Tron'), ('Solana', 'Solana'), ('Cardano', 'Cardano')], max_length=50)),
            ],
        ),
    ]
