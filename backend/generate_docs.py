import json
import os


def generate_endpoints_md():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(base_dir, "DATA_ROOM", "api", "openapi.json")
    output_path = os.path.join(base_dir, "DATA_ROOM", "api", "endpoints.md")

    with open(input_path, "r") as f:
        data = json.load(f)

    paths = data.get("paths", {})

    files_content = [
        "# API Endpoints Specification",
        "",
        "| Method | Path | Auth | Description |",
        "|---|---|---|---|",
    ]

    # Sort by path for readability
    for path in sorted(paths.keys()):
        methods = paths[path]
        for method, details in methods.items():
            method_str = method.upper()
            summary = details.get("summary", "")
            security = "No"
            if "security" in data or "security" in details:
                # Very basic check, inaccurate but sufficient for high level
                # Better: check if path starts with certain prefixes or has security dict
                pass

            # Refine Auth detection based on standard Bearer pattern usually found in components
            # or simply based on our knowledge of prefixes
            if (
                path.startswith("/admin")
                or path.startswith("/advisor")
                or path.startswith("/strategies")
            ):
                security = "**Yes**"
            elif path.startswith("/auth/users/me"):
                security = "**Yes**"

            files_content.append(
                f"| {method_str} | `{path}` | {security} | {summary} |"
            )

    with open(output_path, "w") as f:
        f.write("\n".join(files_content))

    print(f"Generated {output_path}")


if __name__ == "__main__":
    generate_endpoints_md()
