# Generated by Django 5.1.6 on 2025-02-14 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auctionlisting_is_active_alter_pictures_picture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auctionlisting',
            old_name='categery',
            new_name='category',
        ),
    ]
