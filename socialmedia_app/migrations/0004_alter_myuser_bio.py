# Generated by Django 5.1.3 on 2025-01-08 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia_app', '0003_post_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='bio',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
