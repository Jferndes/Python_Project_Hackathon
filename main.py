from flask import Flask, render_template, Response , request
import csv
import io
import sqlite3
from datetime import datetime

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

 
@app.route("/ajouter_contact",  methods=['POST', 'GET'])
def ajouter_contact():
    if request.method == 'POST':
        #Récup info form
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        tel = request.form['tel']
        date_naissance = request.form['dob']
        photo = request.form['photo']

        print(nom, prenom, email, tel, date_naissance, photo)
        # Connexion à la base de données (cela créera la base de données si elle n'existe pas encore)
        connection = connect_db()
        cursor = connection.cursor()

        cursor.execute('''
                INSERT INTO Contact (nom, prenom, e_mail, tel, date_naissance, photo_profil, created_date, updated_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nom, prenom, email, tel, date_naissance, photo, datetime.now(), datetime.now()))

        connection.commit()
        connection.close()

    return render_template('ajouter.html')

 
# Route pour l'export CSV
@app.route('/export_csv')
def export_csv():
    # Connexion à la base de données
    connection = connect_db()
    cursor = connection.cursor()

    # Exemple pour récupérer les données de la table Contact
    cursor.execute("SELECT * FROM Contact")
    contacts = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    connection.close()

    # Générer le contenu CSV
    csv_content = generate_csv_content(contacts)

    # Retourner le contenu CSV en tant que fichier téléchargeable
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=export.csv"}
    )

def generate_csv_content(data):
    output = io.StringIO()
    writer = csv.writer(output)

    # Ajouter les en-têtes CSV si nécessaire
    # writer.writerow(["Colonne1", "Colonne2", ...])

    # Ajouter les données CSV
    for row in data:
        writer.writerow(row)

    return output.getvalue()


@app.get("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
