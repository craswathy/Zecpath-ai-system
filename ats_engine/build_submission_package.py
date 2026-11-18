import glob
import os
import zipfile
from datetime import datetime

SKIP_DIRS = {"__pycache__", ".pytest_cache", "submission_package", ".ipynb_checkpoints"}
SKIP_SUFFIX = (".bak", ".pyc", ".zip", ".log")
SKIP_NAMES = {".env"}
MAX_MB = 25
OUT_DIR = "submission_package"
ZIP_NAME = "Zecpath_AI_Internship_Submission.zip"


def collect():
    included, too_big = [], []
    for folder, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if name.endswith(SKIP_SUFFIX) or name in SKIP_NAMES:
                continue
            path = os.path.relpath(os.path.join(folder, name), ".")
            if os.path.getsize(path) > MAX_MB * 1024 * 1024:
                too_big.append(path)
            else:
                included.append(path)
    return sorted(included), sorted(too_big)


def hygiene_report(included):
    print("REPOSITORY CHECK")
    root_md = [f for f in included if os.sep not in f and f.endswith(".md")]
    print(f"  Documents in the root folder: {len(root_md)}")
    samples = sorted(glob.glob("data/*.pdf") + glob.glob("data/*.docx"))
    print(f"  Sample resume files in data/ ({len(samples)}): review each. Remove or anonymise any that belong to real people.")
    for s in samples:
        print("     -", s)
    for needed in ("README.md", "requirements.txt", ".gitignore", "AI_ROADMAP.md", "INTERNSHIP_PORTFOLIO.md"):
        print(f"  {'OK     ' if os.path.exists(needed) else 'MISSING'} {needed}")


def run():
    included, too_big = collect()
    hygiene_report(included)

    lines = ["Zecpath AI internship submission package",
             f"Built: {datetime.now():%Y-%m-%d %H:%M}",
             f"Files: {len(included)}", ""]
    lines += [f"{os.path.getsize(p):>10}  {p}" for p in included]
    manifest = "\n".join(lines)

    os.makedirs(OUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUT_DIR, ZIP_NAME)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for path in included:
            z.write(path, arcname=path)
        z.writestr("MANIFEST.txt", manifest)
    with open(os.path.join(OUT_DIR, "MANIFEST.txt"), "w", encoding="utf-8") as f:
        f.write(manifest)

    size_mb = round(os.path.getsize(zip_path) / (1024 * 1024), 1)
    print(f"\nPackage: {zip_path}  ({len(included)} files, {size_mb} MB)")
    if too_big:
        print(f"Skipped {len(too_big)} file(s) over {MAX_MB} MB (upload separately if needed):")
        for p in too_big:
            print("   -", p)


if __name__ == "__main__":
    run()