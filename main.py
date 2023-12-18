from flask import Flask, render_template, Response, request, redirect, url_for, flash
from function import *
import csv
import io

app = Flask(__name__)
app.secret_key = 'test'


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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        values = (nom, prenom, email, tel, date_naissance, photo, now(), now())
        action_bdd(query, values)

        # Redirection vers la liste des contacts avec message de confirmation
        flash("Le contact a été créé", "success")
        return redirect(url_for('liste_contacts'))

    elif request.method == 'GET':
        return render_template('contactNew.html')


@app.route("/contacts/<int:contactId>/edit", methods=['GET', 'POST'])
def edit_contact(contactId):
    # Récupération du contact
    query = "SELECT * FROM Contact WHERE id_contact = ?"
    values = (contactId,)
    contact = recup_bdd(query, values, True)

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
                        SET nom=?, prenom=?, e_mail=?, tel=?, date_naissance=?, photo_profil=?, updated_date=?
                        WHERE id_contact=?
                    '''
            values = (nom, prenom, email, tel, date_naissance, photo, now(), contactId)
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
            VALUES (?, ?, ?, ?)
        '''
        values = (nom, photo, now(), now())
        action_bdd(query, values)

        # Redirection vers la liste des groupes avec message de confirmation
        flash("Le groupe a été créé", "success")
        return redirect(url_for('liste_groupes'))

    elif request.method == 'GET':
        return render_template('groupeNew.html')

@app.route("/groupes/<int:groupeId>/edit", methods=['GET', 'POST'])
def edit_groupe(groupeId):
    # Récupération du groupe
    query = "SELECT * FROM Groupe WHERE id_groupe = ?"
    values = (groupeId,)
    groupe = recup_bdd(query, values, True)

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
                        SET nom_de_groupe=?, photo_groupe=?, updated_date=?
                        WHERE id_groupe=?
                    '''
            values = (nom, photo, now(), groupeId)
            action_bdd(query, values)

            # Message de confirmation
            flash("Le groupe a été modifié", "warning")

        # Redirection vers la liste des groupes
        return redirect(url_for('liste_groupes'))


@app.route("/groupes/<int:groupeId>/delete", methods=['GET', 'POST'])
def delete_groupe(groupeId):
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

        # Requête dans la base de données (suppression des liens avec les contacts)
        query = "DELETE FROM Appartenir WHERE id_groupe = ?"
        values = (groupeId,)
        action_bdd(query, values)

        # Redirection vers la liste des groupes avec message de confirmation
        flash("Le groupe a été supprimé", "danger")
        return redirect(url_for('liste_groupes'))


# Route pour l'export CSV
@app.route('/export_csv')
def export_csv():

    # Récupération de tout les contacts
    query = "SELECT * FROM Contact"
    contacts = recup_bdd(query)

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


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)