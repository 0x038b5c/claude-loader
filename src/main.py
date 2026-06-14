from pathlib import Path

import shutil
import subprocess

ROOT_DIR = Path(__file__).resolve().parent.parent

GITHUB_USERNAME = "0x038b5c"
PAYLOAD_REPO    = f"https://github.com/{GITHUB_USERNAME}/claude-payload"


def run(cmd, successcode=0, **kwargs):
    result = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
        **kwargs,
    )
    if result.returncode != successcode:
        print("ERROR running:", cmd)
        print(result.stderr)
        print(result.stdout)
    return result, result.returncode == successcode


def main():
    # Install age key
    shutil.copy(ROOT_DIR / "keys" / "age.key", "/opt/age.key")
    print("Age key installed at /opt/age.key")

    # Clear stale payload dir if present (e.g. from a previous session)
    shutil.rmtree("/opt/payload", ignore_errors=True)

    # Clone payload and run
    run(f"git clone {PAYLOAD_REPO} /opt/payload --depth 1")
    result, _ = run(f"PYTHONPATH=/opt/payload python -m src.main {GITHUB_USERNAME}")

    if result.stderr:
        print("ERROR:")
        print(result.stderr)

    print(result.stdout)


if __name__ == "__main__":
    main()
