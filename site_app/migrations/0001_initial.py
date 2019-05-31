# Generated by Django 2.1.7 on 2019-05-31 01:19

from django.db import migrations, models
import django.db.models.deletion
import site_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordTicket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=256, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='password_tickets', to='core_app.User')),
            ],
        ),
        migrations.CreateModel(
            name='RegisterProcess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=256, null=True)),
                ('signup_url', models.CharField(max_length=256, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='register_process', to='core_app.User')),
            ],
            bases=(site_app.models.RegisterProcessMixin, models.Model),
        ),
    ]
