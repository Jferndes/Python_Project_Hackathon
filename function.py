import sqlite3

# Fonction pour se connecter à la base de données
def connect_db():
    return sqlite3.connect('hackathon_bdd.sqlite')

# Fonction pour pour récupérer des données dans la base de données
def recup_bdd(query: str, doOne: bool = False):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute(query)

    if doOne:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()

    connection.close()
    return result

# Fonction pour faire une action (INSERT, UPDATE, DELETE) dans la base de données
def action_bdd(query: str):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()
