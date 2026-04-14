FROM python:3.11-slim

#ajoute curl
RUN apt-get update && apt-get install -y curl

#Définit le répertoire de travail (créé s'il n'existe pas)
WORKDIR /mon_app

#Copie tout le projet local dans /mon_app
COPY . /mon_app

# Installe les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt 

# Indique que l'application écoute sur le port 5000
EXPOSE 5000

# Se place dans le dossier contenant web.py
WORKDIR /mon_app/app

# Lance l'application
CMD ["python", "web.py"]