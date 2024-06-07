# Session Manager

A tool to manage GNOME sessions by saving and restoring window layouts.

## Usage

To save the current session:

```bash
session-manager save
```

To restore the last saved session:

```bash
session-manager restore
```

Each individual display setup (determined by the number of connected monitors and their resolution) is saved as a separate session.
The script will restore the session that matches the current display setup.
The session is saved in `~/.config/session-manager/session_<layout_hash>`.

## Requirements

- Python 3.x
- `wmctrl` command-line tool
- `xrandr` command-line tool

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ll-nick/session-manager.git
```

2. Run the install script:

```bash
cd session-manager
./install.sh
```

This symlinks the script to `~/.local/bin`. Make sure this directory is in your `PATH`.

To install the script to a different directory, run the install script with the desired directory as an argument:

```bash
./install.sh /path/to/directory
```

## Credits

This scripts builds upon [this awesome answer on Ask Ubuntu](https://askubuntu.com/a/645614) by [Jacob Vlijm](https://askubuntu.com/users/72216/jacob-vlijm).

