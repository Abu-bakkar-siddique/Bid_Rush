# Generated by Django 5.0.6 on 2024-09-08 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pictures',
            name='picture',
            field=models.ImageField(blank=True, default='images/placeholder.jpeg', upload_to='auctions/images'),
        ),
    ]
