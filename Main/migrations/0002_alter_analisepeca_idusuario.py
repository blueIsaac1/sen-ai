<<<<<<< HEAD
# Generated by Django 5.1 on 2024-08-13 17:02

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analisepeca',
            name='IdUsuario',
            field=models.IntegerField(verbose_name=django.contrib.auth.models.User),
        ),
    ]
=======
# Generated by Django 5.1 on 2024-08-13 17:02

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analisepeca',
            name='IdUsuario',
            field=models.IntegerField(verbose_name=django.contrib.auth.models.User),
        ),
    ]
>>>>>>> 930e0c7 (Teste de primeiro git)
