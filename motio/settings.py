from pydantic import BaseModel, Field
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent / "settings.json"

class Settings(BaseModel):
    face_tracking: bool = True
    smooth_tracking: bool = True
    tracking_smoothing_alpha: float = Field(default=0.3, ge=0.0, le=1.0)

    low_light_correction: bool = True
    low_light_threshold: float = Field(default=0.4, ge=0.0, le=1.0)

    background_blur: bool = False
    blur_strength: int = Field(default=15, ge=1, le=51)

    def save(self, path: Path = SETTINGS_PATH):
        path.write_text(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: Path = SETTINGS_PATH):
        if path.exists():
            return cls.model_validate_json(path.read_text())
        return cls()

settings = Settings.load()