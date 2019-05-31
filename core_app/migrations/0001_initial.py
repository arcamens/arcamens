# Generated by Django 2.1.7 on 2019-05-31 01:19

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('card_app', '0001_initial'),
        ('slock', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clipboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cards', models.ManyToManyField(related_name='card_clipboard_users', to='card_app.Card')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('html', models.TextField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(default=datetime.datetime.now, null=True)),
                ('end', models.DateField(default=datetime.datetime.now, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=70, null=True)),
                ('token', models.CharField(max_length=256)),
                ('invite_url', models.CharField(max_length=256)),
                ('status', models.CharField(choices=[('0', 'Staff'), ('1', 'Worker'), ('2', 'Contributor')], default='2', max_length=6)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('0', 'Staff'), ('1', 'Worker'), ('2', 'Contributor')], default='0', max_length=6)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('indexer', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='NodeFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern', models.CharField(blank=True, default='', help_text='/projectname/', max_length=255)),
                ('status', models.BooleanField(blank=True, default=False, help_text='Filter On/Off.')),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.CharField(max_length=100, verbose_name='Description')),
                ('expiration', models.DateTimeField(blank=True, null=True)),
                ('public', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(default='...', max_length=256, null=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='core_app.Organization')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('basicuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='slock.BasicUser')),
                ('onesignal_id', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(help_text='Example: Software Enginer.', max_length=256, null=True, verbose_name='Bio')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='')),
                ('enabled', models.BooleanField(default=False)),
                ('c_storage', models.IntegerField(default=0)),
                ('c_download', models.IntegerField(default=0)),
                ('max_users', models.IntegerField(default=3)),
                ('paid', models.BooleanField(default=False)),
                ('expiration', models.DateField(null=True)),
                ('default', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core_app.Organization')),
                ('organizations', models.ManyToManyField(related_name='users', through='core_app.Membership', to='core_app.Organization')),
            ],
            options={
                'abstract': False,
            },
            bases=('slock.basicuser', models.Model),
        ),
        migrations.CreateModel(
            name='UserFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern', models.CharField(blank=True, default='', help_text='Example: oliveira@arcamens.com', max_length=255)),
                ('organization', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core_app.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.User')),
            ],
        ),
        migrations.CreateModel(
            name='UserTagship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('tag', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_tagship', to='core_app.Tag')),
                ('tagger', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_taggership', to='core_app.User')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_tagship', to='core_app.User')),
            ],
        ),
        migrations.CreateModel(
            name='EBindTagUser',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='ECreateTag',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='EDeleteTag',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
                ('tag_name', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='EDisabledAccount',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
                ('reason', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='EInviteUser',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='EJoinOrganization',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='ERemoveOrganizationUser',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
                ('reason', models.CharField(blank=True, default='', max_length=256)),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='EShout',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
                ('msg', models.CharField(help_text='No pain no gain!', max_length=256, verbose_name='Msg')),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event', models.Model),
        ),
        migrations.CreateModel(
            name='EUnbindTagUser',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.CreateModel(
            name='EUpdateOrganization',
            fields=[
                ('event_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core_app.Event')),
            ],
            options={
                'abstract': False,
            },
            bases=('core_app.event',),
        ),
        migrations.AddField(
            model_name='user',
            name='tags',
            field=models.ManyToManyField(related_name='users', through='core_app.UserTagship', to='core_app.Tag'),
        ),
        migrations.AddField(
            model_name='organization',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owned_organizations', to='core_app.User'),
        ),
        migrations.AddField(
            model_name='nodefilter',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.Organization'),
        ),
        migrations.AddField(
            model_name='nodefilter',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.User'),
        ),
        migrations.AddField(
            model_name='membership',
            name='inviter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_membership', to='core_app.User'),
        ),
        migrations.AddField(
            model_name='membership',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core_app.Organization'),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_membership', to='core_app.User'),
        ),
        migrations.AddField(
            model_name='invite',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='core_app.Organization'),
        ),
        migrations.AddField(
            model_name='invite',
            name='peer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_invites', to='core_app.User'),
        ),
        migrations.AddField(
            model_name='invite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='core_app.User'),
        ),
        migrations.AddField(
            model_name='eventfilter',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.Organization'),
        ),
        migrations.AddField(
            model_name='eventfilter',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.User'),
        ),
        migrations.AddField(
            model_name='event',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core_app.Organization'),
        ),
        migrations.AddField(
            model_name='event',
            name='signers',
            field=models.ManyToManyField(related_name='seen_events', to='core_app.User'),
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core_app.User'),
        ),
        migrations.AddField(
            model_name='event',
            name='users',
            field=models.ManyToManyField(related_name='events', to='core_app.User'),
        ),
    ]
