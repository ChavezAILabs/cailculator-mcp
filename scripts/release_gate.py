"""
Release gate. Run before `twine upload` and before `railway up`:

    python scripts/release_gate.py            # golden suite + gate records + build
    python scripts/release_gate.py --no-build # checks only

Steps (any failure stops the release):
  1. Working tree must be clean (the stamped commit has to describe the build).
  2. `pytest tests/golden -q` must pass (known-failure cases may xfail; nothing may fail).
  3. Every non-Template profile needs a GATES.json that matches its manifest version and
     whose commit has no later changes to profile/pipeline code. Otherwise re-run
     scripts/check_profile_gates.py. (A failing gate record is allowed: the profile ships
     as Experimental. A missing or stale one is not.)
  4. Delete build/ and dist/, write src/cailculator_mcp/_build_info.py (commit + golden
     suite version), run
     `python -m build`, then delete _build_info.py so source checkouts never carry a
     stale stamp.

Uploading (`twine upload dist/*`) and deploying (`railway up` from auth_server/) stay
manual on purpose.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "src" / "cailculator_mcp"
BUILD_INFO = PKG / "_build_info.py"
PIPELINE_PATHS = ["src/cailculator_mcp/profiles", "src/cailculator_mcp/tools.py",
                  "src/cailculator_mcp/patterns.py", "src/cailculator_mcp/zdtp",
                  "src/cailculator_mcp/core", "src/cailculator_mcp/hypercomplex.py"]


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def fail(msg):
    print(f"RELEASE BLOCKED: {msg}")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true", help="for dry runs only; stamps '+dirty'")
    opts = ap.parse_args()

    # 1. clean tree
    dirty = git("status", "--porcelain", "--untracked-files=no").stdout.strip()
    if dirty and not opts.allow_dirty:
        fail("working tree has uncommitted changes to tracked files:\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD").stdout.strip() + ("+dirty" if dirty else "")
    suite = (REPO / "tests" / "golden" / "VERSION").read_text(encoding="utf-8").strip()
    print(f"commit {commit}, golden suite v{suite}")

    # 2. golden suite
    print("running golden suite (in-process + spawned server from a temp cwd) ...", flush=True)
    rc = subprocess.run([sys.executable, "-m", "pytest", "tests/golden", "-q"], cwd=REPO).returncode
    if rc != 0:
        fail("golden suite did not pass")

    # 3. gate records current
    for manifest_path in sorted((PKG / "profiles").glob("*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("tier") == "Template":
            continue
        name, gates_path = manifest["name"], manifest_path.parent / "GATES.json"
        if not gates_path.exists():
            fail(f"{name}: no GATES.json; run scripts/check_profile_gates.py {name}")
        record = json.loads(gates_path.read_text(encoding="utf-8"))
        if record.get("profile_version") != manifest.get("version"):
            fail(f"{name}: GATES.json is for version {record.get('profile_version')}, "
                 f"manifest is {manifest.get('version')}; re-run the gate check")
        base = record.get("commit", "").split("+")[0]
        changed = git("diff", "--name-only", base, "HEAD", "--", *PIPELINE_PATHS).stdout.split()
        changed = [c for c in changed if not c.endswith("GATES.json")]
        if not base or git("cat-file", "-e", base).returncode != 0 or changed:
            fail(f"{name}: pipeline/profile code changed since the gate check at {record.get('commit')}"
                 + (f" ({', '.join(changed)})" if changed else "") + "; re-run the gate check")
        tier = "Official" if record.get("all_passed") else "Experimental"
        print(f"  {name}: gate record current -> ships as {tier}")

    if opts.no_build:
        print("checks passed (--no-build: nothing built)")
        return

    # 4. clear old artifacts, stamp, build, unstamp. setuptools reuses build/lib, so files
    # deleted from src/ (e.g. the rhi profile) would otherwise ride along into the wheel,
    # and `twine upload dist/*` would pick up earlier versions.
    for stale in ("build", "dist"):
        shutil.rmtree(REPO / stale, ignore_errors=True)
    BUILD_INFO.write_text(
        '"""Written by scripts/release_gate.py at build time. Do not commit."""\n'
        f'BUILD_COMMIT = "{commit}"\nGOLDEN_SUITE = "{suite}"\n', encoding="utf-8")
    try:
        rc = subprocess.run([sys.executable, "-m", "build"], cwd=REPO).returncode
    finally:
        BUILD_INFO.unlink(missing_ok=True)
    if rc != 0:
        fail("python -m build failed")
    print("\nBuild complete. Next (manual):\n  twine upload dist/*\n  cd auth_server && railway up\n"
          "Then: call get_version and one live tool; confirm provenance.server_version and build_commit.")


if __name__ == "__main__":
    main()
