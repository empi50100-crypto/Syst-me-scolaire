from django.contrib import admin
from .models import Bulletin


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ['eleve', 'periode', 'moyenne_generale', 'rang', 'date_generation']
    list_filter = ['periode', 'date_generation']
