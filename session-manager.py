#!/usr/bin/env python3

import hashlib
import os
import subprocess
import sys
import time

BASE_DIR = os.path.join(os.environ["HOME"], ".config", "session-manager")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)


def print_help():
    print("Usage: session_manager.py [save|restore]")
    print("  save: Save the current session")
    print("  restore: Restore the last saved session")


if len(sys.argv) != 2 or sys.argv[1] not in ["save", "restore"]:
    print_help()
    sys.exit(1)

ARG = sys.argv[1]


def run_command(command):
    try:
        return subprocess.check_output(["/bin/bash", "-c", command]).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error: {e}")
        return ""


def is_normal_window(window_id):
    w_type = run_command(f"xprop -id {window_id}")
    return " _NET_WM_WINDOW_TYPE_NORMAL" in w_type


def get_display_layout_hash():
    xrandr_output = run_command("xrandr --listmonitors")
    return hashlib.sha256(xrandr_output.encode("utf-8")).hexdigest()


def get_session_filepath():
    layout_hash = get_display_layout_hash()
    return os.path.join(BASE_DIR, f"session_{layout_hash}.txt")


def get_app_name(pid):
    return run_command(f"ps -p {pid} -o comm=").strip()


def save_session():
    window_list = [line.split() for line in run_command("wmctrl -lpG").splitlines()]

    session_file = get_session_filepath()
    with open(session_file, "wt") as file:
        for window in window_list:
            if not is_normal_window(window[0]):
                continue
            workspace = window[1]
            pid = window[2]
            geometry = window[3:7]
            app_name = get_app_name(pid)

            file.write(
                f"{app_name} {workspace} {geometry[0]} {geometry[1]} {geometry[2]} {geometry[3]}\n"
            )


def get_app_command(app_name):
    app_name_to_command_map = {
        "gnome-terminal": "gnome-terminal",
        "chrome": "/usr/bin/google-chrome-stable",
        "mattermost-desk": "mattermost-desktop",
    }
    return app_name_to_command_map.get(app_name, app_name)


def get_app_options(app_name):
    app_options_map = {
        "gedit": "--new-window",
    }
    return app_options_map.get(app_name, "")


def set_window_geometry(window_id, workspace, x, y, width, height):
    commands = [
        f"wmctrl -ir {window_id} -b remove,maximized_horz",
        f"wmctrl -ir {window_id} -b remove,maximized_vert",
        f"wmctrl -ir {window_id} -t {workspace}",
        f"wmctrl -ir {window_id} -e 0,{x},{y},{width},{height}",
    ]
    for command in commands:
        run_command(command)


def launch_app_window(app_name, workspace, x, y, width, height):
    existing_windows = run_command("wmctrl -lp")

    processes = run_command("ps -e -o pid,cmd").splitlines()
    for process in processes:
        if app_name in process:
            return

    app_command = get_app_command(app_name)
    options = get_app_options(app_name)

    subprocess.Popen(["/bin/bash", "-c", f"{app_command} {options}"])

    try_count = 0
    max_tries = 30
    window_resized = False
    while not window_resized and try_count < max_tries:
        for windows in run_command("wmctrl -lp").splitlines():
            window_id = windows.split()[0]
            if window_id in existing_windows:
                continue
            set_window_geometry(window_id, workspace, x, y, width, height)
            window_resized = True
            break

        time.sleep(0.5)


def restore_session():
    session_file = get_session_filepath()
    try:
        lines = [line.split() for line in open(session_file).read().splitlines()]
        for line in lines:
            app_name = line[0]
            workspace = line[1]
            x = int(line[2])
            y = int(line[3])
            width = int(line[4])
            height = int(line[5])
            launch_app_window(app_name, workspace, x, y, width, height)
    except FileNotFoundError:
        print("No session file found for the current display layout.")


if ARG == "save":
    save_session()
elif ARG == "restore":
    restore_session()
