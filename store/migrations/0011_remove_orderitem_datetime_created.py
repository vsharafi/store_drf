# Generated by Django 4.2.6 on 2024-06-12 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_remove_customer_user_customer_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='datetime_created',
        ),
    ]