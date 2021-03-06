# Generated by Django 3.2 on 2021-05-02 11:24

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('username', models.TextField(null=True, verbose_name='user name')),
                ('user_type', models.CharField(choices=[('ADMIN', 'Admin'), ('USER', 'User'), ('DEVICE', 'Device')], default='USER', max_length=255)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Circuit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='circuit name')),
                ('active', models.BooleanField(verbose_name='active')),
                ('health_check', models.DateTimeField(null=True, verbose_name='health check')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='circuits', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledOneTimeActivation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('timestamp', models.DateTimeField(verbose_name='timestamp')),
                ('circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='one_time_activations', to='smartgarden.circuit')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledActivation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(verbose_name='active')),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('time', models.TimeField(verbose_name='activation time')),
                ('circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='smartgarden.circuit')),
            ],
        ),
        migrations.CreateModel(
            name='Activation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='amount')),
                ('timestamp', models.DateTimeField(verbose_name='timestamp')),
                ('circuit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activations', to='smartgarden.circuit')),
            ],
        ),
    ]
