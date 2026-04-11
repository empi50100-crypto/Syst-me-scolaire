# Generated migration to add matiere field to Utilisateur model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('authentification', '0001_initial'),
        ('enseignement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='matiere',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='professeurs',
                to='enseignement.matiere',
                verbose_name='Matière enseignée'
            ),
        ),
    ]
