from flask import Flask, render_template, request, redirect, url_for
import db

app = Flask(__name__)

@app.route("/")
def home():    
    clients = db.get_liste_clients()
    return render_template("clients.html", clients=clients)
    
@app.route("/client/<nom_client>", methods=["GET", "POST"])
def detail_client(nom_client):
    
    success = False

    if request.method == "POST":
        print ("test")
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
    
    return render_template("client_detail.html", client=client_data)
    
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