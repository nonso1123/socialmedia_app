# Generated by Django 5.1.3 on 2024-12-24 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia_app', '0002_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_image',
            field=models.ImageField(blank=True, null=True, upload_to='post_image/'),
        ),
    ]
