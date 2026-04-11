#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentification.models import User

if User.objects.filter(role=User.Role.SUPERADMIN).exists():
    print("Erreur: Un super administrateur existe deja!")
    sys.exit(1)

user = User.objects.create_superuser(
    username='admin',
    email='admin@ecole.com',
    password='admin2026',
    first_name='Super',
    last_name='Admin'
)
user.role = User.Role.SUPERADMIN
user.is_superuser = True
user.is_staff = True
user.save()

print("==================================================")
print("SUPER ADMINISTRATEUR CREE AVEC SUCCES!")
print("==================================================")
print("Username: admin")
print("Mot de passe: admin2026")
print("==================================================")
