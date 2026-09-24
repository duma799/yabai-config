#!/usr/bin/env python3

import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent.resolve()
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP_DIR = Path.home() / ".config" / f"yabaduma-backup-{TIMESTAMP}"

GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
NC = "\033[0m"


def log(msg):
    print(f"{BLUE}[INFO]{NC} {msg}")


def ask(question, default=True):
    hint = "[Y/n]" if default else "[y/N]"
    answer = input(f"{BLUE}[?]{NC} {question} {hint} ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def success(msg):
    print(f"{GREEN}[SUCCESS]{NC} {msg}")


def warn(msg):
    print(f"{YELLOW}[WARNING]{NC} {msg}")


def run_cmd(cmd, shell=False):
    result = subprocess.run(cmd, shell=shell, text=True)
    return result.returncode == 0


def run_cmd_or_exit(cmd, shell=False):
    if not run_cmd(cmd, shell):
        print(f"Error executing command: {cmd}")
        sys.exit(1)


def check_brew_package(package_name):
    result = subprocess.run(
        ["brew", "list", "--formula"], capture_output=True, text=True
    )
    return package_name in result.stdout.split()


def check_cask(cask_name):
    result = subprocess.run(["brew", "list", "--cask"], capture_output=True, text=True)
    return cask_name in result.stdout.split()


def install_dependencies(install_sketchybar=True, install_borders=True, install_tint_app=False):
    log("Checking prerequisites...")
    if not shutil.which("brew"):
        warn("Homebrew not found. Installing...")
        run_cmd_or_exit(
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True,
        )
    else:
        success("Homebrew is installed.")

    log("Tapping repositories...")
    run_cmd_or_exit(["brew", "tap", "koekeishiya/formulae"])
    if install_sketchybar or install_borders:
        run_cmd_or_exit(["brew", "tap", "FelixKratz/formulae"])

    packages = [
        "koekeishiya/formulae/yabai",
        "koekeishiya/formulae/skhd",
        "blueutil",
        "jq",
    ]

    if install_borders:
        packages.append("FelixKratz/formulae/borders")
    if install_sketchybar:
        packages.append("FelixKratz/formulae/sketchybar")

    log("Installing dependencies...")
    for pkg in packages:
        pkg_name = pkg.split("/")[-1]

        if check_brew_package(pkg_name):
            log(f"{pkg_name} is already installed.")
        else:
            log(f"Installing {pkg}...")
            run_cmd_or_exit(["brew", "install", pkg])

    font = "font-hack-nerd-font"
    if check_cask(font):
        log(f"{font} is already installed.")
    else:
        log(f"Installing {font}...")
        run_cmd_or_exit(["brew", "install", "--cask", font])

    # tint: colours from the wallpaper (replaces pywal). Its full name,
    # because Homebrew has an unrelated formula called "tint".
    log("Installing tint...")
    run_cmd_or_exit(["brew", "tap", "duma799/tint", "https://github.com/duma799/tint"])
    if check_brew_package("tint"):
        log("tint is already installed.")
    else:
        run_cmd_or_exit(["brew", "install", "duma799/tint/tint"])

    if install_tint_app:
        if check_cask("tint-app"):
            log("The tint app is already installed.")
        else:
            run_cmd_or_exit(["brew", "install", "--cask", "duma799/tint/tint-app"])

    if shutil.which("wal"):
        warn("pywal is still installed but no longer used. Remove it with: pip3 uninstall pywal")


def expand_path(path_str):
    return Path(os.path.expanduser(path_str))


def backup_and_link(src, dest):
    src = Path(src)
    dest = expand_path(str(dest))

    dest_dir = dest.parent

    if dest.exists() or dest.is_symlink():
        shutil.move(str(dest), str(BACKUP_DIR))

    dest_dir.mkdir(parents=True, exist_ok=True)
    os.symlink(src, dest)
    success(f"Linked {src} -> {dest}")


def setup_files(install_sketchybar=True, install_borders=True):
    log(f"Backing up existing configs to {BACKUP_DIR}...")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    backup_and_link(REPO_DIR / "yabairc", Path.home() / ".yabairc")
    backup_and_link(REPO_DIR / "skhdrc", Path.home() / ".skhdrc")

    if install_borders:
        backup_and_link(
            REPO_DIR / "bordersrc", Path.home() / ".config" / "borders" / "bordersrc"
        )
    if install_sketchybar:
        backup_and_link(REPO_DIR / "sketchybar", Path.home() / ".config" / "sketchybar")

    backup_and_link(REPO_DIR / "scripts", Path.home() / ".config" / "skhd" / "scripts")

    log("Setting up globally accessible scripts...")
    local_bin = Path.home() / ".local" / "bin"
    local_bin.mkdir(parents=True, exist_ok=True)

    reload_theme_src = REPO_DIR / "reload-theme.py"
    reload_theme_dest = local_bin / "reload-theme"

    backup_and_link(reload_theme_src, reload_theme_dest)
    backup_and_link(REPO_DIR / "scripts" / "new-wezterm", local_bin / "new-wezterm")

    reload_theme_src.chmod(reload_theme_src.stat().st_mode | 0o111)

    # tint runs this after every theme change: it updates Zed, VS Code,
    # Antigravity and Gemini CLI (tint reloads SketchyBar and borders itself).
    backup_and_link(
        reload_theme_src, Path.home() / ".config" / "tint" / "hooks" / "post-apply"
    )

    if str(local_bin) not in os.environ["PATH"]:
        warn(f"Ensure {local_bin} is in your PATH. Add this to your shell rc:")
        print(f'export PATH="{local_bin}:$PATH"')


def start_services(install_sketchybar=True, install_borders=True):
    log("Starting services...")

    for tool in ["yabai", "skhd"]:
        log(f"Starting {tool}...")
        run_cmd([tool, "--stop-service"])
        if run_cmd([tool, "--start-service"]):
            success(f"{tool} service started.")
        else:
            warn(
                f"Failed to start {tool}. "
                f"Run '{tool} --start-service' manually after granting Accessibility permissions."
            )

    brew_services = []
    if install_borders:
        brew_services.append("borders")
    if install_sketchybar:
        brew_services.append("sketchybar")

    for service in brew_services:
        log(f"Starting {service}...")
        if run_cmd(["brew", "services", "restart", service]):
            success(f"{service} service started.")
        else:
            warn(
                f"Failed to start {service}. Run 'brew services restart {service}' manually."
            )

    log("Starting tint (re-themes on every wallpaper change, from login)...")
    if run_cmd(["tint", "service", "install"]):
        success("tint service started.")
    else:
        warn("Failed to start tint. Run 'tint service install' manually, then 'tint doctor'.")


def main():
    try:
        print("")
        print("=== Yabaduma Config Installer ===")
        print("")

        install_sketchybar = ask("Install sketchybar (status bar)?", default=True)
        install_borders = ask("Install borders (window borders)?", default=True)
        install_tint_app = ask("Install the tint desktop app (preview and tweak themes)?", default=False)
        print("")

        install_dependencies(install_sketchybar, install_borders, install_tint_app)
        setup_files(install_sketchybar, install_borders)
        start_services(install_sketchybar, install_borders)

        success("Installation complete!")
        print("")
        print("Next steps:")
        print("1. Grant Accessibility permissions to yabai and skhd if prompted.")
        print("2. Change the wallpaper: tint themes everything from it.")
        print("   Or: reload-theme /path/to/img.jpg (sets it and themes from it).")
        print("3. Run 'tint doctor' if something doesn't change colour.")

    except KeyboardInterrupt:
        print("\nInstallation aborted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
