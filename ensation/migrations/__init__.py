from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Matiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True, verbose_name='Nom de la matière')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Code')),
                ('coefficient', models.DecimalField(decimal_places=2, default=1, max_digits=3, verbose_name='Coefficient')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('est_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Matière',
                'verbose_name_plural': 'Matières',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Salle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, unique=True, verbose_name='Nom de la salle')),
                ('capacite', models.IntegerField(default=30, verbose_name='Capacité')),
                ('type_salle', models.CharField(choices=[('cours', 'Salle de cours'), ('bureau', 'Bureau'), ('laboratoire', 'Laboratoire'), ('sport', 'Salle de sport'), ('conference', 'Salle de conférence')], default='cours', max_length=20, verbose_name='Type de salle')),
                ('est_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'verbose_name': 'Salle',
                'verbose_name_plural': 'Salles',
                'ordering': ['nom'],
            },
        ),
    ]