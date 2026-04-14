import os
from pathlib import Path
import shutil #sert a supprimer les dossiers a tout ce qu'il y a en dessous
import csv


chemin_actuel = os.getcwd() #rep du script
BASE_CLIENTS = os.path.join(chemin_actuel, "Clients") # .\DossierScript\Clients\
os.makedirs(BASE_CLIENTS, exist_ok=True) #On créé le dossier Clients, s'il n'existe pas

def get_liste_clients(): #Récupére tout les nom de dossiers contenu dans le dossiers Clients
    return [d for d in os.listdir(BASE_CLIENTS) if os.path.isdir(os.path.join(BASE_CLIENTS, d))]

def get_client_path(nom_client): #renvoi le chemin vers le dossier client
    return os.path.join(BASE_CLIENTS, nom_client)
    
def get_client_upload(nom_client): #renvoi le chemin vers le dossier ou upload les fichiers du client
    DOSSIER_CIBLE = get_client_path(nom_client)
    return os.path.join(DOSSIER_CIBLE, "Documents")
    
def get_client_csv(nom_client): #renvoi le chemin vers le fichier InfosClient.csv
    DOSSIER_CIBLE = get_client_path(nom_client)
    return os.path.join(DOSSIER_CIBLE, "InfosClient.csv")
    
def get_client_info(nom_client, info_demande): #info possible: Nom;Prénom;Adresse;Email;Teléphone;VetoNom;VetoAdresse;VetoTeléphone;ContactNom;ContactPrénom;ContactTeléphone;tmp_trajet;choix_cle /!\ la casse
    FICHIER_CIBLE = get_client_csv(nom_client)
    if os.path.isfile(FICHIER_CIBLE):
            with open(FICHIER_CIBLE, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                try:
                    ligne = next(reader) #donne la première ligne de données
                    return ligne.get(info_demande) #retourne l'infos demandé 
                except StopIteration:
                    return None  # info non disponible
    print (f"db_error_1 : fichier {FICHIER_CIBLE} non existant") #log
    return #fichier non existant
    
def get_client_animaux_path(nom_client): #renvoi le chemin vers le dossier Animaux du client (celui-ci contient un fichier csv par animal)
    DOSSIER_CIBLE = get_client_path(nom_client)
    return os.path.join(DOSSIER_CIBLE, "Animaux")
    
def get_liste_animaux_client(nom_client): #renvoi la liste des animaux du client (nom du fichier)
    DOSSIER_CIBLE = get_client_animaux_path(nom_client)
    return [os.path.splitext(f)[0] for f in os.listdir(DOSSIER_CIBLE)] #os.path.splitext(f)[0] pour récupe uniquement le nom du fichier
    
def get_animal_info(nom_client, nom_animal, info_demande):#recupére: liste des infos possible - Espéce;Sexe;Nom;Stérilisé;DateDeNaissance;Caractère;Nourriture;BesoinParticulier /!\ a la casse
    DOSSIER_CIBLE = get_client_animaux_path(nom_client)
    CSV = f"{nom_animal}.csv"
    FICHIER_CIBLE = os.path.join(DOSSIER_CIBLE, CSV)
    if os.path.isfile(FICHIER_CIBLE):
            with open(FICHIER_CIBLE, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                try:
                    ligne = next(reader) #donne la première ligne de données
                    return ligne.get(info_demande) #retourne l'infos demandé 
                except StopIteration:
                    return None  # info non disponible
    print (f"db_error_2 : fichier {FICHIER_CIBLE} non existant") #log
    return #fichier non existant
    
def get_client_documents_path(nom_client): #renvoi le chemin vers le dossier de stockage des documents upload
    DOSSIER_CIBLE = get_client_path(nom_client)
    return os.path.join(DOSSIER_CIBLE, "Documents")
    
def create_client(nouveau_client): #permet la création d'un nouveau clients (structure : dossiers et csv) 
    chemin_nouveau = os.path.join(BASE_CLIENTS, nouveau_client)
    dossier_animaux = os.path.join(chemin_nouveau, "Animaux")
    dossier_document = os.path.join(chemin_nouveau, "Documents")
    infos_client_csv = os.path.join(chemin_nouveau, "InfosClient.csv")
    if not os.path.exists(chemin_nouveau):
        os.makedirs(chemin_nouveau)
        os.makedirs(dossier_animaux)
        os.makedirs(dossier_document)
        with open(infos_client_csv, "w", newline='', encoding='utf-8') as f:
            fieldnames = ["Nom", "Prénom", "Adresse", "Email", "Teléphone", "VetoNom", "VetoAdresse", "VetoTeléphone", "ContactNom", "ContactPrénom", "ContactTeléphone", "tmp_trajet", "choix_cle"]
            writer = csv.DictWriter(f, fieldnames, delimiter=';') #indique les colonnes et comment fonctionne le fichier (séparateur ;)
            writer.writeheader() #Ecrit la ligne d'entéte (les colonne)
            writer.writerow({col: "" for col in fieldnames}) #écris des valeur a vide pour initialiser
            return True, f"Dossier créé : {nouveau_client}" #on renvoi si réussite + message
    else:
        return False, "Ce dossier existe déjà." #on renvoi si echec + message
        
def delete_client(nom_client): #permet la suppression d'un dossier client
    dossier_a_suppr = os.path.join(BASE_CLIENTS, nom_client)
    if os.path.exists(dossier_a_suppr):
        shutil.rmtree(dossier_a_suppr) #suppr le dossier et tous ce qu'il y a en dessous
        return True, f"Dossier supprimé : {nom_client}" #on renvoi si réussite + message
    else:
        return False, f"Le dossier {nom_client} n'existe pas"  #on renvoi si réussite + message
        
def set_client_info(nom_client, info, valeur): #modifie: : liste des infos possible - Nom;Prénom;Adresse;Email;Teléphone;VetoNom;VetoAdresse;VetoTeléphone;ContactNom;ContactPrénom;ContactTeléphone;tmp_trajet;choix_cle /!\ la casse
    FICHIER_CIBLE = get_client_csv(nom_client)
    if not os.path.isfile(FICHIER_CIBLE):
        print(f"db_error_3 : fichier {FICHIER_CIBLE} non existant") #log
        return
        
    with open(FICHIER_CIBLE, newline='', encoding='utf-8') as f: #lecture des données existante
        reader = csv.DictReader(f, delimiter=';')
        lignes = list(reader)
        fieldnames = reader.fieldnames
    if not lignes:
        print(f"db_error_4 : fichier {FICHIER_CIBLE}, manque valeurs")
        return
        
    lignes[0][info] = valeur #on change la valeur souhaité dans la variable
    
    with open(FICHIER_CIBLE, "w", newline='', encoding='utf-8') as f: #réécris le fichier
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(lignes)
            
def set_animal_info(nom_client, nom_animal, info, valeur): #modifie: : liste des infos possible - Espéce;Sexe;Nom;Stérilisé;DateDeNaissance;Caractère;Nourriture;BesoinParticulier /!\ a la casse
    DOSSIER_CIBLE = get_client_animaux_path(nom_client)
    CSV = f"{nom_animal}.csv"
    FICHIER_CIBLE = os.path.join(DOSSIER_CIBLE, CSV)
    if not os.path.isfile(FICHIER_CIBLE):
        print(f"db_error_5 : fichier {FICHIER_CIBLE} non existant") #log
        return
        
    with open(FICHIER_CIBLE, newline='', encoding='utf-8') as f: #lecture des données existante
        reader = csv.DictReader(f, delimiter=';')
        lignes = list(reader)
        fieldnames = reader.fieldnames
        
    lignes[0][info] = valeur #on change la valeur souhaité dans la variable
    
    with open(FICHIER_CIBLE, "w", newline='', encoding='utf-8') as f: #réécris le fichier
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(lignes)
            
def create_animal(nom_client, nom_animal):
    DOSSIER_CIBLE = get_client_animaux_path(nom_client)
    FICHIER_NOUVEAU = os.path.join(DOSSIER_CIBLE, f"{nom_animal}.csv")
    if not os.path.exists(FICHIER_NOUVEAU):
        colonnes = ["Espéce", "Sexe", "Nom", "Stérilisé", "DateDeNaissance", "Caractère", "Nourriture", "BesoinParticulier"]
        # Créer le fichier et écrire l'en-tête
        with open(FICHIER_NOUVEAU, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=colonnes, delimiter=";")
            writer.writeheader()  # écrit la ligne des titres
            writer.writerow({col: "" for col in colonnes}) #écris des valeur a vide pour initialiser
        return True, f"Animal créé : {nom_animal}" #on renvoi si réussite + message
    else:
        return False, "Cette animal existe déjà." #on renvoi si echec + message
    
def delete_animal(nom_client, nom_animal):
    DOSSIER_CIBLE = get_client_animaux_path(nom_client)
    CSV = f"{nom_animal}.csv"
    FICHIER_CIBLE = os.path.join(DOSSIER_CIBLE, CSV)
    if os.path.exists(FICHIER_CIBLE):
                os.remove(FICHIER_CIBLE)
                return True, "Suppression réussi" #on renvoi si echec + message
    else:
        print(f"db_error_6 : fichier : {FICHIER_CIBLE}, introuvable")
        return False