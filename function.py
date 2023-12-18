import sqlite3
from datetime import datetime
import flask_bcrypt


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


def valid_login(password_hash, password_clear):
    return flask_bcrypt.check_password_hash(pw_hash=password_hash, password=password_clear)


def is_valid_date_of_birth(date_str):
    try:
        date_of_birth = datetime.strptime(date_str, "%Y-%m-%d").date()
        current_date = datetime.now().date()

        # Vérifier que la date de naissance est antérieure à la date actuelle
        if date_of_birth > current_date:
            return False
        else:
            return True
    except ValueError:
        return False