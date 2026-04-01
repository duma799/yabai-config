#!/usr/bin/env python3

import subprocess
import json

SCRATCHPAD_TITLE = "scratchpad"
TERMINAL_CMD = ["wezterm", "start", "--class", SCRATCHPAD_TITLE]


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def run_yabai(args):
    return run(["yabai", "-m"] + args)


def get_scratchpad_window():
    windows_json = run_yabai(["query", "--windows"])
    if not windows_json:
        return None
    windows = json.loads(windows_json)
    for window in windows:
        if window.get("title") == SCRATCHPAD_TITLE:
            return window
    return None


def create_scratchpad():
    subprocess.Popen(TERMINAL_CMD, start_new_session=True)


def show_scratchpad(window_id):
    run_yabai(["window", str(window_id), "--focus"])
    window = get_scratchpad_window()
    if window and not window.get("is-floating"):
        run_yabai(["window", str(window_id), "--toggle", "float"])
    run_yabai(["window", str(window_id), "--grid", "10:10:1:1:8:7"])


def minimize_window(window_id):
    run_yabai(["window", str(window_id), "--minimize"])


def main():
    window = get_scratchpad_window()
    if window is None:
        create_scratchpad()
    elif window.get("is-minimized", False):
        run_yabai(["window", str(window["id"]), "--deminimize"])
        show_scratchpad(window["id"])
    elif window.get("has-focus", False):
        minimize_window(window["id"])
    else:
        show_scratchpad(window["id"])


if __name__ == "__main__":
    main()
