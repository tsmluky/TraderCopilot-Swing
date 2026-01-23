import sys
import os
import json

# Add backend to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


def export_openapi():
    print("Exporting OpenAPI Schema...")
    openapi_data = app.openapi()

    # Ensure OUTPUT dir exists
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DATA_ROOM", "api"
    )
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "openapi.json")

    with open(output_path, "w") as f:
        json.dump(openapi_data, f, indent=2)

    print(f"Successfully exported to {output_path}")


if __name__ == "__main__":
    export_openapi()
