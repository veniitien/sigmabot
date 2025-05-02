from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import os

Base = declarative_base()

# Association tables
team_members = Table('team_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('team_id', Integer, ForeignKey('teams.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pages = relationship("Page", back_populates="owner")
    owned_teams = relationship("Team", back_populates="owner")
    member_teams = relationship("Team", secondary=team_members, back_populates="members")
    code_files = relationship("CodeFile", back_populates="owner")

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="owned_teams")
    members = relationship("User", secondary=team_members, back_populates="member_teams")
    pages = relationship("Page", back_populates="team")

class Page(Base):
    __tablename__ = 'pages'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    is_private = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="pages")
    team = relationship("Team", back_populates="pages")
    todos = relationship("Todo", back_populates="page", cascade="all, delete-orphan")

class Todo(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True)
    content = Column(String)
    is_completed = Column(Boolean, default=False)
    page_id = Column(Integer, ForeignKey('pages.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    page = relationship("Page", back_populates="todos")

class CodeFile(Base):
    __tablename__ = 'code_files'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(String)
    language = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    is_private = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="code_files")

# Create database and tables
def init_db():
    engine = create_engine('sqlite:///app.db')
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db() 