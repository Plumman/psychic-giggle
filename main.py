from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import models
import schemas
from database import engine, SessionLocal, test_connection
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)
test_connection()  # Call the test function to execute the query


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Fast Api Exam api v1"}


@app.get("/trip", status_code=status.HTTP_200_OK, response_model=List[schemas.ShowTrip])
async def all(limit=10, sort='latest', db: Session = Depends(get_db)):
    trip = db.query(models.Trip).limit(limit).all()
    return trip


@app.get("/trip/{id}", response_model=schemas.ShowTrip)
async def show(id: int, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Trip not found.')
    return trip


@app.post("/trip", status_code=status.HTTP_201_CREATED)
async def create(request: schemas.Trip, db: Session = Depends(get_db)):
    new_trip = models.Trip(name=request.name, description=request.description,
                           joiner_total_count=request.joiner_total_count)
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip


@app.delete('/trip/{id}', status_code=status.HTTP_202_ACCEPTED)
async def delete(id, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == id)
    if not trip.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Trip not found')
    trip.delete()
    db.commit()
    return {'detail': 'Trip deleted'}


@app.put("/trip/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update(id, request: schemas.Trip, db: Session = Depends(get_db)):
    trip = db.query(models.Trip).filter(models.Trip.id == id)
    if not trip.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Trip not found')
    print(request)
    trip.update(dict(request))
    db.commit()
    return {'detail': 'Trip updated.'}
