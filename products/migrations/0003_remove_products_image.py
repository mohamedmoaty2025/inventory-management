# Generated by Django 5.2 on 2025-05-14 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_products_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='products',
            name='image',
        ),
    ]
