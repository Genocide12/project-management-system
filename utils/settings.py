from pathlib import Path
import json

class AppSettings:
    def __init__(self, path: Path|None=None):
        self.path = path or Path('data/app_settings.json')
        self.data = {}
        self.load()
    def load(self):
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding='utf-8'))
        else:
            self.data = {'theme':'light'}
            self.save()
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding='utf-8')
