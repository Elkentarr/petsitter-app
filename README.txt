#PetSitter Management Tool

## Description
Application pour auto-entreprise de petsitting permettant :
- la gestion des clients et animaux
- le calcul des coûts de prestation
- la génération de documents (contrats, devis, factures)

Le projet existe en deux versions :
- Version Desktop (Tkinter)
- Version Web (Flask - en cours de développement)


## Prérequis

- Python 3.10+
- pip
- (Linux uniquement) python3-tk pour Tkinter
- Docker (optionnel)


## Technologies utilisées

- Python
- Tkinter (interface desktop)
- Flask (version web)
- CSV (stockage local)
- Docker


## Installation locale

cmd
pip install -r requirements.txt

#Desktop

python ./app/main.py

Ou pour une version .exe
pyinstaller --onefile --noconsole main.py

#WEB - Pour rappel pas encore terminé
python ./app/web.py

## DOCKER

# Build de l'image
cmd
docker build -t petsitter-app .

# Lancement
cmd
docker run -p 5000:5000 petsitter-app