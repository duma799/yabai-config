#!/usr/bin/env python3
"""Re-theme everything from the wallpaper, or from an image.

tint (https://github.com/duma799/tint) does the work: it writes the colours,
reloads SketchyBar and JankyBorders, and themes Zed, VS Code, Antigravity and
Gemini CLI. This is a short name for it:

    reload-theme                 re-theme from the current wallpaper
    reload-theme image.jpg       make it the wallpaper and theme from it
"""

import shutil
import subprocess
import sys
from pathlib import Path


def main():
    tint = shutil.which("tint")
    if not tint:
        print("Error: tint not found. Install it: brew install duma799/tint/tint")
        sys.exit(1)

    args = [tint, "apply"]
    if len(sys.argv) > 1:
        wallpaper = sys.argv[1]
        if not Path(wallpaper).exists():
            print(f"Error: Wallpaper not found: {wallpaper}")
            sys.exit(1)
        args += [wallpaper, "--set-wallpaper"]

    sys.exit(subprocess.run(args).returncode)


if __name__ == "__main__":
    main()
