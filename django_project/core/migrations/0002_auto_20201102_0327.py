# Generated by Django 3.1.2 on 2020-11-02 03:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='watchers',
            field=models.ManyToManyField(through='core.Favorite', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favorite',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.section'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.subject'),
        ),
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('user', 'section')},
        ),
    ]