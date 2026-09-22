"""Forwarder for Devin sessions opened inside devin-setup/.

Devin sets DEVIN_PROJECT_DIR to the nearest `.git` root, which for the
nested devin-setup/ tree is this repo's root, while the hook commands in
devin-setup/.devin/hooks.v1.json run "$DEVIN_PROJECT_DIR/.devin/hooks/
devin_mode.py". Without this file python3 exits 2 on the missing script
and Devin reads exit 2 as "block" — every prompt was refused. Product
repos carry .devin/ at their root and never reach this file.
"""
import runpy
from pathlib import Path

runpy.run_path(
    str(
        Path(__file__).resolve().parents[2]
        / "devin-setup" / ".devin" / "hooks" / "devin_mode.py"
    ),
    run_name="__main__",
)
