# Generated by Django 3.2.19 on 2023-05-24 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0043_invoice_global_discount'),
        ('sites', '0002_alter_domain_unique'),
        ('vendorpromo', '0002_affiliate_couponcode_promotionalcampaign'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='couponcode',
            options={'verbose_name': 'Coupon Code', 'verbose_name_plural': 'Coupon Codes'},
        ),
        migrations.AddField(
            model_name='couponcode',
            name='invoice',
            field=models.ManyToManyField(blank=True, related_name='coupon_code', to='vendor.Invoice'),
        ),
        migrations.AlterField(
            model_name='couponcode',
            name='promo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_code', to='vendorpromo.promotionalcampaign'),
        ),
        migrations.AlterField(
            model_name='promotionalcampaign',
            name='applies_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promo_campaign', to='vendor.offer'),
        ),
        migrations.AlterField(
            model_name='promotionalcampaign',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promo_campaign', to='sites.site', verbose_name='Site'),
        ),
    ]
