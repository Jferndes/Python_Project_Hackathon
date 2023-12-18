from flask import Flask, render_template, Response, request, redirect, url_for, flash
from function import *
from werkzeug.utils import secure_filename
import os
import csv
import io

app = Flask(__name__)
app.secret_key = 'test'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get("/")
def index():
    return render_template('index.html')

@app.route("/contacts")
def liste_contacts():
    # Récupération de tout les contacts
    query = "SELECT * FROM Contact"
    contacts = recup_bdd(query)

    # Rendu du modèle avec les données récupérées
    return render_template('contactList.html', contacts=contacts)


@app.route("/contacts/new",  methods=['POST', 'GET'])
def ajouter_contact():
    if request.method == 'POST':
        # Récupération des informations du formulaire
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        tel = request.form['tel']
        date_naissance = request.form['dob']
        photo = request.form['photo']

        # Requête dans la base de données
        query = '''
            INSERT INTO Contact (nom, prenom, e_mail, tel, date_naissance, photo_profil, created_date, updated_date)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')
        '''.format(nom, prenom, email, tel, date_naissance, photo, now(), now())
        action_bdd(query)

        # Redirection vers la liste des contacts avec message de confirmation
        flash("Le contact a été créé", "success")
        return redirect(url_for('liste_contacts'))

    elif request.method == 'GET':
        return render_template('contactNew.html')


@app.route("/contacts/<int:contactId>/edit", methods=['GET', 'POST'])
def edit_contact(contactId):
    # Récupération du contact
    query = "SELECT * FROM Contact WHERE id_contact = {}".format(contactId)
    contact = recup_bdd(query, True)

    if request.method == 'GET':
        if contact:
            return render_template('contactEdit.html', contact=contact)

    elif request.method == 'POST':
        # Vérification de modification des valeurs
        i = 1
        doUpdate = False
        for key in request.form:
            if request.form[key] != contact[i]:
                doUpdate = True
            i += 1

        if doUpdate:
            # Récupération des informations du formulaire
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            tel = request.form['tel']
            date_naissance = request.form['dob']
            photo = request.form['photo']

            # Requête dans la base de données
            query = '''
                        UPDATE Contact
                        SET nom='{}', prenom='{}', e_mail='{}', tel='{}', date_naissance='{}', photo_profil='{}', updated_date='{}'
                        WHERE id_contact='{}'
                    '''.format(nom, prenom, email, tel, date_naissance, photo, now(), contactId)
            action_bdd(query)

            # Message de confirmation
            flash("Le contact a été modifié", "warning")

        # Redirection vers la liste des contacts
        return redirect(url_for('liste_contacts'))


@app.route("/contacts/<int:contactId>/delete", methods=['GET', 'POST'])
def delete_contact(contactId):
    if request.method == 'GET':
        # Récupération du contact
        query = "SELECT * FROM Contact WHERE id_contact = '{}'".format(contactId)
        contact = recup_bdd(query, True)

        if contact:
            return render_template('contactDelete.html', contact=contact)

    elif request.method == 'POST':
        # Requête dans la base de données
        query = "DELETE FROM Contact WHERE id_contact = '{}'".format(contactId)
        action_bdd(query)

        # Redirection vers la liste des contacts avec message de confirmation
        flash("Le contact a été supprimé", "danger")
        return redirect(url_for('liste_contacts'))


# Définir la route pour afficher la liste des groupes
@app.route("/groupes")
def liste_groupes():
    # Récupération de tout les groupes
    query = "SELECT * FROM Groupe"
    groupes = recup_bdd(query)

    # Rendu du modèle avec les données récupérées
    return render_template('groupeList.html', groupes=groupes)


@app.route("/groupes/new",  methods=['POST', 'GET'])
def ajouter_groupe():
    if request.method == 'POST':
        # Récupération des informations du formulaire
        nom = request.form['nom']
        photo = request.form['photo']

        # Requête dans la base de données
        query = '''
            INSERT INTO Groupe (nom_de_groupe, photo_groupe, created_date, updated_date) 
            VALUES ('{}', '{}', '{}', '{}')
        '''.format(nom, photo, now(), now())
        action_bdd(query)

        # Redirection vers la liste des groupes avec message de confirmation
        flash("Le groupe a été créé", "success")
        return redirect(url_for('liste_groupes'))

    elif request.method == 'GET':
        return render_template('groupeNew.html')

@app.route("/groupes/<int:groupeId>/edit", methods=['GET', 'POST'])
def edit_groupe(groupeId):
    # Récupération du groupe
    query = "SELECT * FROM Groupe WHERE id_groupe = {}".format(groupeId)
    groupe = recup_bdd(query, True)

    if request.method == 'GET':
        if groupe:
            return render_template('groupeEdit.html', groupe=groupe)

    elif request.method == 'POST':
        # Vérification de modification des valeurs
        i = 1
        doUpdate = False
        for key in request.form:
            if request.form[key] != groupe[i]:
                doUpdate = True
            i += 1

        if doUpdate:
            # Récupération des informations du formulaire
            nom = request.form['nom']
            photo = request.form['photo']

            # Requête dans la base de données
            query = '''
                        UPDATE Groupe
                        SET nom='{}', photo_groupe='{}', updated_date='{}'
                        WHERE id_groupe='{}'
                    '''.format(nom, photo, now(), groupeId)
            action_bdd(query)

            # Message de confirmation
            flash("Le groupe a été modifié", "warning")

        # Redirection vers la liste des groupes
        return redirect(url_for('liste_groupes'))


@app.route("/groupes/<int:groupeId>/delete", methods=['GET', 'POST'])
def delete_groupe(groupeId):
    if request.method == 'GET':
        # Récupération du contact
        query = "SELECT * FROM Groupe WHERE id_groupe = '{}'".format(groupeId)
        groupe = recup_bdd(query, True)

        if groupe:
            return render_template('groupeDelete.html', groupe=groupe)

    elif request.method == 'POST':
        # Requête dans la base de données (suppression du groupe)
        query = "DELETE FROM Groupe WHERE id_groupe = '{}'".format(groupeId)
        action_bdd(query)

        # Requête dans la base de données (suppression des liens avec les contacts)
        query = "DELETE FROM Appartenir WHERE id_groupe = '{}'".format(groupeId)
        action_bdd(query)

        # Redirection vers la liste des groupes avec message de confirmation
        flash("Le groupe a été supprimé", "danger")
        return redirect(url_for('liste_groupes'))


# Route pour l'export CSV

@app.route('/export_csv/<table_name>')
def export_csv(table_name):
    # Récupération des données de la table spécifiée
    query = "SELECT * FROM {}".format(table_name)
    data = recup_bdd(query)

    # Générer le contenu CSV
    csv_content = generate_csv_content(data)

    # Retourner le contenu CSV en tant que fichier téléchargeable
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={table_name}_export.csv"}
    )

def generate_csv_content(data):
    output = io.StringIO()
    writer = csv.writer(output)

    # Ajouter les données CSV
    for row in data:
        writer.writerow(row)

    return output.getvalue()


def process_csv(file_path, table_name):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Ignore the header, assuming the CSV does not have one
        for row in reader:
            # Vérifier si la ligne a suffisamment de colonnes
            if len(row) >= 9:
                # Créer un dictionnaire associant chaque en-tête à sa valeur respective
                data = {
                    "nom": row[1],
                    "prenom": row[2],
                    "e_mail": row[3],
                    "tel": row[4],
                    "date_naissance": row[5],
                    "photo_profil": row[6],
                    "created_date": row[7],
                    "updated_date": row[8]
                }
                # Insérer dans la base de données en utilisant la fonction appropriée
                insert_data_into_db(data, table_name)
            else:
                # Gérer le cas où la ligne n'a pas suffisamment de colonnes
                print(f"La ligne {row} n'a pas suffisamment de colonnes.")

    # Réinitialiser la séquence d'auto-incrémentation après l'importation
    reset_sequence('Contact')


def reset_sequence(table_name):
    # Connexion à la base de données
    conn = sqlite3.connect('hackathon_bdd.sqlite')
    cursor = conn.cursor()

    # Génération de la chaîne de requête dynamique
    query = "UPDATE sqlite_sequence SET seq = 0 WHERE name = ?"

    # Exécution de la commande SQL
    cursor.execute(query, (table_name,))

    # Validez la transaction et fermez la connexion
    conn.commit()
    conn.close()
@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    if request.method == 'POST':
        # Sauvegarder les fichiers dans le dossier d'upload
        file_contact = request.files['file_contact']
        file_groupe = request.files['file_groupe']
        ##file_appartenir = request.files['file_appartenir']

        contact_filename = secure_filename(file_contact.filename)
        groupe_filename = secure_filename(file_groupe.filename)
        ##appartenir_filename = secure_filename(file_appartenir.filename)

        contact_path = os.path.join(app.config['UPLOAD_FOLDER'], contact_filename)
        groupe_path = os.path.join(app.config['UPLOAD_FOLDER'], groupe_filename)
        ##appartenir_path = os.path.join(app.config['UPLOAD_FOLDER'], appartenir_filename)

        file_contact.save(contact_path)
        file_groupe.save(groupe_path)
        ##file_appartenir.save(appartenir_path)

        # Traiter les fichiers CSV
        process_csv(contact_path, 'contact')
        process_csv(groupe_path, 'groupe')
        ##process_csv(appartenir_path, 'appartenir')

        flash('Données importées avec succès', 'success')
        return redirect(url_for('index'))

    return render_template('import_csv.html')

def parse_csv(file):
    csv_data = []
    csv_reader = csv.reader(file)
    for row in csv_reader:
        csv_data.append(row)
    return csv_data

def insert_data_into_db(data, table_name):
    # Connexion à la base de données
    conn = sqlite3.connect('hackathon_bdd.sqlite')
    cursor = conn.cursor()

    # Génération de la chaîne de requête dynamique
    columns = ', '.join([f'"{col}"' for col in data.keys()])
    placeholders = ', '.join(['?' for _ in data])
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Insertion des données dans la base de données
    cursor.execute(query, tuple(data.values()))

    # Validez la transaction et fermez la connexion
    conn.commit()
    conn.close()

def process_csv_data(data, table_name):
    # Utilisez la fonction modifiée pour insérer les données
    insert_data_into_db(data, table_name)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)