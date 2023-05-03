# Generated by Django 3.1.11 on 2021-05-28 20:58

import autoslug.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vendor', '0022_offer_meta'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='last updated')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('description', models.TextField(blank=True, default=None, help_text='Enter a description for your Promo Code', null=True, verbose_name='Promo Description')),
                ('code', models.CharField(max_length=80, verbose_name='Code')),
                ('campaign_id', models.CharField(blank=True, max_length=80, null=True, verbose_name='Campaign Identifier')),
                ('campaign_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Campaign Name')),
                ('campaign_description', models.TextField(blank=True, null=True, verbose_name='Campaign Description')),
                ('meta', models.JSONField(blank=True, default=dict, null=True, verbose_name='Meta')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='code', unique_with=('offer__site__id',))),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promo', to='vendor.offer')),
            ],
            options={
                'verbose_name': 'Promo',
                'verbose_name_plural': 'Promos',
            },
        ),
    ]