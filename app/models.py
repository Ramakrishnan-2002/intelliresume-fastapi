from .database import Base
from sqlalchemy import Column,Integer,String,TIMESTAMP,func



class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,unique=True,nullable=False)
    password=Column(String,nullable=False)
    name=Column(String,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=True,server_default=func.now())
