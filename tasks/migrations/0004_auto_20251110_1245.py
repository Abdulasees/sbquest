from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_delete_usertask'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitortask',
            name='user',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
                null=True,   # temporarily allow null to avoid errors
                blank=True,
            ),
        ),
    ]
