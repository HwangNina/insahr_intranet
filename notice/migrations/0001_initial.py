# Generated by Django 3.1.2 on 2020-11-18 05:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('content', models.TextField()),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='employee.employee')),
            ],
            options={
                'db_table': 'notices',
            },
        ),
        migrations.CreateModel(
            name='NoticeAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='file/%Y/%m/%d')),
                ('notice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notice.notice')),
            ],
            options={
                'db_table': 'notice_attachments',
            },
        ),
    ]
