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


def get_screen_resolution():
    # get resolution and the workspace correction (vector)
    xr_output = run_command("xrandr").split()
    pos = xr_output.index("current")
    resolution = [int(xr_output[pos + 1]), int(xr_output[pos + 3].replace(",", ""))]
    vp_data = run_command("wmctrl -d").split()
    curr_vp_data = [int(n) for n in vp_data[5].split(",")]
    return [resolution, curr_vp_data]


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
    relevant_windows = [
        [window[2], [int(n) for n in window[3:7]]]
        for window in window_list
        if is_normal_window(window[0]) == True
    ]
    for idx, window in enumerate(relevant_windows):
        relevant_windows[idx] = (
            f"{get_app_name(window[0])} {' '.join(map(str, window[1]))}"
        )
    session_file = get_session_filepath()
    with open(session_file, "wt") as file:
        for line in relevant_windows:
            file.write(line + "\n")


def launch_app_window(app_name, x, y, width, height):
    existing_windows = run_command("wmctrl -lp")
    # fix command for certain apps that open in new tab by default
    option = " --new-window" if app_name == "gedit" else ""

    # fix command if process name and command to run are different
    app_command = {
        "gnome-terminal": "gnome-terminal",
        "chrome": "/usr/bin/google-chrome-stable",
        "mattermost-desk": "mattermost-desktop",
    }.get(app_name, app_name)

    subprocess.Popen(["/bin/bash", "-c", f"{app_command}{option}"])
    # fix exception for Chrome (command = google-chrome-stable, but processname = chrome)
    app_name = "chrome" if "chrome" in app_name else app_name

    t = 0
    while t < 30:
        new_windows = [
            w.split()[0:3]
            for w in run_command("wmctrl -lp").splitlines()
            if not w in existing_windows
        ]
        processes = [
            [
                (p, w[0])
                for p in run_command("ps -e ww").splitlines()
                if app_name in p and w[2] in p
            ]
            for w in new_windows
        ]
        if processes:
            time.sleep(0.5)
            window_id = processes[0][0][1]
            commands = [
                f"wmctrl -ir {window_id} -b remove,maximized_horz",
                f"wmctrl -ir {window_id} -b remove,maximized_vert",
                f"wmctrl -ir {window_id} -e 0,{x},{y},{width},{height}",
            ]
            for command in commands:
                subprocess.call(["/bin/bash", "-c", command])
            break
        time.sleep(0.5)
        t = t + 1


def restore_session():
    screen_resolution_correction = get_screen_resolution()[1]
    session_file = get_session_filepath()
    try:
        lines = [line.split() for line in open(session_file).read().splitlines()]
        for line in lines:
            app_name = line[0]
            x = str(int(line[1]) - screen_resolution_correction[0])
            y = str(int(line[2]) - screen_resolution_correction[1] - 24)
            width = line[3]
            height = line[4]
            launch_app_window(app_name, x, y, width, height)
    except FileNotFoundError:
        print("No session file found for the current display layout.")


if ARG == "save":
    save_session()
elif ARG == "restore":
    restore_session()
