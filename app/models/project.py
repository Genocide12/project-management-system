from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
class Project(Base):
    __tablename__='projects'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str|None] = mapped_column(Text(), nullable=True)
