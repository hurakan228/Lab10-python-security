"""Build a tiny distributable ZIP; excludes any local secrets."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
dist.mkdir(exist_ok=True)
archive = dist / "lab10-demo-app.zip"
with ZipFile(archive, "w", compression=ZIP_DEFLATED) as out:
    for filename in ("app.py", "config.py", "requirements.txt"):
        out.write(root / filename, arcname=filename)
print(f"Created {archive}")
