# Generated by Django 5.2 on 2025-05-14 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_categroy_products_category'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Categroy',
            new_name='Category',
        ),
    ]
