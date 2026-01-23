# backend/scheduler_entry.py
import os
import logging

# Importa el scheduler real
from scheduler import scheduler_instance

if __name__ == "__main__":
    # Hard safety: nunca ejecutar uvicorn aquí
    logging.basicConfig(level=logging.INFO)
    scheduler_instance.run()
