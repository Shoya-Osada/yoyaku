# Generated by Django 3.1.14 on 2022-03-07 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='店舗')),
                ('address', models.CharField(blank=True, max_length=100, null=True, verbose_name='住所')),
                ('tel', models.CharField(blank=True, max_length=100, null=True, verbose_name='電話番号')),
                ('description', models.TextField(blank=True, default='', verbose_name='説明')),
                ('image', models.ImageField(blank=True, null=True, upload_to='images', verbose_name='イメージ画像')),
            ],
        ),
    ]
