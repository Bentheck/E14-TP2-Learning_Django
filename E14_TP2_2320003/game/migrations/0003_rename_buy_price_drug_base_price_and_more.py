# Generated by Django 5.1 on 2024-08-19 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_drug_zone_drugavailability'),
    ]

    operations = [
        migrations.RenameField(
            model_name='drug',
            old_name='buy_price',
            new_name='base_price',
        ),
        migrations.RemoveField(
            model_name='drug',
            name='sell_price',
        ),
        migrations.RemoveField(
            model_name='zone',
            name='description',
        ),
        migrations.AddField(
            model_name='drug',
            name='stock',
            field=models.PositiveIntegerField(default=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='drug',
            name='zones',
            field=models.ManyToManyField(through='game.DrugAvailability', to='game.zone'),
        ),
        migrations.AlterField(
            model_name='drug',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='drugavailability',
            name='stock',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='zone',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
