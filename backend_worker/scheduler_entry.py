import os
import sys

# Asegura que /backend esté en sys.path (repo root + backend)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from scheduler import scheduler_instance

if __name__ == "__main__":
    scheduler_instance.run()
