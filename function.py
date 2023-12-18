import sqlite3
from datetime import datetime


# Fonction qui donne date plus heure sans les millisecondes
def now():
    return datetime.now().isoformat(' ', 'seconds')


# Fonction pour se connecter à la base de données
def connect_db():
    return sqlite3.connect('hackathon_bdd.sqlite')


# Fonction pour pour récupérer des données dans la base de données
def recup_bdd(query: str, values=None, doOne: bool = False):
    connection = connect_db()
    cursor = connection.cursor()
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)

    if doOne:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()

    connection.close()
    return result

# Fonction pour faire une action (INSERT, UPDATE, DELETE) dans la base de données
def action_bdd(query: str, values):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute(query, values)
    connection.commit()
    connection.close()
