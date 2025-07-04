# Generated by Django 5.2.1 on 2025-06-21 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_stockrecord_cost_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='dimensions',
            field=models.CharField(blank=True, help_text='e.g., 53.3 x 40.6 x 6.4 cm', max_length=255, null=True, verbose_name='Dimensions'),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Manufacturer'),
        ),
        migrations.AddField(
            model_name='product',
            name='weight_grams',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Weight (grams)'),
        ),
        migrations.AlterField(
            model_name='product',
            name='upc',
            field=models.CharField(blank=True, help_text='Universal Product Code (or ASIN, ISBN, etc.)', max_length=255, null=True, verbose_name='UPC / ASIN'),
        ),
        migrations.AlterModelTable(
            name='product',
            table='product',
        ),
        migrations.AlterModelTable(
            name='productattribute',
            table='product_attribute',
        ),
        migrations.AlterModelTable(
            name='productattributevalue',
            table='product_attribute_value',
        ),
        migrations.AlterModelTable(
            name='producttype',
            table='product_type',
        ),
        migrations.AlterModelTable(
            name='stockrecord',
            table='stock_record',
        ),
    ]
