#!/usr/bin/env python3
"""Compatibility entrypoint for the html-md-sync dual-format checker."""

from __future__ import annotations

import runpy
from pathlib import Path


TARGET = Path(__file__).resolve().parents[1] / "skills" / "html-md-sync" / "scripts" / "check_dual_format.py"
runpy.run_path(str(TARGET), run_name="__main__")
