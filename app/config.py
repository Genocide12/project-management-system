from pydantic import BaseModel
from pathlib import Path

class Settings(BaseModel):
    database_url: str = f"sqlite:///{Path('data/db.sqlite').as_posix()}"
    locale: str = 'ru'
    backup_dir: str = 'backups'
    log_level: str = 'INFO'
    @classmethod
    def load(cls):
        Path('data').mkdir(exist_ok=True, parents=True)
        return cls()
