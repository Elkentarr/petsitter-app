# PetSitter Management Tool

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
- nginx

## Installation locale

```bash
pip install -r requirements.txt
```

## Desktop

python ./app/main.py

Ou pour une version .exe
```bash
pyinstaller --onefile --noconsole main.py
```

## WEB - (En cours)
python ./app/web.py

Accès :
http://localhost:5000

## DOCKER WEB + NGINX

Build du conteneur :
```bash
docker-compose up --build
```

Accès :
http://localhost