"""Put the skill scripts on the import path and share test paths."""
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL / "scripts"
ASSETS = SKILL / "assets"
FIXTURE = ASSETS / "minimal-extraction.yaml"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
