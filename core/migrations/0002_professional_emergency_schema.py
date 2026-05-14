import django.db.models.deletion
from django.db import migrations, models


DEFAULT_EMERGENCY_TYPES = {
    'medical': 'Medical',
    'fire': 'Fire',
    'police': 'Police',
}


def seed_types_and_copy_requests(apps, schema_editor):
    EmergencyType = apps.get_model('core', 'EmergencyType')
    EmergencyRequest = apps.get_model('core', 'EmergencyRequest')

    for name in DEFAULT_EMERGENCY_TYPES.values():
        EmergencyType.objects.get_or_create(name=name)

    for emergency_request in EmergencyRequest.objects.select_related('requester'):
        legacy_type = emergency_request.emergency_type or 'medical'
        type_name = DEFAULT_EMERGENCY_TYPES.get(
            legacy_type,
            legacy_type.replace('_', ' ').title() or 'Medical',
        )
        emergency_type, _ = EmergencyType.objects.get_or_create(name=type_name)

        emergency_request.emergency_type_fk = emergency_type
        if not emergency_request.location and emergency_request.requester_id:
            emergency_request.location = emergency_request.requester.location

        emergency_request.save(update_fields=['emergency_type_fk', 'location'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ResponseTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('contact', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='emergencyrequest',
            name='location',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emergencyrequest',
            name='emergency_type_fk',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='emergency_requests',
                to='core.emergencytype',
            ),
        ),
        migrations.RunPython(seed_types_and_copy_requests, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='emergencyrequest',
            name='emergency_type',
        ),
        migrations.RenameField(
            model_name='emergencyrequest',
            old_name='emergency_type_fk',
            new_name='emergency_type',
        ),
        migrations.AlterField(
            model_name='emergencyrequest',
            name='emergency_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='emergency_requests',
                to='core.emergencytype',
            ),
        ),
        migrations.AlterField(
            model_name='emergencyrequest',
            name='requester',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='emergency_requests',
                to='core.requester',
            ),
        ),
        migrations.AlterModelOptions(
            name='emergencyrequest',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='emergencyrequest',
            index=models.Index(fields=['status'], name='core_emerge_status_0e6a41_idx'),
        ),
        migrations.AddIndex(
            model_name='emergencyrequest',
            index=models.Index(fields=['created_at'], name='core_emerge_created_f56d8c_idx'),
        ),
        migrations.AlterModelOptions(
            name='requester',
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                (
                    'emergency_request',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='assignments',
                        to='core.emergencyrequest',
                    ),
                ),
                (
                    'response_team',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='assignments',
                        to='core.responseteam',
                    ),
                ),
            ],
            options={
                'ordering': ['-assigned_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='assignment',
            constraint=models.UniqueConstraint(
                fields=('emergency_request', 'response_team'),
                name='unique_request_team_assignment',
            ),
        ),
    ]
