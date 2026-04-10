# CHECKLIST DE DÉPLOIEMENT SÉCURISÉ
## Système de Gestion Scolaire

---

## 🔴 AVANT LE DÉPLOIEMENT

### 1. Variables d'environnement
- [ ] Copier `.env.example` vers `.env`
- [ ] Générer une nouvelle `SECRET_KEY` (min 50 caractères)
- [ ] Mettre `DEBUG=False`
- [ ] Configurer `ALLOWED_HOSTS` avec votre domaine
- [ ] Configurer `CSRF_TRUSTED_ORIGINS`
- [ ] Configurer `CORS_ALLOWED_ORIGINS`

### 2. Base de données
- [ ] **Utiliser PostgreSQL** (plus sécurisé que SQLite)
- [ ] Configurer un utilisateur PostgreSQL avec privileges limités
- [ ] Activer SSL pour les connexions BDD
- [ ] Créer un backup avant migration

### 3. Certificat SSL
- [ ] Installer Let's Encrypt (gratuit)
- [ ] Configurer redirection HTTP → HTTPS
- [ ] Renouveler automatiquement le certificat

---

## 🟠 PENDANT LE DÉPLOIEMENT

### 4. Installation des dépendances
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

### 5. Collecte des fichiers statiques
```bash
python manage.py collectstatic --noinput
```

### 6. Configuration du serveur
- [ ] Utiliser Gunicorn ou uWSGI
- [ ] Configurer Nginx avec:
  - SSL/TLS (TLS 1.2 minimum)
  - Headers de sécurité
  - Compression gzip
  - Cache statique

### 7. Configuration firewall
```bash
# Ouvrir uniquement les ports nécessaires
# 80 (HTTP) - redirection HTTPS
# 443 (HTTPS)
# 22 (SSH) - accès restreint
```

---

## 🟡 APRÈS LE DÉPLOIEMENT

### 8. Sauvegardes automatiques
```bash
# Planifier sauvegarde quotidienne (Windows Task Scheduler)
schtasks /create /sc daily /tn "SchoolBackup" /tr "python scripts\backup.py" /st 02:00

# Ou avec cron (Linux)
# 0 2 * * * /usr/bin/python3 /path/to/scripts/backup.py
```

### 9. Vérifications de sécurité
- [ ] Tester connexion HTTPS
- [ ] Vérifier que `.env` n'est pas accessible
- [ ] Vérifier que `db.sqlite3` n'est pas accessible
- [ ] Tester rate limiting (5 tentatives → lockout)
- [ ] Vérifier headers de sécurité:
  ```
  Content-Security-Policy
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Strict-Transport-Security
  ```

### 10. Monitoring
- [ ] Configurer logs centralisés
- [ ] Configurer alertes email sur erreurs
- [ ] Monitorer espace disque (backups)
- [ ] Monitorer tentatives de connexion échouées

---

## 🟢 MAINTENANCE

### 11. Mises à jour régulières
```bash
# Hebdomadaire
pip install --upgrade -r requirements.txt

# Après chaque mise à jour Django
python manage.py check --deploy
```

### 12. Tests de sécurité
- [ ] Scanner OWASP ZAP (mensuel)
- [ ] Test de pénétration (annuel)
- [ ] Audit des logs de connexion
- [ ] Vérification intégrité sauvegardes

### 13. Politique de mots de passe
- [ ] Imposer longueur minimale 12 caractères
- [ ] Exiger majuscules, minuscules, chiffres, symboles
- [ ] Changer les mots de passe tous les 90 jours
- [ ] Activer 2FA pour Direction et Comptabilité

---

## 📋 CONFIGURATION NGINX RECOMMANDÉE

```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com;

    ssl_certificate /etc/letsencrypt/live/votre-domaine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-domaine.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /path/to/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📋 CONFIGURATION GUNICORN

```bash
# Unit file systemd (Linux)
gunicorn core.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --chdir /path/to/gestion_ecole
```

---

## 🔗 HÉBERGEMENTS RECOMMANDÉS

| Provider | Type | Prix | Sécurité |
|----------|------|------|----------|
| **OVH Cloud** | VPS | ~5€/mois | Bonne |
| **DigitalOcean** | VPS | ~6$/mois | Excellente |
| **AWS EC2** | Cloud | ~10$/mois | Très bonne |
| **Railway** | PaaS | Freemium | Bonne |
| **Render** | PaaS | Freemium | Bonne |

---

## 📞 INCIDENT DE SÉCURITÉ

1. **Isoler** le serveur (déconnecter d'Internet)
2. **Identifier** la faille
3. **Corriger** le problème
4. **Restaurer** depuis dernière sauvegarde propre
5. **Notifier** les autorités si fuite de données personnelles
6. **Documenter** l'incident

---

## ✅ CHECKLIST RAPIDE

- [ ] `.env` configuré avec DEBUG=False
- [ ] HTTPS activé avec certificat valide
- [ ] PostgreSQL configuré
- [ ] Sauvegardes automatisées
- [ ] Logs activés
- [ ] Firewall configuré
- [ ] Rate limiting vérifié
- [ ] Headers de sécurité vérifiés
