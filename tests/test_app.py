import pytest
from app.web import app #récupération app web

@pytest.fixture #creation client de test flask
def client():
    app.config['TESTING'] = True #activation du mode test flask - erreurs plus explicites
    with app.test_client() as client: #simulation navigateur GET POST
        yield client #renvoi l'objet (client) utilisable dans les tests

def test_home_page(client): #premier test - test de la route / en simulant une requête http
    response = client.get("/")
    assert response.status_code == 200 #vérifie si la page existe et pas d'erreur serveur

def test_create_client_page(client): #deuxieme test - test d'accès a la route /client/new
    response = client.get("/client/new")
    assert response.status_code == 200