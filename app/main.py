from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/identify", response_model=schemas.IdentifyResponse)
def identify(request: schemas.IdentifyRequest, db: Session = Depends(get_db)):
    if not request.email and not request.phoneNumber:
        raise HTTPException(
            status_code=400, detail="Provide at least email or phone number."
        )

    return crud.identify_contact(db, request.email, request.phoneNumber)
