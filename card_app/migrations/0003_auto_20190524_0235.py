# Generated by Django 2.1.7 on 2019-05-24 02:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core_app', '0002_auto_20190524_0235'),
        ('card_app', '0002_auto_20190524_0235'),
        ('post_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='parent_post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='card_forks', to='post_app.Post'),
        ),
        migrations.AddField(
            model_name='card',
            name='path',
            field=models.ManyToManyField(related_name='children', to='card_app.Card'),
        ),
        migrations.AddField(
            model_name='card',
            name='relations',
            field=models.ManyToManyField(related_name='related', to='card_app.Card'),
        ),
        migrations.AddField(
            model_name='card',
            name='tags',
            field=models.ManyToManyField(related_name='cards', through='card_app.CardTagship', to='core_app.Tag'),
        ),
        migrations.AddField(
            model_name='card',
            name='workers',
            field=models.ManyToManyField(related_name='tasks', through='card_app.CardTaskship', to='core_app.User'),
        ),
        migrations.AlterUniqueTogether(
            name='cardtaskship',
            unique_together={('card', 'worker')},
        ),
        migrations.AlterUniqueTogether(
            name='cardtagship',
            unique_together={('card', 'tag')},
        ),
        migrations.AlterUniqueTogether(
            name='cardsearch',
            unique_together={('user', 'organization')},
        ),
        migrations.AddField(
            model_name='cardpin',
            name='card',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='card_app.Card'),
        ),
        migrations.AddField(
            model_name='cardpin',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core_app.Organization'),
        ),
        migrations.AddField(
            model_name='cardpin',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core_app.User'),
        ),
        migrations.AlterUniqueTogether(
            name='cardfilter',
            unique_together={('user', 'organization', 'list')},
        ),
        migrations.AlterUniqueTogether(
            name='cardpin',
            unique_together={('user', 'organization', 'card')},
        ),
    ]
