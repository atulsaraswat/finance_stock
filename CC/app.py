import json
from pathlib import Path

from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILE = BASE_DIR / "profile.json"
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"

app = Flask(__name__, template_folder="templates")


def load_profile(path: Path):
    if not path.exists():
        return {}
    if path.suffix.lower() in {".yaml", ".yml"}:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def load_requirements(path: Path):
    if not path.exists():
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line and not line.startswith("#")]


@app.route("/")
def index():
    profile = load_profile(DEFAULT_PROFILE)
    requirements = load_requirements(REQUIREMENTS_FILE)
    return render_template(
        "index.html",
        profile=profile,
        profile_path=DEFAULT_PROFILE.name,
        requirements=requirements,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
