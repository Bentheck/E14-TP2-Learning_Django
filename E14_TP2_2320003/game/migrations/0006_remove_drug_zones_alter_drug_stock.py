# Generated by Django 5.1 on 2024-08-19 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_remove_transaction_item_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drug',
            name='zones',
        ),
        migrations.AlterField(
            model_name='drug',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
    ]