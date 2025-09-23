from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
class Task(Base):
    __tablename__='tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'))
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32), default='todo')
    details: Mapped[str|None] = mapped_column(Text(), nullable=True)
