import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from tkcalendar import DateEntry #permet l'utilisation de champs date avec interface greaphique DateEntry(root, date_pattern='dd/mm/yyyy')
import webbrowser #pour ouvrir des liens
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName #permet de gérer les pdf
from datetime import datetime #pour récup la date du jouer
import db #récup le fichier db.py pour accèder a ses fonctions
import utils #récup le fichier utils.py pour accéder a ses fonctions
import os
from decimal import Decimal, ROUND_DOWN, ROUND_UP, InvalidOperation #pour arrondir a l'inférieur l'avance

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion autoEntreprise PetSitter")
        self.frames = {}
        self.history = []
        self.dossier_choisi = None  # Initialise la variable pour la récupérer dans les différente class - renverra le nom du dossier client uniquement
        
        for F in (SelectionClient, InfosClients, InfosGarde):
            page = F(parent=self, controller=self)
            self.frames[F] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SelectionClient)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()
        
        # Appelle automatiquement la méthode on_show si elle existe
        if hasattr(frame, "on_show"):
            frame.on_show()

        if self.history and self.history[-1] != page_class:
            self.history.append(page_class)
        elif not self.history:
            self.history.append(page_class)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            previous = self.history[-1]
            self.show_frame(previous)

class SelectionClient(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        controller.title("Gestion autoEntreprise PetSitter - Selection Client") #met a jour le titre de la fenêtre

        self.label = tk.Label(self, text="Choisissez un dossier :")
        self.label.pack(pady=10)

        self.combo = ttk.Combobox(self, state="readonly")
        self.combo.pack(padx=20, pady=10)
        self.combo.bind("<<ComboboxSelected>>", self.selection_change)
        
        #conteneur pour les bouton suivant et suppr
        bouton_frame = tk.Frame(self)
        bouton_frame.pack(pady=10)
        
        self.bouton_suppr = tk.Button(bouton_frame, text="Supprimer", state="disabled", command=self.supprimer_selection)
        self.bouton_suppr.pack(side='left', padx=5)

        self.bouton_suivant = tk.Button(bouton_frame, text="Suivant", state="disabled", command=self.confirmer_selection)
        self.bouton_suivant.pack(side='left', padx=5)

        self.dossier_selectionne = None

        self.actualiser_menu()

    def actualiser_menu(self):
        self.combo['values'] = db.get_liste_clients() + ["Nouveau client..."]
        self.combo.set('')
        self.bouton_suivant.config(state="disabled")
        self.bouton_suppr.config(state="disabled")

    def selection_change(self, event=None):
        selection = self.combo.get()
        if selection == "Nouveau client...":
            nom_nouveau = simpledialog.askstring("Nouveau Client", "Nom du client :")
            if nom_nouveau:
                success, message = db.create_client(nom_nouveau) #récupere le résultat de la fonction True ou False + mesage d'erreur
                if success:
                    messagebox.showinfo("Succès", message)
                else:
                    messagebox.showwarning("Erreur", message)
                self.actualiser_menu()
        else:
            self.bouton_suivant.config(state="normal")
            self.bouton_suppr.config(state="normal")

    def confirmer_selection(self):
        dossier_choisi = self.combo.get()
        if dossier_choisi and dossier_choisi != "Nouveau client...":
            self.controller.dossier_choisi = dossier_choisi #On récup la variable dossier choisi dans le controller pour l'utiliser n'importe ou
            self.controller.chemin = self.dossier_selectionne #pareille pour le chemin
            self.controller.show_frame(InfosClients)
        else:
            messagebox.showwarning("Sélection invalide", "Veuillez sélectionner un dossier valide.")
            
    def supprimer_selection(self):
        dossier_choisi = self.combo.get()
        if dossier_choisi and dossier_choisi != "Nouveau client...": #si la ligne est pas vide et que ce n'est pas nouveau client
            self.reponse = messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer {dossier_choisi}?")
            if self.reponse:
                success, message = db.delete_client(dossier_choisi)
                if success:
                    messagebox.showinfo("Succès", message)
                else:
                    messagebox.showwarning("Erreur", message)
        self.actualiser_menu()
            

class InfosClients(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller       
        self.animaux_widgets = {}  # Pour stocker les widgets par animal 
        self.nbr_animaux = 0 #pour compter le nbrs d'animaux
            
        # Création du Notebook (le conteneur d'onglets)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)

        # Création des cadres (frames) pour chaque onglet
        self.onglet_infoClient = ttk.Frame(self.notebook)
        self.onglet_infoVeto = ttk.Frame(self.notebook)
        self.onglet_infoContact = ttk.Frame(self.notebook)

        # Ajout des onglets au notebook avec un titre pour chacun
        self.notebook.add(self.onglet_infoClient, text="Infos client")
        self.notebook.add(self.onglet_infoVeto, text="Infos veto")
        self.notebook.add(self.onglet_infoContact, text="Infos contact urgence")

        # Labels + Champs ONGLET CLIENT
        tk.Label(self.onglet_infoClient, text="Nom ").grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.champ_nom_client = tk.Entry(self.onglet_infoClient, width=30) #Crée un widget Entry (champ texte où l’utilisateur peut saisir des données) dans l'onglet onglet_infoClient
        self.champ_nom_client.grid(row=0, column=2)

        tk.Label(self.onglet_infoClient, text="Prénom ").grid(row=0, column=3, padx=10, pady=5, sticky="e")
        self.champ_prenom_client = tk.Entry(self.onglet_infoClient, width=30)
        self.champ_prenom_client.grid(row=0, column=4, columnspan=2)

        tk.Label(self.onglet_infoClient, text="Adresse ").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.champ_adresse_client = tk.Entry(self.onglet_infoClient, width=73) 
        self.champ_adresse_client.grid(row=1, column=2, columnspan=3)

        tk.Label(self.onglet_infoClient, text="Email ").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.champ_email_client = tk.Entry(self.onglet_infoClient, width=30)
        self.champ_email_client.grid(row=2, column=2)

        tk.Label(self.onglet_infoClient, text="Téléphone ").grid(row=3, column=1, padx=10, pady=5, sticky="e")
        self.champ_telephone_client = tk.Entry(self.onglet_infoClient, width=30)
        self.champ_telephone_client.grid(row=3, column=2)

        tk.Label(self.onglet_infoClient, text="").grid(row=0, column=6, padx=20, pady=5, sticky="e") #juste pour rajouter de l'espacement a droite du tableau
        tk.Label(self.onglet_infoClient, text="").grid(row=0, column=0, padx=20, pady=5, sticky="w") #juste pour rajouter de l'espacement a gauche du tableau

        # Labels + Champs ONGLET VETO
        tk.Label(self.onglet_infoVeto, text="Nom ").grid(row=0, column=1, padx=10, pady=5, sticky="e")
        self.champ_nom_veto = tk.Entry(self.onglet_infoVeto, width=30) #Crée un widget Entry (champ texte où l’utilisateur peut saisir des données) dans l'onglet self.onglet_infoVeto
        self.champ_nom_veto.grid(row=0, column=2)

        tk.Label(self.onglet_infoVeto, text="Adresse ").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.champ_adresse_veto = tk.Entry(self.onglet_infoVeto, width=73) 
        self.champ_adresse_veto.grid(row=1, column=2, columnspan=40)

        tk.Label(self.onglet_infoVeto, text="Téléphone ").grid(row=3, column=1, padx=10, pady=5, sticky="e")
        self.champ_telephone_veto = tk.Entry(self.onglet_infoVeto, width=30)
        self.champ_telephone_veto.grid(row=3, column=2)

        tk.Label(self.onglet_infoVeto, text="").grid(row=0, column=6, padx=20, pady=5, sticky="e") #juste pour rajouter de l'espacement a droite du tableau
        tk.Label(self.onglet_infoVeto, text="").grid(row=0, column=0, padx=20, pady=5, sticky="w") #juste pour rajouter de l'espacement a gauche du tableau

        # Labels + Champs ONGLET CONTACT URGENCE
        tk.Label(self.onglet_infoContact, text="Personne à contacter en cas d’urgence autre que le propriétaire").grid(row=0, column=2, padx=10, pady=5, sticky="w", columnspan=40)

        tk.Label(self.onglet_infoContact, text="Nom ").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.champ_nom_contact = tk.Entry(self.onglet_infoContact, width=30)
        self.champ_nom_contact.grid(row=1, column=2)

        tk.Label(self.onglet_infoContact, text="Prénom ").grid(row=1, column=3, padx=10, pady=5, sticky="e")
        self.champ_prenom_contact = tk.Entry(self.onglet_infoContact, width=30)
        self.champ_prenom_contact.grid(row=1, column=4, columnspan=2)

        tk.Label(self.onglet_infoContact, text="Téléphone ").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.champ_telephone_contact = tk.Entry(self.onglet_infoContact, width=30)
        self.champ_telephone_contact.grid(row=2, column=2)

        tk.Label(self.onglet_infoContact, text="").grid(row=0, column=6, padx=20, pady=5, sticky="e") #juste pour rajouter de l'espacement a droite du tableau
        tk.Label(self.onglet_infoContact, text="").grid(row=0, column=0, padx=20, pady=5, sticky="w") #juste pour rajouter de l'espacement a gauche du tableau
        
        # Bouton de suppression
        self.btn_supprimer = ttk.Button(self, text="Supprimer un animal", command=self.supprimer_onglet)
        self.btn_supprimer.pack(side='left', padx=10, pady=10)

        # Bouton de Ajout
        self.btn_ajouter = ttk.Button(self, text="Ajouter un animal", command=lambda: self.ajouter_onglet(True, None))
        self.btn_ajouter.pack(side='right', padx=10, pady=10)
        
        
        # Créer un conteneur pour les boutons Enregistrer et Retour
        bouton_frame = tk.Frame(self)
        bouton_frame.pack(pady=10)
        
        # Bouton Retour
        self.bouton_retour = tk.Button(bouton_frame, text="Retour", command=controller.go_back)
        self.bouton_retour.pack(side='left', padx=5)

        # Bouton Enregistrer
        self.bouton_enregistrer = tk.Button(bouton_frame, text="Enregistrer", command=self.valider_formulaire)
        self.bouton_enregistrer.pack(side='left', padx=5)
        
        # Bouton suivant
        self.bouton_suivant = tk.Button(bouton_frame, text="suivant", command=self.next_onglet)
        self.bouton_suivant.pack(side='left', padx=5)
        
        # Associer la fonction à l’événement de changement d’onglet
        self.notebook.bind("<<NotebookTabChanged>>", self.verifier_bouton_supprimer)
                        
    def on_show(self):
        self.client = self.controller.dossier_choisi 
        self.controller.title(f"Gestion autoEntreprise PetSitter - Infos Client - {self.client}") #met a jour le titre de la fenêtre
        self.animaux_widgets = {}  # Vide les widgets par animal avant de réalimenter 
        self.nbr_animaux = 0 # met a 0 le compteur d'animaux
        self.charger_donnees() #charge les données infos clients
        self.verifier_bouton_supprimer()
    
    # === Fonctions ===

    def charger_donnees(self):
        # Récupère l'instance InfosGarde depuis le controller
        page_infos_garde = self.controller.frames[InfosGarde]  
        
        #On vide les onglets animaux dans un premier temps (si on a fait retour sur un client et on va sur un autre pour pas avoir les animaux d'un autre client)
        onglets_a_garder = ["Infos client", "Infos veto", "Infos contact urgence"]
        # Faire une copie de la liste des onglets pour éviter de modifier la structure pendant l’itération
        for tab_id in self.notebook.tabs():
            nom_onglet = self.notebook.tab(tab_id, option='text')
            if nom_onglet not in onglets_a_garder:
                self.notebook.forget(tab_id)

        #remplissage des lignes avec l'aide des fonctions db
        
        self.champ_nom_client.delete(0, tk.END) #vide le champs tk 0 signifie premier caractére jusqu'a la fin tk.END
        self.champ_nom_client.insert(0, db.get_client_info(self.client, 'Nom')) #remplis le champs tk avec la valeur de la ligne a la colonne Nom
        self.champ_prenom_client.delete(0, tk.END)
        self.champ_prenom_client.insert(0, db.get_client_info(self.client, 'Prénom'))
        self.champ_adresse_client.delete(0, tk.END)
        self.champ_adresse_client.insert(0, db.get_client_info(self.client, 'Adresse'))
        self.champ_email_client.delete(0, tk.END)
        self.champ_email_client.insert(0, db.get_client_info(self.client, 'Email'))
        self.champ_telephone_client.delete(0, tk.END)
        self.champ_telephone_client.insert(0, db.get_client_info(self.client, 'Teléphone'))
        self.champ_nom_veto.delete(0, tk.END)
        self.champ_nom_veto.insert(0, db.get_client_info(self.client, 'VetoNom'))
        self.champ_adresse_veto.delete(0, tk.END)
        self.champ_adresse_veto.insert(0, db.get_client_info(self.client, 'VetoAdresse'))
        self.champ_telephone_veto.delete(0, tk.END)
        self.champ_telephone_veto.insert(0, db.get_client_info(self.client, 'VetoTeléphone'))
        self.champ_nom_contact.delete(0, tk.END)
        self.champ_nom_contact.insert(0, db.get_client_info(self.client, 'ContactNom'))
        self.champ_prenom_contact.delete(0, tk.END)
        self.champ_prenom_contact.insert(0, db.get_client_info(self.client, 'ContactPrénom'))
        self.champ_telephone_contact.delete(0, tk.END)
        self.champ_telephone_contact.insert(0, db.get_client_info(self.client, 'ContactTeléphone'))
        page_infos_garde.choix_recup.delete(0, tk.END)
        page_infos_garde.choix_recup.set(db.get_client_info(self.client, 'choix_cle'))
        page_infos_garde.tmp_trajet_champ.delete(0, tk.END)
        page_infos_garde.tmp_trajet_champ.insert(0, db.get_client_info(self.client, 'tmp_trajet'))
                    
        for animal in db.get_liste_animaux_client(self.client):
            self.ajouter_onglet(False, animal) #on créé les onglet au nom des animaux
            for animal in self.animaux_widgets: #on boucle sur les onglets créé pour remplir ceux corespondant a notre csv
                #CREATION ONGLET ANIMAL
                w = self.animaux_widgets[animal]
                nom_animal = animal
                
                champ_espece = w["espece"]
                champ_sexe = w["sexe"]
                champ_nom = w["nom"]
                champ_sterilise_var = w["sterilise_var"]
                champ_date_naissance = w["date_naissance"]
                champ_caractere = w["caractere"]
                champ_nourriture = w["nourriture"]
                champ_besoin = w["besoin"]
                
                #REMPLISSAGE DES VALEURS    
                champ_espece.delete(0, tk.END) #vide le champs tk 0 signifie premier caractére jusqu'a la fin tk.END
                champ_espece.insert(0, db.get_animal_info(self.client, animal, 'Espéce')) #remplis le champs tk avec la valeur de la ligne a la colonne Nom
                champ_sexe.delete(0, tk.END)
                champ_sexe.insert(0, db.get_animal_info(self.client, animal, 'Sexe'))
                champ_nom.delete(0, tk.END)
                champ_nom.insert(0, db.get_animal_info(self.client, animal, 'Nom'))
                champ_sterilise_var.set(db.get_animal_info(self.client, animal, 'Stérilisé')) #pour un boolean on set la valeur 1 ou 0
                champ_date_naissance.delete(0, tk.END)
                champ_date_naissance.insert(0, db.get_animal_info(self.client, animal, 'DateDeNaissance'))
                champ_caractere.delete(0, tk.END)
                champ_caractere.insert(0, db.get_animal_info(self.client, animal, 'Caractère'))
                champ_nourriture.delete(0, tk.END)
                champ_nourriture.insert(0, db.get_animal_info(self.client, animal, 'Nourriture'))
                champ_besoin.delete(0, tk.END)
                champ_besoin.insert(0, db.get_animal_info(self.client, animal, 'BesoinParticulier'))
                                
    # Après avoir cliquer sur suivant et selectionner un dossier la variable dossier_selectionne (chemin dossier complet) et client (nom du client) est récupéré
    def valider_formulaire(self):
        # Récupère l'instance InfosGarde depuis le controller
        page_infos_garde = self.controller.frames[InfosGarde]  
        
        #SAUVEGARDE DES DONNEES CLIENTS - liste des infos possible - Nom;Prénom;Adresse;Email;Teléphone;VetoNom;VetoAdresse;VetoTeléphone;ContactNom;ContactPrénom;ContactTeléphone;tmp_trajet;choix_cle
        db.set_client_info(self.client, "Nom", self.champ_nom_client.get())
        db.set_client_info(self.client, "Prénom", self.champ_prenom_client.get())
        db.set_client_info(self.client, "Adresse", self.champ_adresse_client.get())
        db.set_client_info(self.client, "Email", self.champ_email_client.get())
        db.set_client_info(self.client, "Teléphone", self.champ_telephone_client.get())
        db.set_client_info(self.client, "VetoNom", self.champ_nom_veto.get())
        db.set_client_info(self.client, "VetoAdresse", self.champ_adresse_veto.get())
        db.set_client_info(self.client, "VetoTeléphone", self.champ_telephone_veto.get())
        db.set_client_info(self.client, "ContactNom", self.champ_nom_contact.get())
        db.set_client_info(self.client, "ContactPrénom", self.champ_prenom_contact.get())
        db.set_client_info(self.client, "ContactTeléphone", self.champ_telephone_contact.get())
        db.set_client_info(self.client, "tmp_trajet", page_infos_garde.tmp_trajet_champ.get())
        db.set_client_info(self.client, "choix_cle", page_infos_garde.choix_recup.get())
        
        #SAUVEGARDE DES DONNEES ANIMAUX - liste des infos possible - Espéce;Sexe;Nom;Stérilisé;DateDeNaissance;Caractère;Nourriture;BesoinParticulier /!\ a la casse
        for animal in self.animaux_widgets:
            w = self.animaux_widgets[animal]
                        
            db.set_animal_info(self.client, animal, "Espéce", w["espece"].get()) 
            db.set_animal_info(self.client, animal, "Sexe", w["sexe"].get())
            db.set_animal_info(self.client, animal, "Nom", w["nom"].get())
            db.set_animal_info(self.client, animal, "Stérilisé", w["sterilise_var"].get())
            db.set_animal_info(self.client, animal, "DateDeNaissance", w["date_naissance"].get())
            db.set_animal_info(self.client, animal, "Caractère", w["caractere"].get())
            db.set_animal_info(self.client, animal, "Nourriture", w["nourriture"].get())
            db.set_animal_info(self.client, animal, "BesoinParticulier", w["besoin"].get())

        messagebox.showinfo("Données enregistrées", f"Client: {db.get_client_info(self.client, 'Nom')} {db.get_client_info(self.client, 'Prénom')} sauvegardé")
        
    def ajouter_onglet(self, new, animal): #renvoi new = true ou false si besoin de créer un nouvel animal ou pas et le nom de l'animal (lié au csv)
        self.nbr_animaux +=1 #incremente le nbrs d'animaux
        if new:
            self.nom_nouveau = simpledialog.askstring("Nouvel animal", "Nom de l'animal :")
        else:
            self.nom_nouveau = animal

        # Création de l'onglet
        onglet = ttk.Frame(self.notebook)
        self.notebook.add(onglet, text=self.nom_nouveau)

        # Widgets de saisie
        widgets = {}

        tk.Label(onglet, text="Espèce").grid(row=0, column=1, padx=10, pady=5, sticky="e")
        widgets["espece"] = tk.Entry(onglet, width=30)
        widgets["espece"].grid(row=0, column=2, sticky="e")

        tk.Label(onglet, text="Sexe (M ou F)").grid(row=0, column=3, padx=10, pady=5, sticky="e")
        widgets["sexe"] = tk.Entry(onglet, width=30)
        widgets["sexe"].grid(row=0, column=4, sticky="e")

        tk.Label(onglet, text="Nom").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        widgets["nom"] = tk.Entry(onglet, width=30)
        widgets["nom"].grid(row=1, column=2, sticky="e")

        widgets["sterilise_var"] = tk.IntVar()
        widgets["sterilise_checkbox"] = tk.Checkbutton(onglet, text="Animal stérilisé", variable=widgets["sterilise_var"])
        widgets["sterilise_checkbox"].grid(row=1, column=4, sticky="w")

        tk.Label(onglet, text="Date de naissance").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        widgets["date_naissance"] = DateEntry(onglet, date_pattern='dd/mm/yyyy')
        widgets["date_naissance"].grid(row=2, column=2, sticky="w")
        
        #tk.Label(onglet, text="Date de naissance").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        #widgets["date_naissance"] = tk.Entry(onglet, width=30)
        #widgets["date_naissance"].grid(row=2, column=2, sticky="w")

        tk.Label(onglet, text="Caractère").grid(row=3, column=1, padx=10, pady=5, sticky="e")
        widgets["caractere"] = tk.Entry(onglet, width=70)
        widgets["caractere"].grid(row=3, column=2, columnspan=40, sticky="w")

        tk.Label(onglet, text="Nourriture").grid(row=4, column=1, padx=10, pady=5, sticky="e")
        widgets["nourriture"] = tk.Entry(onglet, width=70)
        widgets["nourriture"].grid(row=4, column=2, columnspan=40, sticky="w")

        tk.Label(onglet, text="Besoin particulier").grid(row=5, column=1, padx=10, pady=5, sticky="e")
        widgets["besoin"] = tk.Entry(onglet, width=70)
        widgets["besoin"].grid(row=5, column=2, columnspan=40, sticky="w")

        # Espacement
        tk.Label(onglet, text="").grid(row=0, column=6, padx=20, pady=5, sticky="e")
        tk.Label(onglet, text="").grid(row=0, column=0, padx=20, pady=5, sticky="w")

        self.notebook.select(self.notebook.index("end") - 1)

        # Sauvegarder les widgets pour cet animal
        self.animaux_widgets[self.nom_nouveau] = widgets
        
        #CREATION DB NOUVEL ANIMAL
        if new == True:
            db.create_animal(self.client, self.nom_nouveau)

        

    def supprimer_onglet(self):
        self.reponse = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir continuer ?")
        if self.reponse:
            
            self.onglet_actif = self.notebook.index(self.notebook.select())
            nom_onglet = self.notebook.tab(self.onglet_actif, option='text')
            success, message = db.delete_animal(self.client, nom_onglet)
            if success:
                self.notebook.forget(self.onglet_actif)
                self.nbr_animaux -=1 #on retire un animal de la variable
                messagebox.showinfo("Succès", message)
            else:
                messagebox.showwarning("Erreur", message)

    def verifier_bouton_supprimer(self, event=None):
        self.onglet_actif = self.notebook.index(self.notebook.select())
        nom_onglet = self.notebook.tab(self.onglet_actif, option='text')
        
        if nom_onglet == "Infos client" or nom_onglet == "Infos veto" or nom_onglet == "Infos contact urgence":
            self.btn_supprimer.config(state="disabled")  # bouton grisé
        else:
            self.btn_supprimer.config(state="normal")    # bouton actif
            
    def next_onglet(self):
        self.controller.show_frame(InfosGarde)


class InfosGarde(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.onglet_infoGarde = ttk.Frame(self.notebook)
        self.onglet_facturation = ttk.Frame(self.notebook)
        self.onglet_production_doc = ttk.Frame(self.notebook)
        
        self.notebook.add(self.onglet_infoGarde, text="Infos Garde")
        self.notebook.add(self.onglet_facturation, text="Infos Tarification")
        self.notebook.add(self.onglet_production_doc, text="Production de document")
        
        self.widgets_garde = [] #créer une variable liste pour contenir les champs date de garde + liste (matin/apres midi/soir)
        self.nbrs_de_garde = 0 #initialise une variable nbrs de gardes
        
        # Créer un conteneur pour les boutons Enregistrer et Retour
        bouton_frame = tk.Frame(self)
        bouton_frame.pack(pady=10)
        
        # Bouton Retour
        self.bouton_retour = tk.Button(bouton_frame, text="Retour", command=controller.go_back)
        self.bouton_retour.pack(side='left', padx=5)

        # Bouton Enregistrer
        self.bouton_enregistrer = tk.Button(bouton_frame, text="Enregistrer", command=lambda: self.sauvegarder_infos())
        self.bouton_enregistrer.pack(side='left', padx=5)
        
        #Champ date debut et fin de la garde
        
        tk.Label(self.onglet_infoGarde, text="Date de debut").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.date_debut = DateEntry(self.onglet_infoGarde, date_pattern='dd/mm/yyyy')
        self.date_debut.grid(row=1, column=2, sticky="w")
        
        tk.Label(self.onglet_infoGarde, text="Date de fin").grid(row=1, column=3, padx=10, pady=5, sticky="e")
        self.date_fin = DateEntry(self.onglet_infoGarde, date_pattern='dd/mm/yyyy')
        self.date_fin.grid(row=1, column=4, sticky="w")
        
        #Champ date remise de clé
        
        tk.Label(self.onglet_infoGarde, text="Date de remise des clés a la PetSitter").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.date_remise_cles = DateEntry(self.onglet_infoGarde, date_pattern='dd/mm/yyyy')
        self.date_remise_cles.grid(row=2, column=2, sticky="w")
        
        tk.Label(self.onglet_infoGarde, text="Date de récupération des clés").grid(row=3, column=1, padx=10, pady=5, sticky="e")
        self.date_recup_cles = DateEntry(self.onglet_infoGarde, date_pattern='dd/mm/yyyy')
        self.date_recup_cles.grid(row=3, column=2, sticky="w")
        
        #champs listes
        self.choix_recup = ttk.Combobox(self.onglet_infoGarde, state="readonly")
        self.choix_recup.grid(row=3, column=3, sticky="e")
        self.choix_recup['values'] = ["Dans la boite au lettre"] + ["Chez la PetSitter"]
        self.choix_recup.set('Dans la boite au lettre')
        
        self.detail_date_bool_var = tk.IntVar() #stock la variable a 0 ou 1
        self.detail_date_bool = tk.Checkbutton(self.onglet_infoGarde, text="Détailler les dates", variable=self.detail_date_bool_var, command=self.detail_date) #interface graphique mettant a jour la variable quand coché ou non
        self.detail_date_bool.grid(row=4, column=2, sticky="w")
        
        # Bouton ajouter date
        self.bouton_ajouter_date = tk.Button(self.onglet_infoGarde, text="Ajouter une date", command=self.ajouter_date_garde)
        self.bouton_ajouter_date.grid(row=4, column=4, sticky="w")
        self.bouton_ajouter_date.grid_remove() #on l'efface tant que la coche détail est pas vrai
        
        
        self.last_fixed_row = 4 #référence le dernier numéro de ligne utilisé
        self.row_counter = self.last_fixed_row #variable qu'on va pouvoir manipuler
        
        #entry de l'onglet tarification
        
        #nbrs de garde
        tk.Label(self.onglet_facturation, text="Nbrs de gardes").grid(row=1, column=1, padx=10, pady=5, sticky="e")
        self.nbrs_de_garde_champ = tk.Entry(self.onglet_facturation, width=5)
        self.nbrs_de_garde_champ.grid(row=1, column=2)
        
        #temps de trajet
        tk.Label(self.onglet_facturation, text="Temps de trajet").grid(row=1, column=4, padx=10, pady=5, sticky="e")
        self.tmp_trajet_champ = tk.Entry(self.onglet_facturation, width=5)
        self.tmp_trajet_champ.grid(row=1, column=5)
        
        #prix essence trajet
        tk.Label(self.onglet_facturation, text="Prix essence trajet").grid(row=2, column=1, padx=10, pady=5, sticky="e")
        self.prix_essence_trajet_champ = tk.Entry(self.onglet_facturation, width=5)
        self.prix_essence_trajet_champ.grid(row=2, column=2)
        
        #Temps de garde total
        tk.Label(self.onglet_facturation, text="Temps de garde total").grid(row=2, column=4, padx=10, pady=5, sticky="e")
        self.tmp_garde_totl_champ = tk.Entry(self.onglet_facturation, width=5)
        self.tmp_garde_totl_champ.grid(row=2, column=5)
        
        #Prix Horaire de la garde
        tk.Label(self.onglet_facturation, text="Prix horaire garde").grid(row=3, column=1, padx=10, pady=5, sticky="e")
        self.prix_horraire_champ = tk.Entry(self.onglet_facturation, width=5)
        self.prix_horraire_champ.grid(row=3, column=2)
        self.prix_horraire_champ.insert(0, '16')
        
        self.bouton_calculer = tk.Button(self.onglet_facturation, text="Calculer", command=lambda: self.calculer())
        self.bouton_calculer.grid(row=3, column=4, padx=25 ,sticky="e")
        
        self.results_text = tk.Text(self.onglet_facturation, height=14, width=80)
        self.results_text.grid(row=4, column=1, columnspan=2000)
        
        #bouton lien mappy https://fr.mappy.com/itineraire#/recherche/49%20Rue%20Pierre%20Blard%2C%2044800%20Saint-Herblain/49%20Rue%20Pierre%20Blard%2C%2044800%20Saint-Herblain
        self.bouton_map = tk.Button(self.onglet_facturation, text="Mappy", command=lambda: self.ouvrir_lien_mappy())
        self.bouton_map.grid(row=1, column=6, pady=5, padx=25,sticky="e")
        
        #bouton lien eclerc essence https://www.cartecarburant.leclerc/stations-service/pays-loire/loire-atlantique/saint-herblain/eleclerc-saint-herblain
        self.bouton_essence = tk.Button(self.onglet_facturation, text="Prix Gazole", command=lambda: self.ouvrir_lien_essence())
        self.bouton_essence.grid(row=2, column=6, pady=5, padx=25,sticky="e")
        
        #entry de l'onglet production
        
        #bouton ouvrir dossier client doc
        self.bouton_dossier_client = tk.Button(self.onglet_production_doc, text="Ouvrir le dossier client", command=lambda: self.open_dir(db.get_client_upload(self.client)))
        self.bouton_dossier_client.grid(row=2, column=2, pady=50, padx=25,sticky="e")
        
        #bouton generer contrat
        self.bouton_contrat = tk.Button(self.onglet_production_doc, text="Génerer le contrat", command=lambda: self.upload_contrat("Contrat_de_Pet_sitting.pdf"))
        self.bouton_contrat.grid(row=1, column=1, pady=25, padx=25)
        
        #bouton generer devis
        self.bouton_devis = tk.Button(self.onglet_production_doc, text="Génerer le devis", command=lambda: self.upload_contrat("Devis.pdf"))
        self.bouton_devis.grid(row=1, column=2, pady=25, padx=25)
        
        #bouton generer facture
        self.bouton_facture = tk.Button(self.onglet_production_doc, text="Génerer la facture", command=lambda: self.upload_contrat("Facture.pdf"))
        self.bouton_facture.grid(row=1, column=3, pady=25, padx=25)
        
        #bouton generer contrat d'abo
        self.bouton_contrat_abo = tk.Button(self.onglet_production_doc, text="Génerer le contrat d'abo", command=lambda: self.upload_contrat("Contrat_d'abonnement_de_Pet_sitting.pdf"))
        self.bouton_contrat_abo.grid(row=1, column=5, pady=25, padx=25)
        
        #bouton generer facture acompte
        self.bouton_facture_acompte = tk.Button(self.onglet_production_doc, text="Génerer la facture acompte", command=lambda: self.upload_contrat("Facture_acompte.pdf"))
        self.bouton_facture_acompte.grid(row=1, column=4, pady=25, padx=25)
        

    def detail_date(self):
        if self.detail_date_bool_var.get() == 1:
            self.afficher_date_garde(True)
            self.bouton_ajouter_date.grid()
        else:
            self.afficher_date_garde(False)
            self.bouton_ajouter_date.grid_remove()
            
    def ajouter_date_garde(self):
        self.nbrs_de_garde += 1 #on augmente le counter nbrs de garde a chaque ajout
        self.row_counter += 1 #on ajoute 1 pour ce possitioner a la prochaine ligne
        
        label = tk.Label(self.onglet_infoGarde, text=f"Garde {self.nbrs_de_garde} :")
        label.grid(row=self.row_counter, column=1, padx=10, pady=5, sticky="e")
        
        date_garde = DateEntry(self.onglet_infoGarde, date_pattern='dd/mm/yyyy')
        date_garde.grid(row=self.row_counter, column=2, sticky="w")
        
        #champs listes
        choix_horraire = ttk.Combobox(self.onglet_infoGarde, state="readonly")
        choix_horraire.grid(row=self.row_counter, column=3, sticky="e")
        choix_horraire['values'] = ["matin"] + ["après-midi"] + ["soir"]
        choix_horraire.set('matin')
        
        btn_suppr = tk.Button(self.onglet_infoGarde, text="X", command=lambda: self.supprimer_garde(label))
        btn_suppr.grid(row=self.row_counter, column=4, padx=5, sticky="w")
        
        self.widgets_garde.append({"label": label,"date_entry": date_garde,"moment": choix_horraire,"btn_suppr": btn_suppr}) #on rajoute au widgets
        date_garde.bind("<<DateEntrySelected>>", lambda e: self.trier_gardes())
        
    def afficher_date_garde(self, afficher): #afficher ou masquer afficher = True quand on doit afficher sinon on masque
        for widget in self.widgets_garde:
            if afficher and self.nbrs_de_garde > 0:
                widget["label"].grid()
                widget["date_entry"].grid()
                widget["moment"].grid()
                widget["btn_suppr"].grid()
            else:
                widget["label"].grid_remove()
                widget["date_entry"].grid_remove()
                widget["moment"].grid_remove()
                widget["btn_suppr"].grid_remove()
                    
    def supprimer_garde(self, label_to_delete):
        new_widgets = []
        self.nbrs_de_garde -= 1

        for widget in self.widgets_garde:
            if widget["label"] == label_to_delete:
                widget["label"].destroy()
                widget["date_entry"].destroy()
                widget["moment"].destroy()
                widget["btn_suppr"].destroy()
            else:
                new_widgets.append(widget)

        self.widgets_garde = new_widgets

        # Réorganisation
        for idx, widget in enumerate(self.widgets_garde, 1):
            row = self.last_fixed_row + idx

            widget["label"].config(text=f"Garde {idx} :")
            widget["label"].grid(row=row, column=1, padx=10, pady=5, sticky="e")
            widget["date_entry"].grid(row=row, column=2, sticky="w")
            widget["moment"].grid(row=row, column=3, sticky="w")
            widget["btn_suppr"].grid(row=row, column=4, padx=5, sticky="w")

            self.row_counter = row

    def trier_gardes(self):
        def get_date(widget):
            date_str = widget["date_entry"].get()
            try:
                return datetime.strptime(date_str, "%d/%m/%Y")
            except:
                return datetime.max  # si vide > va à la fin

        #tri des widgets
        self.widgets_garde.sort(key=get_date)

        #réorganisation visuelle
        for idx, widget in enumerate(self.widgets_garde, 1):
            row = self.last_fixed_row + idx

            widget["label"].config(text=f"Garde {idx} :")
            widget["label"].grid(row=row, column=1, padx=10, pady=5, sticky="e")
            widget["date_entry"].grid(row=row, column=2, sticky="w")
            widget["moment"].grid(row=row, column=3, sticky="w")
            widget["btn_suppr"].grid(row=row, column=4, padx=5, sticky="w")

            self.row_counter = row
    
    def to_decimal(self, val): #permet a l'usager de saisir , ou .
        val = val.strip().replace(',', '.')
        return Decimal(val)
    
            
    def calculer(self):        
        # Récupération des valeurs en decimal
        try:
            tmp_garde_totl = self.to_decimal(self.tmp_garde_totl_champ.get())
            prix_horraire = self.to_decimal(self.prix_horraire_champ.get())
            nbrs_de_garde = self.to_decimal(self.nbrs_de_garde_champ.get())
            tmp_trajet = self.to_decimal(self.tmp_trajet_champ.get())
            prix_essence_trajet = self.to_decimal(self.prix_essence_trajet_champ.get())
            
            #envoi des valeurs a l'outil de calcul
            success, message, cout_trajet, total_prix_garde_no_trajet, total_prix_trajet_no_essence, total_prix_essence_ac_urssaf, total_prix_trajet, prix_avance_garde, prix_reste_garde, total_prix_garde, tarif_15, tarif_30, tarif_45, tarif_60 = utils.calculer(tmp_garde_totl, prix_horraire, nbrs_de_garde, tmp_trajet, prix_essence_trajet) #elem a tranmettre : tmp_garde_totl, prix_horraire, nbrs_de_garde, tmp_trajet, prix_essence_trajet
            if success:
                # Affichage
                self.results_text.delete("1.0", tk.END)

                self.results_text.insert(tk.END, f"prix 15 min : {tarif_15:.2f} €\n")
                self.results_text.insert(tk.END, f"prix 30 min : {tarif_30:.2f} €\n")
                self.results_text.insert(tk.END, f"prix 45 min : {tarif_45:.2f} €\n")
                self.results_text.insert(tk.END, f"prix 60 min : {tarif_60:.2f} €\n\n")

                self.results_text.insert(tk.END, f"Cout du trajet par garde (avec URSSAF): {cout_trajet:.2f} €\n")
                self.results_text.insert(tk.END, f"Total garde (hors trajet) : {total_prix_garde_no_trajet:.2f} €\n")
                self.results_text.insert(tk.END, f"Total trajet (hors essence) : {total_prix_trajet_no_essence:.2f} €\n")
                self.results_text.insert(tk.END, f"Prix essence avec URSSAF : {total_prix_essence_ac_urssaf:.2f} €\n")
                self.results_text.insert(tk.END, f"Total trajet : {total_prix_trajet:.2f} €\n")
                self.results_text.insert(tk.END, f"Prix de l'avance (25%) : {prix_avance_garde:.2f} €\n")
                self.results_text.insert(tk.END, f"Reste à payer : {prix_reste_garde:.2f} €\n")
                self.results_text.insert(tk.END, f"Total : {total_prix_garde:.2f} €\n\n")
                
                #On conserve les résultat en variable pour les réutiliser si besoin pour génération doc pdf
                
                self.tarif_15 = tarif_15
                self.tarif_30 = tarif_30
                self.tarif_45 = tarif_45
                self.tarif_60 = tarif_60
                self.cout_trajet = cout_trajet
                self.total_prix_garde_no_trajet = total_prix_garde_no_trajet
                self.total_prix_trajet_no_essence = total_prix_trajet_no_essence
                self.total_prix_essence_ac_urssaf = total_prix_essence_ac_urssaf
                self.total_prix_trajet = total_prix_trajet
                self.prix_avance_garde = prix_avance_garde
                self.prix_reste_garde = prix_reste_garde
                self.total_prix_garde = total_prix_garde
            else:
                messagebox.showerror("erreur", message)
        except InvalidOperation:
            messagebox.showerror("erreur", "Mauvaise saisie")
        
            
    def ouvrir_lien_essence(self):
        webbrowser.open("https://www.cartecarburant.leclerc/stations-service/pays-loire/loire-atlantique/saint-herblain/eleclerc-saint-herblain")
        
    def ouvrir_lien_mappy(self):
        webbrowser.open("https://fr.mappy.com/itineraire#/recherche/49%20Rue%20Pierre%20Blard%2C%2044800%20Saint-Herblain/49%20Rue%20Pierre%20Blard%2C%2044800%20Saint-Herblain")
        
    def sauvegarder_infos(self):
        # Appelle directement la méthode valider_formulaire de InfosClients
        self.page_infos_clients.valider_formulaire()
        
    def on_show(self):
        # Récupère l'instance InfosClients depuis le controller
        self.page_infos_clients = self.controller.frames[InfosClients]
        #récupére le nbr d'animaux
        self.nbr_animaux = self.page_infos_clients.nbr_animaux
        
        self.client = self.controller.dossier_choisi 
        
    def upload_contrat(self, type_fichier):
        date_du_jour = datetime.now().strftime('%d/%m/%Y')
        animaux_count = 0 #pour compter le numéro de l'animal ou on est
        data_animaux = {} #créé un dictionnaire pour compléter le pdf plus tard
        contact_urgence = f'{self.page_infos_clients.champ_nom_contact.get().upper()} {self.page_infos_clients.champ_prenom_contact.get()} {self.page_infos_clients.champ_telephone_contact.get()}' #concatener pour donner exemple: NOM Prenom 07 80 80 80 80
        date_de_garde = [] #champ liste
        if self.choix_recup.get() == 'Dans la boite au lettre':
            recup_bal = PdfName('Yes') #pdf ne prend pas True ou False, obligé de renvoyer ce genre de valeur pour cocher/afficher case coché
            recup_chez_petsitter = PdfName('Off')
        else:
            recup_bal = PdfName('Off')
            recup_chez_petsitter = PdfName('Yes')
        
        for w in self.widgets_garde:
            date = w["date_entry"].get()
            creneau = w["moment"].get() #matin - apres midi ou soir
            date_and_creneau = f'{date} - {creneau}'
            date_de_garde.append(date_and_creneau)
            
        txt_date_de_garde = ', '.join(date_de_garde) #permet de joindre séparé d'une , chaque éléments dans la liste
        
        for animal in self.page_infos_clients.animaux_widgets:    
            animaux_count += 1 
            nbr = animaux_count
            w = self.page_infos_clients.animaux_widgets[animal]
            nom_animal = animal #nom de l'onglet
                        
            champ_espece = w["espece"].get()
            champ_sexe = w["sexe"].get()
            champ_nom = w["nom"].get()
            champ_sterilise_var = w["sterilise_var"].get()
            champ_date_naissance = w["date_naissance"].get()
            champ_caractere = w["caractere"].get()
            champ_nourriture = w["nourriture"].get()
            champ_besoin = w["besoin"].get()
            
            if champ_sterilise_var == 0:
                sterilise = 'N'
            else:
                sterilise = 'O'
            data_temp = {
            f'espece{nbr}': champ_espece,
            f'sexe{nbr}': champ_sexe,
            f'nom_animal{nbr}': champ_nom,
            f'sterilise{nbr}': sterilise,
            f'date_naissance_animal{nbr}': champ_date_naissance,
            f'caractere_animal{nbr}': champ_caractere,
            f'nourriture_animal{nbr}': champ_nourriture,
            f'besoin_animal{nbr}': champ_besoin
            }
            data_animaux.update(data_temp) #on rajoute les données dans le dictionaire data_animaux
        
        data = {
        'nom_proprio': self.page_infos_clients.champ_nom_client.get(),
        'prenom_proprio': self.page_infos_clients.champ_prenom_client.get(),
        'portable_proprio': self.page_infos_clients.champ_telephone_client.get(),
        'mail_proprio': self.page_infos_clients.champ_email_client.get(),
        'addr_proprio': self.page_infos_clients.champ_adresse_client.get(),
        'nom_veto': self.page_infos_clients.champ_nom_veto.get(),
        'tel_veto': self.page_infos_clients.champ_telephone_veto.get(),
        'addr_veto': self.page_infos_clients.champ_adresse_veto.get(),
        'contact_urgence': contact_urgence,
        'date_debut_garde': self.date_debut.get(),
        'date_fin_garde': self.date_fin.get(),
        'dates_de_passage': txt_date_de_garde,
        'date_cle_r_petsitter': self.date_remise_cles.get(),
        'date_cle_r_proprio': self.date_recup_cles.get(),
        'cle_r_bal': recup_bal,
        'cle_r_chez_petsitter': recup_chez_petsitter,
        'date_production_doc': date_du_jour,
        }

        try: #on ajoute les valeurs de tarif dans le date(s'il y en a)
            data.update({
                'total_temps_garde': self.tmp_garde_totl_champ.get(),
                'prix_total_garde': f"{self.total_prix_garde:.2f}",
                'prix_reste_garde': f"{self.prix_reste_garde:.2f}",
                'prix_avance_garde': f"{self.prix_avance_garde:.2f}",
                'prix15': f"{self.tarif_15:.2f}",
                'prix30': f"{self.tarif_30:.2f}",
                'prix45': f"{self.tarif_45:.2f}",
                'prix60': f"{self.tarif_60:.2f}",
            })
        except Exception:
            messagebox.showwarning("Attention", "Aucun tarif calculé")
            
        data.update(data_animaux) #on rajoute les infos des animaux
        
        success, message = utils.fill_pdf(self.client, type_fichier, data) #On envoi le nom du client, le fichier qu'on souhaite générer et l'ensemble des données pour la création d'un pdf
        
        if success:
            messagebox.showinfo("Création réussi", message)
        else:
            messagebox.showerror("ERREUR", message)
        
    
    def open_dir(self, chemin):
        os.startfile(chemin)
if __name__ == "__main__":
    app = Application()
    app.mainloop()
