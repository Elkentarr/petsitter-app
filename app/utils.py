import os
import webbrowser #pour ouvrir des liens
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName #permet de gérer les pdf
from datetime import datetime #pour récup la date du jouer
import math
from decimal import Decimal, ROUND_DOWN, ROUND_UP #pour arrondir a l'inférieur l'avance
import db


#Chemins ou sont stocké de modeles
chemin_actuel = os.getcwd() #rep du script
dossier_modele = os.path.join(chemin_actuel, "Modeles")

def calculer(tmp_garde_totl, prix_horraire, nbrs_de_garde, tmp_trajet, prix_essence_trajet):
        try:
            # Calculs
            total_prix_garde_no_trajet = (tmp_garde_totl / Decimal('60')) * prix_horraire

            total_prix_trajet_no_essence = (
                (nbrs_de_garde * (tmp_trajet * Decimal('2'))) / Decimal('60')
            ) * prix_horraire

            total_prix_essence = (prix_essence_trajet * Decimal('2')) * nbrs_de_garde

            total_prix_essence_ac_urssaf = (
                total_prix_essence * Decimal('1.215')
            )

            total_prix_trajet = (
                total_prix_trajet_no_essence + total_prix_essence_ac_urssaf
            )

            total_prix_garde = (
                total_prix_garde_no_trajet + total_prix_trajet
            )

            # Avance (25%) → coupée à 2 décimales
            prix_avance_garde = (
                total_prix_garde * Decimal('0.25')
            ).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            prix_reste_garde = (
                total_prix_garde - prix_avance_garde
            ).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

            # Coût trajet pour une garde
            cout_trajet = (
                ((tmp_trajet * Decimal('2')) / Decimal('60')) * prix_horraire
                + (prix_essence_trajet * Decimal('2'))
                + ((prix_essence_trajet * Decimal('2')) * Decimal('0.215'))
            )

            # Tarifs (arrondi au centime supérieur)
            def arrondi_sup(val):
                return val.quantize(Decimal('0.00'), rounding=ROUND_UP)

            tarif_15 = arrondi_sup(((Decimal('15') / Decimal('60')) * prix_horraire) + cout_trajet)
            tarif_30 = arrondi_sup(((Decimal('30') / Decimal('60')) * prix_horraire) + cout_trajet)
            tarif_45 = arrondi_sup(((Decimal('45') / Decimal('60')) * prix_horraire) + cout_trajet)
            tarif_60 = arrondi_sup(((Decimal('60') / Decimal('60')) * prix_horraire) + cout_trajet)
            
            return True, "calcul fini", cout_trajet, total_prix_garde_no_trajet, total_prix_trajet_no_essence, total_prix_essence_ac_urssaf, total_prix_trajet, prix_avance_garde, prix_reste_garde, total_prix_garde, tarif_15, tarif_30, tarif_45, tarif_60
            
        except ValueError:
            return False, "Veuillez entrer des valeurs numériques valides.", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 #on renvoi le bon nombre de valeur mais a 0
            
#REMPLISSAGE DOC PDF AVEC VALEUR
def fill_pdf(client, model_pdf, data): #nom_du_model.pdf (stocké dans .\Modeles), data a incorporer dans le model key: valeur, le model est un fichier pdf type formulaire avec des clé défini
    chemin_model_pdf = os.path.join(dossier_modele, model_pdf)
    dest_pdf = db.get_client_upload(client)
    nom_model = os.path.splitext(model_pdf)[0] #on récup juste le nom du model
    date_du_jour = datetime.now().strftime('%d-%m-%Y')
    fichier_pdf = f'{client}-{nom_model}_du_{date_du_jour}.pdf' #création du nom du fichier
    output_pdf = os.path.join(dest_pdf, fichier_pdf) #chemin complet avec fichier.pdf final
    try:
        pdf = PdfReader(chemin_model_pdf)
    except:
        return False, f"Le fichier {chemin_model_pdf}, n'existe pas"
    for page in pdf.pages:
        annotations = page.Annots
        if annotations:
            for annotation in annotations:
                if annotation.Subtype == PdfName('Widget') and annotation.T:
                    key = annotation.T[1:-1]  # nom du champ sans parenthèses
                    if key in data:
                        val = data[key]
                        if isinstance(val, type(PdfName('Yes'))):
                            # Pour une case à cocher (valeur PdfName)
                            annotation.V = val
                            annotation.AS = val
                        else:
                            # Pour un champ texte (valeur normale)
                            annotation.V = val
                            annotation.AP = None  # pour forcer la mise à jour de l'apparence
    
    PdfWriter().write(output_pdf, pdf)
    return True, f"fichier généré : {output_pdf}" #si succes et on renvoi le chemin du fichier pdf créé