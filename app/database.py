from typing import Annotated
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from tinydb import TinyDB



SQLALCHEMY_DATABASE_URL='sqlite:///./resume.db'


engine=create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False})
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session, Depends(get_db)]

resume_metadata=TinyDB('resume_meta.json')


