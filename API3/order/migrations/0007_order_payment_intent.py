# Generated by Django 5.1.6 on 2025-02-14 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_remove_order_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_intent',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
