import shutil
from pathlib import Path

import click

ROOT_DIR = Path(__file__).resolve().parent.parent

def run(cmd, **kwargs):
    import subprocess
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True, **kwargs)
    if result.returncode != 0:
        print(f"ERROR running: {cmd}")
        print(result.stderr)
        print(result.stdout)
    return result, result.returncode == 0


@click.command()
@click.option("--user", default=None, help="GitHub username (Mode B: simple single-account)")
@click.option("--uuid", default=None, help="Account UUID (Mode A: fleet/config-driven)")
@click.option(
    "--config",
    default=None,
    help='Config repo in "user/repo" format (required when --uuid is set)',
)
def main(user, uuid, config):
    # Validate mutual exclusivity
    if user and uuid:
        raise click.UsageError("--user and --uuid are mutually exclusive.")
    if not user and not uuid:
        raise click.UsageError("One of --user or --uuid is required.")
    if uuid and not config:
        raise click.UsageError("--config (user/repo) is required when --uuid is set.")

    # Install age key
    shutil.copy(ROOT_DIR / "keys" / "age.key", "/opt/age.key")
    print("Age key installed at /opt/age.key")

    # Clear stale dirs
    shutil.rmtree("/opt/payload", ignore_errors=True)
    shutil.rmtree("/opt/claude-config", ignore_errors=True)

    if uuid:
        # ── Mode A: fleet/config-driven ────────────────────────────────────

        # Write account UUID
        Path("/opt/account-uuid").write_text(uuid)

        # Clone config repo
        config_url = f"https://github.com/{config}"
        _, ok = run(f"git clone {config_url} /opt/claude-config --depth 1")
        if not ok:
            raise RuntimeError(f"Failed to clone config repo: {config_url}")

        # Determine payload repo from config.toml if present, else default
        import tomllib
        config_toml = Path("/opt/claude-config/config.toml")
        payload_repo_slug = None
        if config_toml.exists():
            with open(config_toml, "rb") as f:
                cfg = tomllib.load(f)
            g = cfg.get("global", {})
            acct = cfg.get("account", {}).get(uuid, {})
            payload_repo_slug = acct.get("payload_repo") or g.get("payload_repo")

        # Fall back to <github_username from config>/claude-payload
        if not payload_repo_slug:
            with open(config_toml, "rb") as f:
                cfg = tomllib.load(f)
            github_username = (
                cfg.get("account", {}).get(uuid, {}).get("github_username")
                or cfg.get("global", {}).get("github_username")
            )
            if not github_username:
                raise RuntimeError("Cannot determine github_username from config.toml")
            payload_repo_slug = f"{github_username}/claude-payload"

        payload_url = f"https://github.com/{payload_repo_slug}"
        _, ok = run(f"git clone {payload_url} /opt/payload --depth 1")
        if not ok:
            raise RuntimeError(f"Failed to clone payload repo: {payload_url}")

    else:
        # ── Mode B: simple single-account ──────────────────────────────────

        # Write github username
        Path("/opt/github-username").write_text(user)

        payload_url = f"https://github.com/{user}/claude-payload"
        _, ok = run(f"git clone {payload_url} /opt/payload --depth 1")
        if not ok:
            raise RuntimeError(f"Failed to clone payload repo: {payload_url}")

    # ── Invoke payload ──────────────────────────────────────────────────────
    result, _ = run("PYTHONPATH=/opt/payload python -m src.main")
    if result.stderr:
        print("ERROR:")
        print(result.stderr)
    print(result.stdout)


if __name__ == "__main__":
    main()
