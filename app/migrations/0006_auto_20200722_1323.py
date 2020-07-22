# Generated by Django 2.2.14 on 2020-07-22 13:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_leavewordreplyzan_leavewordzan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(max_length=16, verbose_name='语言')),
            ],
            options={
                'verbose_name_plural': '分类',
            },
        ),
        migrations.AddField(
            model_name='topic',
            name='lang',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Category', verbose_name='分类'),
        ),
    ]
