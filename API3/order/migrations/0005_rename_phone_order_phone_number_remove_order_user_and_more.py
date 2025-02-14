# Generated by Django 5.1.6 on 2025-02-14 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_remove_order_payment_method'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='phone',
            new_name='phone_number',
        ),
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(default='Unknow', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='postcode',
            field=models.CharField(default='Unknow', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='user_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
