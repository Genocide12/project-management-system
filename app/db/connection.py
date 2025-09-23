from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.task import Task

class Database:
    def __init__(self, url: str):
        self.engine = create_engine(url, future=True)
        self.Session = sessionmaker(bind=self.engine, future=True)
    def ensure_initialized(self):
        Base.metadata.create_all(self.engine)
    def session(self):
        return self.Session()
