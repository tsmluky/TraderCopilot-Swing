import sys
from sqlalchemy.orm import Session
from database import SessionLocal
from models_db import Changelog
import json
from datetime import datetime

def main():
    with SessionLocal() as db:
        new_log = Changelog(
            version="1.0.3",
            date=datetime.utcnow().strftime("%B %d, %Y"),
            title="Optimización de Estrategias",
            description="Ajuste temporal en los módulos de análisis para mejorar la precisión global del sistema.",
            changes=json.dumps([
                "Temporalmente estrategias Donchian Breakout y Trend Surfer SMA desactivadas (en gris) para evaluación de rendimiento."
            ]),
            type="minor"
        )
        db.add(new_log)
        db.commit()
        print("Successfully added changelog 1.0.3")

if __name__ == "__main__":
    main()
