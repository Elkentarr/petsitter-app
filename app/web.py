from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from app import db

app = Flask(__name__)

@app.route("/")
def home():    
    clients = db.get_liste_clients()
    return render_template("clients.html", clients=clients)
    
@app.route("/client/<nom_client>", methods=["GET", "POST"])
def detail_client(nom_client):
    
    success = False

    if request.method == "POST":
        # récupération des données du formulaire
        db.set_client_info(nom_client, "Nom", request.form["nom"])
        db.set_client_info(nom_client, "Prénom", request.form["prenom"])
        db.set_client_info(nom_client, "Email", request.form["email"])
        db.set_client_info(nom_client, "Teléphone", request.form["telephone"])
        db.set_client_info(nom_client, "Adresse", request.form["adresse"])
        
        success = True

    # GET → affichage
    client_data = {
        "Nom": db.get_client_info(nom_client, "Nom"),
        "Prenom": db.get_client_info(nom_client, "Prénom"),
        "Email": db.get_client_info(nom_client, "Email"),
        "Telephone": db.get_client_info(nom_client, "Teléphone"),
        "Adresse": db.get_client_info(nom_client, "Adresse"),
    }
    
    animaux = db.get_liste_animaux_client(nom_client) #récup la liste des animaux
    
    return render_template("client_detail.html", fiche_client=nom_client ,client=client_data, animaux=animaux)
    
@app.route("/client/<nom_client>/<nom_animal>", methods=["GET", "POST"])
def detail_animal(nom_client, nom_animal):    
        success = False
        
        if request.method == "POST":
            # récupération des données du formulaire
            nouvel_date_naissance = datetime.strptime(request.form["date_naissance"], "%Y-%m-%d").strftime("%d/%m/%Y") #remet dans son format correct DD/MM/YYYY
            
            sterilise = request.form.get("sterilise") #renvoi 1 ou None
            if sterilise :
                sterilise = 1
            else:
                sterilise = 0
            
            db.set_animal_info(nom_client, nom_animal, 'Espéce', request.form["espece"]), #remplis le champs tk avec la valeur de la ligne a la colonne Nom
            db.set_animal_info(nom_client, nom_animal, 'Sexe', request.form["sexe"]),
            db.set_animal_info(nom_client, nom_animal, 'Nom', request.form["nom"]),
            db.set_animal_info(nom_client, nom_animal, 'Stérilisé', sterilise), #Renvoi 1 ou 0
            db.set_animal_info(nom_client, nom_animal, 'DateDeNaissance', nouvel_date_naissance),
            db.set_animal_info(nom_client, nom_animal, 'Caractère', request.form["caractere"]),
            db.set_animal_info(nom_client, nom_animal, 'Nourriture', request.form["nourriture"]),
            db.set_animal_info(nom_client, nom_animal, 'BesoinParticulier', request.form["besoin"])
            
            success = True
            
        # GET → affichage
        date_de_naissance = db.get_animal_info(nom_client, nom_animal, 'DateDeNaissance') #format DD/MM/YYYY
        date_formatted = datetime.strptime(date_de_naissance, "%d/%m/%Y").strftime("%Y-%m-%d") #format pour html YYYY-MM-DD
        
        animal_data = {
            "espece": db.get_animal_info(nom_client, nom_animal, 'Espéce'), #remplis le champs tk avec la valeur de la ligne a la colonne Nom
            "sexe": db.get_animal_info(nom_client, nom_animal, 'Sexe'),
            "nom": db.get_animal_info(nom_client, nom_animal, 'Nom'),
            "sterilise": db.get_animal_info(nom_client, nom_animal, 'Stérilisé'), #Renvoi 1 ou 0
            "date_naissance": date_formatted,
            "caractere": db.get_animal_info(nom_client, nom_animal, 'Caractère'),
            "nourriture": db.get_animal_info(nom_client, nom_animal, 'Nourriture'),
            "besoin": db.get_animal_info(nom_client, nom_animal, 'BesoinParticulier')
        }
        
        return render_template("animal_detail.html", animal=animal_data, client=nom_client)
    
@app.route("/client/<fiche_client>/nouvel_animal", methods=["GET", "POST"])
def create_animal(fiche_client):

    message = None

    if request.method == "POST":
        nom_animal = request.form["nom"]

        success, msg = db.create_animal(fiche_client, nom_animal)

        message = msg

        if success:
            return redirect(url_for("detail_animal", nom_client=fiche_client, nom_animal=nom_animal))

    return render_template("create_animal.html", message=message)
    
@app.route("/client/new", methods=["GET", "POST"])
def create_client():

    message = None

    if request.method == "POST":
        nom = request.form["nom"]

        success, msg = db.create_client(nom)

        message = msg

        if success:
            return redirect(url_for("detail_client", nom_client=nom))

    return render_template("create_client.html", message=message)
    
@app.route("/client/delete/<nom_client>", methods=["GET", "POST"])
def delete_client(nom_client):
    if request.method == "POST":
        db.delete_client(nom_client)
        return redirect(url_for("home"))
    return render_template("delete_client.html", client=nom_client)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)