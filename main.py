from flask import Flask, render_template, Response, request, redirect, url_for, flash, session
from function import *
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import csv
import io

app = Flask(__name__)
app.secret_key = 'test'

bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT * FROM User WHERE username = ?"
        values = (username,)
        user = recup_bdd(query, values, doOne=True)

        if not user:
            flash("Invalid Username/Password", "danger")
            return redirect(url_for('login'))

        if valid_login(user[2], password):
            session['username'] = username
            session['id'] = user[0]
            session['grade'] = user[5]

            flash("Bienvenue "+username, "success")
            return redirect(url_for('index'))

        else:
            flash("Invalid Username/Password", "danger")
            return render_template('auth/login.html')

    elif request.method == 'GET':
        return render_template('auth/login.html')


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        session.pop('id', None)
        flash("Vous avez été deconnecté", "danger")
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_ctrl = request.form['password_ctrl']

        if password != password_ctrl:
            flash("Les mots de passe ne sont pas identiques", "danger")
            return redirect(url_for('register'))

        else:
            query = "SELECT * FROM User WHERE username = ?"
            values = (username,)
            user = recup_bdd(query, values, doOne=True)

            if user:
                flash("Ce username est déjà pris", "danger")
                return redirect(url_for('register'))

            else:
                password_crypt = bcrypt.generate_password_hash(password)

                query = '''
                        INSERT INTO User (username, password, created_date, updated_date, grade)
                        VALUES (?, ?, ?, ?, ?)'''
                values = (username, password_crypt, now(), now(), 0)
                action_bdd(query, values)

                flash("Le compte a été créer", "success")
                return redirect(url_for('login'))


@app.get("/contacts")
def liste_contacts():
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        # Récupération de tout les contacts
        query = "SELECT * FROM Contact WHERE id_user = ?"
        values = (session['id'],)
        contacts = recup_bdd(query, values)

        listIds = set(getListIds(contacts, 8))  # set permet d'avoir seulement une occurence par element

        # Récupération des nom de groupe
        placeholders = ",".join(["?"] * len(listIds))
        query = "SELECT * FROM Groupe WHERE id_groupe IN ({})".format(placeholders)
        values = tuple(listIds)
        groupes = recup_bdd(query, values)

        # Création de la liste à afficher
        listAffichage = []
        for contact in contacts:
            elem = {"id": contact[0],
                    "nom": contact[1],
                    "prenom": contact[2],
                    "email": contact[3],
                    "tel": contact[4],
                    "date": contact[5]
                    }
            for groupe in groupes:
                if contact[8] == groupe[0]:
                    elem["nom_groupe"] = groupe[1]

            listAffichage.append(elem)

        return render_template('contactList.html', contacts=listAffichage)


@app.get("/contacts/admin")
def liste_contacts_admin():
    if 'id' not in session:
        return redirect(url_for('login'))

    elif session['grade'] != 1:
        flash("Vous n'êtes pas administateur", "danger")
        return redirect(url_for('index'))

    else:
        # Récupération de tout les contacts
        query = "SELECT * FROM Contact"
        contacts = recup_bdd(query)

        # Rendu du modèle avec les données récupérées
        return render_template('contactListAdmin.html', contacts=contacts)


@app.route("/contacts/new",  methods=['POST', 'GET'])
def ajouter_contact():
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        if request.method == 'POST':
            # Récupération des informations du formulaire
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            tel = request.form['tel']
            date_naissance = request.form['dob']
            groupe = request.form['groupe']
            if not groupe:
                groupe = 1

            # Requête dans la base de données
            query = '''
                INSERT INTO Contact (nom, prenom, e_mail, tel, date_naissance, created_date, updated_date, id_groupe, id_user)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            values = (nom, prenom, email, tel, date_naissance, now(), now(), groupe, session["id"])
            action_bdd(query, values)

            # Redirection vers la liste des contacts avec message de confirmation
            flash("Le contact a été créé", "success")
            return redirect(url_for('liste_contacts'))

        elif request.method == 'GET':
            # Récupération de la liste des groupes
            query_contacts = "SELECT * FROM Groupe WHERE id_user=?"
            values = (session['id'],)
            groupes = recup_bdd(query_contacts, values)

            return render_template('contactNew.html', groupes=groupes)


@app.route("/contacts/<int:contactId>/edit", methods=['GET', 'POST'])
def edit_contact(contactId):
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        # Récupération du contact
        query = "SELECT * FROM Contact WHERE id_contact = ?"
        values = (contactId,)
        contact = recup_bdd(query, values, True)

        if request.method == 'GET':
            if contact:
                # Récupération de la liste des groupes
                query_groupes = "SELECT * FROM Groupe WHERE id_user=?"
                values = (session['id'],)
                groupes = recup_bdd(query_groupes, values)

                query_g_selected = "SELECT * FROM Groupe WHERE id_groupe=?"
                values = (contact[8],)
                groupe_selected = recup_bdd(query_g_selected, values, True)

                return render_template('contactEdit.html', contact=contact, groupes=groupes, groupe_selected=groupe_selected)

        elif request.method == 'POST':
            # Vérification de modification des valeurs
            i = 1
            doUpdate = False
            for key in request.form:
                if key == "groupe":
                    if int(request.form[key]) != contact[8]:
                        doUpdate = True
                elif request.form[key] != contact[i]:
                    doUpdate = True
                i += 1

            if doUpdate:
                # Récupération des informations du formulaire
                nom = request.form['nom']
                prenom = request.form['prenom']
                email = request.form['email']
                tel = request.form['tel']
                date_naissance = request.form['dob']
                groupe = request.form['groupe']

                print(groupe)


                # Requête dans la base de données
                query = '''
                            UPDATE Contact
                            SET nom=?, prenom=?, e_mail=?, tel=?, date_naissance=?, updated_date=?, id_groupe=?
                            WHERE id_contact=? AND id_user=?
                        '''
                values = (nom, prenom, email, tel, date_naissance, now(), groupe, contactId, session['id'])
                action_bdd(query, values)

                # Message de confirmation
                flash("Le contact a été modifié", "warning")

            else:
                # Message d'erreur
                flash("Le contact non modifié : Aucune valeur modifié", "warning")

            # Redirection vers la liste des contacts
            return redirect(url_for('liste_contacts'))


@app.route("/contacts/<int:contactId>/delete", methods=['GET', 'POST'])
def delete_contact(contactId):
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        if request.method == 'GET':
            # Récupération du contact
            query = "SELECT * FROM Contact WHERE id_contact = ?"
            values = (contactId,)
            contact = recup_bdd(query, values, True)

            if contact:
                return render_template('contactDelete.html', contact=contact)

        elif request.method == 'POST':
            # Requête dans la base de données
            query = "DELETE FROM Contact WHERE id_contact = ?"
            values = (contactId,)
            action_bdd(query, values)

            # Redirection vers la liste des contacts avec message de confirmation
            flash("Le contact a été supprimé", "danger")
            return redirect(url_for('liste_contacts'))


# Définir la route pour afficher la liste des groupes
@app.route("/groupes")
def liste_groupes():
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        # Récupération de tout les groupes
        query = "SELECT * FROM Groupe WHERE id_user = ?"
        values = (session['id'],)
        groupes = recup_bdd(query, values)

        # Rendu du modèle avec les données récupérées
        return render_template('groupeList.html', groupes=groupes)


# Définir la route pour afficher la liste des groupes ADMIN
@app.route("/groupes/admin")
def liste_groupes_admin():
    if 'id' not in session:
        return redirect(url_for('login'))

    elif session['grade'] != 1:
        flash("Vous n'êtes pas administateur", "danger")
        return redirect(url_for('index'))

    else:
        # Récupération de tout les groupes
        query = "SELECT * FROM Groupe"
        groupes = recup_bdd(query)

        # Rendu du modèle avec les données récupérées
        return render_template('groupeListAdmin.html', groupes=groupes)


@app.route("/groupes/new",  methods=['POST', 'GET'])
def ajouter_groupe():
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        if request.method == 'POST':
            # Récupération des informations du formulaire
            nom = request.form['nom']

            # Vérification nom
            query = "SELECT * FROM Groupe WHERE nom_de_groupe=?"
            values = (nom,)
            groupe = recup_bdd(query, values)

            if groupe:
                flash("Le nom existe déjà", "danger")
                return redirect(url_for('ajouter_groupe'))

            else:
                # Requête dans la base de données
                query_groupe = '''
                            INSERT INTO Groupe (nom_de_groupe, created_date, updated_date, id_user) 
                            VALUES (?, ?, ?, ?)
                        '''
                values = (nom, now(), now(), session['id'])
                action_bdd(query_groupe, values)

                # Redirection vers la liste des groupes avec message de confirmation
                flash("Le groupe a été créé", "success")
                return redirect(url_for('liste_groupes'))

        elif request.method == 'GET':
            return render_template('groupeNew.html')

@app.route("/groupes/<int:groupeId>/edit", methods=['GET', 'POST'])
def edit_groupe(groupeId):
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        # Récupération du groupe
        query = "SELECT * FROM Groupe WHERE id_groupe = ?"
        values = (groupeId,)
        groupe = recup_bdd(query, values, True)

        if request.method == 'GET':
            if groupe:
                return render_template('groupeEdit.html', groupe=groupe)

        elif request.method == 'POST':
            # Récupération des informations du formulaire
            nom = request.form['nom']
            if nom != groupe[1]:
                # Vérification nom
                query = "SELECT * FROM Groupe WHERE nom_de_groupe=?"
                values = (nom,)
                groupe_exist = recup_bdd(query, values)

                if groupe_exist:
                    flash("Le nom existe déjà", "danger")
                    return redirect(url_for('edit_groupe', groupeId=groupeId))

                else:
                    # Requête dans la base de données
                    query = '''
                                UPDATE Groupe
                                SET nom_de_groupe=?, updated_date=?
                                WHERE id_groupe=? AND id_user=?
                            '''
                    values = (nom, now(), groupeId, 1)
                    action_bdd(query, values)

                    # Message de confirmation
                    flash("Le groupe a été modifié", "warning")

            # Redirection vers la liste des groupes
            return redirect(url_for('liste_groupes'))


@app.route("/groupes/<int:groupeId>/delete", methods=['GET', 'POST'])
def delete_groupe(groupeId):
    if 'id' not in session:
        return redirect(url_for('login'))

    else:
        if request.method == 'GET':
            # Récupération du contact
            query = "SELECT * FROM Groupe WHERE id_groupe = ?"
            values = (groupeId,)
            groupe = recup_bdd(query, values, True)

            if groupe:
                return render_template('groupeDelete.html', groupe=groupe)

        elif request.method == 'POST':
            # Requête dans la base de données (suppression du groupe)
            query = "DELETE FROM Groupe WHERE id_groupe = ?"
            values = (groupeId,)
            action_bdd(query, values)

            # Redirection vers la liste des groupes avec message de confirmation
            flash("Le groupe a été supprimé", "danger")
            return redirect(url_for('liste_groupes'))



# Route pour l'export CSV
@app.route('/export_csv/<table_name>')
def export_csv(table_name):
    if 'id' not in session:
        return redirect(url_for('login'))

    user_id = session['id']

    # Récupération des données de la table spécifiée liées à l'utilisateur actuel
    query = f"SELECT * FROM {table_name} WHERE id_user = ?"
    values = (user_id,)
    data = recup_bdd(query, values)

    # Générer le contenu CSV
    csv_content = generate_csv_content(data)

    # Renommer le fichier CSV en fonction du nom de la table
    filename = f"{table_name}_export.csv"

    # Retourner le contenu CSV en tant que fichier téléchargeable avec le nouveau nom
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

def generate_csv_content(data):
    output = io.StringIO()
    writer = csv.writer(output)

    # Ajouter les données CSV
    for row in data:
        writer.writerow(row)

    return output.getvalue()


def process_csv_contact(file_path, table_name):
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
                    "created_date": row[6],
                    "updated_date": row[7],
                    "id_user": row[8]
                }
                # Insérer dans la base de données en utilisant la fonction appropriée
                insert_data_into_db(data, table_name)
            else:
                # Gérer le cas où la ligne n'a pas suffisamment de colonnes
                print(f"La ligne {row} n'a pas suffisamment de colonnes.")

    # Réinitialiser la séquence d'auto-incrémentation après l'importation
    reset_sequence('Contact')

def process_csv_groupe(file_path, table_name):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Ignore the header, assuming the CSV does not have one
        for row in reader:
            # Vérifier si la ligne a suffisamment de colonnes
            if len(row) >= 4:
                # Créer un dictionnaire associant chaque en-tête à sa valeur respective
                data = {
                    "nom_de_groupe": row[1],
                    "created_date": row[2],
                    "updated_date": row[3],
                    "id_user": row[4]
                }
                # Insérer dans la base de données en utilisant la fonction appropriée
                insert_data_into_db(data, table_name)
            else:
                # Gérer le cas où la ligne n'a pas suffisamment de colonnes
                print(f"La ligne {row} n'a pas suffisamment de colonnes.")

    # Réinitialiser la séquence d'auto-incrémentation après l'importation
    reset_sequence('Groupe')

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
        file_contact = request.files.get('file_contact')
        file_groupe = request.files.get('file_groupe')

        import_contact = request.form.get('import_contact')
        import_groupe = request.form.get('import_groupe')

        if import_contact and file_contact:
            contact_filename = secure_filename(file_contact.filename)
            contact_path = os.path.join(app.config['UPLOAD_FOLDER'], contact_filename)
            file_contact.save(contact_path)
            process_csv_contact(contact_path, 'contact')
            flash('Données de contact importées avec succès', 'success')

        if import_groupe and file_groupe:
            groupe_filename = secure_filename(file_groupe.filename)
            groupe_path = os.path.join(app.config['UPLOAD_FOLDER'], groupe_filename)
            file_groupe.save(groupe_path)
            process_csv_groupe(groupe_path, 'groupe')
            flash('Données de groupe importées avec succès', 'success')

        return redirect(url_for('liste_contacts'))

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