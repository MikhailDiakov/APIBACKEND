# Generated by Django 5.1.6 on 2025-02-13 10:17

import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5)),
                ('price_after_discount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('price_per_item', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('image', models.URLField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='order.order')),
            ],
        ),
    ]
