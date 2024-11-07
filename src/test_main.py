import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Trip
import os

# Test database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Create the engine and sessionmaker for the test database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override for the database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Create the tables in the test database
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def setup_db():
    # Create a new session for the test
    db = TestingSessionLocal()
    
    # Create a test trip record
    trip = Trip(name="Test Trip", description="Test Description", joiner_total_count=5)
    db.add(trip)
    db.commit()
    db.refresh(trip)
    
    yield db  # This will be accessible in the tests
    
    db.query(Trip).delete()  # Clean up after the test

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Fast Api Exam api v1"}

def test_all_trips(setup_db):
    response = client.get("/trip")
    assert response.status_code == 200
    assert len(response.json()) > 0  # Assuming there is at least one trip in the database

def test_show_trip(setup_db):
    # Fetch a trip from the database
    trip = setup_db.query(Trip).first()
    response = client.get(f"/trip/{trip.id}")
    assert response.status_code == 200
    assert response.json()["name"] == trip.name

def test_create_trip():
    new_trip = {
        "name": "New Trip",
        "description": "Description of new trip",
        "joiner_total_count": 10
    }
    response = client.post("/trip", json=new_trip)
    assert response.status_code == 201
    assert response.json()["name"] == new_trip["name"]

def test_update_trip(setup_db):
    trip = setup_db.query(Trip).first()
    updated_trip = {
        "name": "Updated Trip",
        "description": "Updated Description",
        "joiner_total_count": 15
    }
    response = client.put(f"/trip/{trip.id}", json=updated_trip)
    assert response.status_code == 202
    assert response.json()["detail"] == "Trip updated."

def test_delete_trip(setup_db):
    trip = setup_db.query(Trip).first()
    response = client.delete(f"/trip/{trip.id}")
    assert response.status_code == 202
    assert response.json() == {"detail": "Trip deleted"}

import asyncio

# Workaround for Windows asyncio issue
if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())