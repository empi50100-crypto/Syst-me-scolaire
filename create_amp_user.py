import psycopg2

conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='AMP50100',
    database='postgres'
)
conn.autocommit = True
cur = conn.cursor()

try:
    cur.execute("CREATE USER AMP WITH PASSWORD 'AMP50100' CREATEDB CREATEROLE")
    print("Utilisateur AMP créé!")
except:
    print("L'utilisateur AMP existe déjà")

# Donner les droits sur la base
cur.execute("GRANT ALL PRIVILEGES ON DATABASE gestion_scolaire TO AMP")
print("Droits accordés!")

conn.close()
print("Configuration terminée!")
print("Login: AMP")
print("Mot de passe: AMP50100")