from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_unique_requester_identity'),
    ]

    operations = [
        migrations.AddField(
            model_name='emergencyrequest',
            name='after_image',
            field=models.ImageField(blank=True, null=True, upload_to='emergency_requests/after/'),
        ),
        migrations.AddField(
            model_name='emergencyrequest',
            name='before_image',
            field=models.ImageField(blank=True, null=True, upload_to='emergency_requests/before/'),
        ),
    ]
