from collections import defaultdict

from django.db import migrations, models


def merge_duplicate_requesters(apps, schema_editor):
    Requester = apps.get_model('core', 'Requester')
    EmergencyRequest = apps.get_model('core', 'EmergencyRequest')

    identities = defaultdict(list)

    for requester in Requester.objects.order_by('id'):
        cleaned_name = requester.name.strip()
        cleaned_phone = requester.phone.strip()
        cleaned_location = requester.location.strip()

        if (
            requester.name != cleaned_name or
            requester.phone != cleaned_phone or
            requester.location != cleaned_location
        ):
            requester.name = cleaned_name
            requester.phone = cleaned_phone
            requester.location = cleaned_location
            requester.save(update_fields=['name', 'phone', 'location'])

        identities[(cleaned_name, cleaned_phone, cleaned_location)].append(requester.id)

    for requester_ids in identities.values():
        if len(requester_ids) < 2:
            continue

        canonical_id = requester_ids[0]
        duplicate_ids = requester_ids[1:]

        EmergencyRequest.objects.filter(requester_id__in=duplicate_ids).update(requester_id=canonical_id)
        Requester.objects.filter(id__in=duplicate_ids).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_professional_emergency_schema'),
    ]

    operations = [
        migrations.RunPython(merge_duplicate_requesters, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='requester',
            constraint=models.UniqueConstraint(
                fields=('name', 'phone', 'location'),
                name='unique_requester_identity',
            ),
        ),
    ]
