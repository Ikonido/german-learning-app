import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup test DB
TEST_DATABASE_URL = "sqlite:///./test_german_app.db"

# Remove existing test DB if any
if os.path.exists("./test_german_app.db"):
    try:
        os.remove("./test_german_app.db")
    except OSError:
        pass

# We override the settings DATABASE_URL before importing the app
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.main import app
from app.db.session import Base, get_db
from app.models import Word, NounDetail, VerbDetail, WordType, Gender, Auxiliary

# Create database engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Seed some words for tests
db = TestingSessionLocal()
w1 = Word(german="Haus", translation="дом", word_type=WordType.NOUN, level="A1", category="home")
db.add(w1)
db.flush()
d1 = NounDetail(word_id=w1.id, gender=Gender.DAS, plural="Häuser")
db.add(d1)

w2 = Word(german="gehen", translation="идти", word_type=WordType.VERB, level="A1", category="motion")
db.add(w2)
db.flush()
d2 = VerbDetail(word_id=w2.id, praeteritum="ging", perfekt="gegangen", auxiliary=Auxiliary.SEIN)
db.add(d2)
db.commit()
db.close()

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_and_login():
    # Register
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    
    # Register duplicate
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    
    # Login
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
    
    # Login wrong pass
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_auth_me_no_token():
    # This should return 401, not 500!
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_auth_me_valid_token():
    # Login to get token
    response = client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    token = response.json()["access_token"]
    
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_get_random_word():
    response = client.get("/vocab/random")
    assert response.status_code == 200
    assert "german" in response.json()
    assert response.json()["german"] in ["Haus", "gehen"]

def test_check_answer_noun():
    # German article + word
    response = client.post("/vocab/1/check", json={"answer": "das Haus"})
    assert response.status_code == 200
    assert response.json()["correct"] is True

    # Russian translation
    response = client.post("/vocab/1/check", json={"answer": "дом"})
    assert response.status_code == 200
    assert response.json()["correct"] is True
    
    response = client.post("/vocab/1/check", json={"answer": "wrong"})
    assert response.status_code == 200
    assert response.json()["correct"] is False

def test_check_answer_verb():
    # German past form
    response = client.post("/vocab/2/check", json={"answer": "ging"})
    assert response.status_code == 200
    assert response.json()["correct"] is True

    # German perfect form
    response = client.post("/vocab/2/check", json={"answer": "sein gegangen"})
    assert response.status_code == 200
    assert response.json()["correct"] is True

    # Russian translation
    response = client.post("/vocab/2/check", json={"answer": "идти"})
    assert response.status_code == 200
    assert response.json()["correct"] is True
