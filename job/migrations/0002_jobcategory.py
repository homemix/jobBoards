# Generated by Django 5.1.1 on 2024-10-08 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remotive_id', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
            ],
        ),
    ]
