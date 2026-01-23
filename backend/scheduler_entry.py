# backend/scheduler_entry.py
import logging
from scheduler import scheduler_instance

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler_instance.run()
