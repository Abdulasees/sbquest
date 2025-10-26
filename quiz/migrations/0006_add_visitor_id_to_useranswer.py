from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_alter_useranswer_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useranswer',
            name='visitor_id',
            field=models.CharField(max_length=64, db_index=True, default='anon'),  # temporary default to avoid NOT NULL issue
            preserve_default=False,
        ),
    ]
