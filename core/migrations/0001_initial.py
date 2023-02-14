# Generated by Django 3.0.6 on 2021-05-06 16:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='relevance_metrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=400)),
                ('metrics', models.FloatField()),
                ('run_date', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='templateupload',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('filepath', models.FileField(upload_to='uploads/')),
                ('purpose', models.CharField(blank=True, choices=[('addsubject', 'Add Subject'), ('customsubjectsearch', 'Custom Subject Search')], max_length=400)),
                ('timestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='searchsubject',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('search_subject', models.CharField(blank=True, max_length=400, unique=True)),
                ('stakeholder', models.EmailField(blank=True, max_length=254, null=True)),
            ],
            options={
                'unique_together': {('search_subject', 'stakeholder')},
            },
        ),
        migrations.CreateModel(
            name='news',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('search_subject', models.CharField(blank=True, max_length=400)),
                ('newsdate', models.CharField(blank=True, max_length=400, null=True)),
                ('source', models.CharField(blank=True, max_length=4000, null=True)),
                ('url', models.CharField(blank=True, max_length=4000, unique=True)),
                ('title', models.CharField(blank=True, max_length=4000, null=True)),
                ('summary', models.CharField(blank=True, max_length=4000, null=True)),
                ('sentiment', models.CharField(blank=True, max_length=10, null=True)),
                ('annotation', models.CharField(blank=True, max_length=10, null=True)),
                ('cosine_similarity', models.FloatField(blank=True, null=True)),
            ],
            options={
                'unique_together': {('search_subject', 'newsdate', 'source', 'url', 'title')},
            },
        ),
        migrations.CreateModel(
            name='filtered_news',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('search_subject', models.CharField(blank=True, max_length=400)),
                ('newsdate', models.CharField(blank=True, max_length=400, null=True)),
                ('source', models.CharField(blank=True, max_length=4000, null=True)),
                ('url', models.CharField(blank=True, max_length=4000, unique=True)),
                ('title', models.CharField(blank=True, max_length=4000, null=True)),
                ('summary', models.CharField(blank=True, max_length=4000, null=True)),
                ('sentiment', models.CharField(blank=True, max_length=10, null=True)),
                ('annotation', models.CharField(blank=True, max_length=10, null=True)),
                ('cosine_similarity', models.FloatField(blank=True, null=True)),
            ],
            options={
                'unique_together': {('search_subject', 'newsdate', 'source', 'url', 'title')},
            },
        ),
    ]