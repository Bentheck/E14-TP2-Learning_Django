# Generated by Django 5.1 on 2024-08-19 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_alter_drug_name_alter_drug_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.DecimalField(decimal_places=2, default=1000.0, max_digits=10)),
            ],
        ),
    ]
