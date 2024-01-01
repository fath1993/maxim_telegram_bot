# Generated by Django 4.2.7 on 2023-11-26 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link_text_id', models.CharField(max_length=255, verbose_name='link text id')),
                ('links', models.TextField(verbose_name='links')),
            ],
            options={
                'verbose_name': 'لینک تکست',
                'verbose_name_plural': 'لینک تکست',
            },
        ),
    ]
