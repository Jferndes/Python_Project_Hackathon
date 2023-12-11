from flask import Flask, render_template
import sqlite3

app = Flask(__name__)
app.secret_key = 'test'

# Fonction pour se connecter à la base de données
def connect_db():
    return sqlite3.connect('hackathon.sqlite')

# Page d'accueil qui affiche les données des tables Contact et Groupe
@app.route("/liste_contacts")
def liste_contacts():
    # Connexion à la base de données
    connection = connect_db()
    cursor = connection.cursor()

    # Récupération des contacts
    cursor.execute("SELECT * FROM Contact")
    contacts = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    connection.close()

    return render_template('liste_contacts.html', contacts=contacts)

# Définir la route pour afficher la liste des groupes
@app.route("/liste_groupes")
def liste_groupes():
    # Connexion à la base de données
    connection = connect_db()
    cursor = connection.cursor()

    # Récupération des groupes
    cursor.execute("SELECT * FROM Groupe")
    groupes = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    connection.close()

    # Rendu du modèle avec les données récupérées
    return render_template('liste_groupes.html', groupes=groupes)

@app.get("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
