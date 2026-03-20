from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flujopdf', '0003_alter_job_id_alter_page_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
