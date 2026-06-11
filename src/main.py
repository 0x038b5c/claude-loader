from pathlib import Path

import shutil
import subprocess

ROOT_DIR = Path(__file__).resolve().parent.parent

def run(cmd, successcode=0, **kwargs):
    result = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
        **kwargs
    )

    success = result.returncode == successcode

    if not success:
        print("ERROR Running:", cmd)
        print("stderr:")
        print(result.stderr)
        print("stdout:")
        print(result.stdout)

    return result, success

def main():
    # install age key
    shutil.copy(
        ROOT_DIR / "keys" / "age.key",
        "/opt/age.key",
    )

    print("Age key installed at /opt/age.key")

    # clear stale payload dir if present (e.g. from a previous session)
    shutil.rmtree("/opt/payload", ignore_errors=True)

    # run payload
    run("git clone https://github.com/0x038b5c/claude-payload /opt/payload --depth 1")
    result, _ = run("PYTHONPATH=/opt/payload python -m src.main")

    if result.stderr:
        print("ERROR:")
        print(result.stderr)

    print(result.stdout)

if __name__ == "__main__":
    main()
