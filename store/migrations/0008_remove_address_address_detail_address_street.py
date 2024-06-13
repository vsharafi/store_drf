# Generated by Django 4.2.6 on 2024-06-12 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_remove_category_datetime_created_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='address_detail',
        ),
        migrations.AddField(
            model_name='address',
            name='street',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
