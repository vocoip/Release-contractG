#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path


def get_app_name() -> str:
    return "contractG"


def get_user_data_dir(app_name: str | None = None) -> Path:
    name = app_name or get_app_name()

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / name

    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / name
        return Path.home() / "AppData" / "Roaming" / name

    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / name
    return Path.home() / ".local" / "share" / name


def get_writable_base_dir() -> Path:
    override = os.environ.get("CONTRACTG_HOME")
    if override:
        return Path(override).expanduser().resolve()
    if hasattr(sys, "_MEIPASS"):
        return get_user_data_dir().resolve()
    return Path(__file__).resolve().parents[2]


def ensure_writable_layout() -> Path:
    base = get_writable_base_dir()
    base.mkdir(parents=True, exist_ok=True)
    for folder in ("data", "output", "logs", "config", "templates"):
        (base / folder).mkdir(parents=True, exist_ok=True)
    return base


def set_working_directory() -> Path:
    base = ensure_writable_layout()
    os.chdir(str(base))
    return base


def get_resource_base_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]
