from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0004_link_existing_messages'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='is_groupe',
            field=models.BooleanField(default=False, verbose_name='Est un groupe'),
        ),
        migrations.AddField(
            model_name='conversation',
            name='nom',
            field=models.CharField(blank=True, max_length=100, verbose_name='Nom du groupe'),
        ),
    ]
