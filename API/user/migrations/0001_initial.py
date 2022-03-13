# Generated by Django 4.0.3 on 2022-03-13 04:40

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(max_length=50, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, default='', max_length=50, null=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('phone_number', models.CharField(blank=True, max_length=14, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid phone number.', regex='[0-9]{9,14}$')])),
                ('picture', models.ImageField(default='image/profile/profile.*', upload_to='image/profile/')),
                ('address', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('last_seen', models.DateTimeField(blank=True, null=True, verbose_name='Last Seen')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='email address')),
                ('key', models.PositiveIntegerField(blank=True, null=True, unique=True)),
                ('count', models.PositiveIntegerField(default=1)),
                ('created', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
    ]