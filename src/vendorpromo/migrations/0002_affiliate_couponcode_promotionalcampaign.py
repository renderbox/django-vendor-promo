# Generated by Django 3.2.19 on 2023-05-22 01:12

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0043_invoice_global_discount'),
        ('sites', '0002_alter_domain_unique'),
        ('vendorpromo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionalCampaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('campaign_id', models.CharField(blank=True, max_length=80, null=True, verbose_name='Campaign Identifier')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Campaign Name')),
                ('description', models.TextField(blank=True, default=None, help_text='Enter a description or objective for this campaign', null=True, verbose_name='Description')),
                ('start_date', models.DateTimeField(blank=True, help_text='The date when this promotion is valid from', null=True, verbose_name='Start Date')),
                ('end_date', models.DateTimeField(blank=True, help_text='The date when this promotion is no longer valid', null=True, verbose_name='End Date')),
                ('is_percent_off', models.BooleanField(default=False, help_text='Fixed Amount or Percent Off', verbose_name='Percent Off?')),
                ('max_redemptions', models.IntegerField(blank=True, help_text='The maximum redemptions for the whole promotion', null=True, verbose_name='Max Redemptions')),
                ('meta', models.JSONField(blank=True, default=dict, null=True, verbose_name='Meta')),
                ('applies_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vendor.offer')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'Promotional Campaign',
                'verbose_name_plural': 'Promotional Campaigns',
            },
        ),
        migrations.CreateModel(
            name='CouponCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('code', autoslug.fields.AutoSlugField(blank=True, null=True, unique_with=('promo__site',), verbose_name='Affiliate Code')),
                ('max_redemptions', models.IntegerField(blank=True, null=True, verbose_name='Max Redemptions')),
                ('end_date', models.DateTimeField(blank=True, help_text='When will the code be unavailable', null=True, verbose_name='End Date')),
                ('meta', models.JSONField(blank=True, default=dict, null=True)),
                ('promo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon', to='vendorpromo.promotionalcampaign')),
            ],
            options={
                'verbose_name': 'Promo Code',
                'verbose_name_plural': 'Promo Codes',
            },
        ),
        migrations.CreateModel(
            name='Affiliate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(blank=True, null=True, unique_with=('customer_profile__site',), verbose_name='Affiliate Code')),
                ('contact_name', models.CharField(blank=True, max_length=120, null=True, verbose_name='Contact Name')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('company', models.CharField(blank=True, max_length=120, null=True, verbose_name='Company')),
                ('customer_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vendor.customerprofile', verbose_name='Customer Profile')),
                ('promo', models.ManyToManyField(blank=True, to='vendorpromo.PromotionalCampaign', verbose_name='Promotion Campaign')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.site', verbose_name='Site')),
            ],
            options={
                'verbose_name': 'Affiliate',
                'verbose_name_plural': 'Affiliates',
            },
        ),
    ]
