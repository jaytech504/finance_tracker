# Generated by Django 4.2.16 on 2024-12-22 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fin_track', '0013_rename_budget_budget_total_budget_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='difference',
            field=models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=10),
        ),
    ]
