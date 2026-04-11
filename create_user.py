import psycopg2

conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='AMP50100',
    database='postgres'
)
conn.autocommit = True
cur = conn.cursor()

# Créer le nouvel utilisateur
cur.execute("CREATE USER admin_school WITH PASSWORD 'ecole2026' CREATEDB CREATEROLE")

# Donner les droits sur la base
cur.execute("GRANT ALL PRIVILEGES ON DATABASE gestion_scolaire TO admin_school")

print("Utilisateur admin_school créé avec succès!")
print("Login: admin_school")
print("Mot de passe: ecole2026")