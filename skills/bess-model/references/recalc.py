"""
recalc.py — portable Excel formula recalculation + error audit
===============================================================
openpyxl writes formulas but never evaluates them. Until something recalculates the
file, every formula cell is empty and #REF!/#NUM!/#N/A bugs stay invisible. This script
drives LibreOffice headlessly to calculate and save, then audits the result.

Works in three environments without modification:
  * Claude.ai / Cowork sandbox   — LibreOffice preinstalled
  * Claude Code on macOS/Linux   — uses `soffice` on PATH or the standard app bundle
  * Claude Code on Windows       — finds soffice.exe under Program Files

If LibreOffice is not installed, the script does NOT fail silently. It exits with a
clear message telling you to open the workbook in Excel once (which recalculates it)
before trusting any value.

USAGE
    python3 recalc.py <path/to/workbook.xlsx> [timeout_seconds]

EXIT CODES
    0 = recalculated, zero formula errors
    1 = recalculated, formula errors found (details printed)
    2 = could not recalculate (LibreOffice missing / timed out) — values NOT verified
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook

ERRORS = ("#REF!", "#NUM!", "#N/A", "#VALUE!", "#DIV/0!", "#NAME?", "#NULL!")

MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub RecalculateAndSave()
      ThisComponent.calculateAll()
      ThisComponent.store()
      ThisComponent.close(True)
    End Sub
</script:module>"""


def find_soffice():
    """Locate the LibreOffice binary on any of the three supported platforms."""
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if exe:
        return exe
    system = platform.system()
    if system == "Darwin":
        candidates = ["/Applications/LibreOffice.app/Contents/MacOS/soffice"]
    elif system == "Windows":
        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
    else:
        candidates = ["/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice"]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def macro_dir():
    """Where LibreOffice keeps user Basic macros, per platform."""
    system = platform.system()
    if system == "Darwin":
        base = "~/Library/Application Support/LibreOffice/4/user/basic/Standard"
    elif system == "Windows":
        base = r"%APPDATA%\LibreOffice\4\user\basic\Standard"
        return Path(os.path.expandvars(base))
    else:
        base = "~/.config/libreoffice/4/user/basic/Standard"
    return Path(os.path.expanduser(base))


def install_macro():
    d = macro_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / "Module1.xba").write_text(MACRO)
    # Register Module1 in script.xlb so LibreOffice loads it.
    xlb = d / "script.xlb"
    if not xlb.exists() or "Module1" not in xlb.read_text():
        xlb.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE library:library PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "library.dtd">\n'
            '<library:library xmlns:library="http://openoffice.org/2000/library" '
            'library:name="Standard" library:readonly="false" library:passwordprotected="false">\n'
            ' <library:element library:name="Module1"/>\n'
            "</library:library>"
        )


def soffice_env():
    """
    Environment for the LibreOffice subprocess.

    On a normal machine (Windows/macOS/Linux) plain env + the headless VCL plugin is
    enough. The Claude.ai/Cowork sandbox additionally blocks AF_UNIX sockets, which
    makes LibreOffice hang forever; that environment ships a helper that builds an
    LD_PRELOAD shim to work around it. Use the helper when it is there, ignore it
    otherwise — this is what makes one script work in all three environments.
    """
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "svp"
    for p in (
        "/mnt/skills/public/xlsx/scripts",
        "/mnt/skills/public/docx/scripts",
        "/mnt/skills/public/pptx/scripts",
    ):
        if os.path.isdir(p):
            sys.path.insert(0, p)
            try:
                from office.soffice import get_soffice_env  # type: ignore

                return get_soffice_env()
            except Exception:
                pass
            finally:
                sys.path.remove(p)
    return env


def clear_stale_lock(path):
    """
    A LibreOffice process that was killed or timed out leaves a `.~lock.<file>#`
    beside the workbook. Every subsequent headless run then blocks on it silently
    until it times out — including runs of completely different scripts. Nothing
    reports this; it just looks like LibreOffice is broken. Clear it first.
    """
    p = Path(path).resolve()
    lock = p.parent / f".~lock.{p.name}#"
    if lock.exists():
        try:
            lock.unlink()
        except OSError:
            pass


def recalc(path, timeout=90):
    soffice = find_soffice()
    if not soffice:
        print(
            "LibreOffice not found — cannot recalculate.\n"
            "  The workbook is written but its formulas are UNEVALUATED.\n"
            "  Fix: install LibreOffice, or open the file once in Excel (which recalculates\n"
            "  on open) and re-save. Do not quote any number from it until you have."
        )
        return 2

    clear_stale_lock(path)
    install_macro()
    cmd = [
        soffice,
        "--headless",
        "--norestore",
        # Must run against the DEFAULT user profile — that is where install_macro()
        # wrote Module1. Overriding UserInstallation with a fresh temp profile makes
        # LibreOffice hang waiting for a macro that is not there.
        "vnd.sun.star.script:Standard.Module1.RecalculateAndSave?language=Basic&location=application",
        str(Path(path).resolve()),
    ]
    try:
        subprocess.run(
            cmd, capture_output=True, timeout=timeout, check=False, env=soffice_env()
        )
    except subprocess.TimeoutExpired:
        print(f"LibreOffice timed out after {timeout}s — values NOT verified.")
        return 2

    return audit(path)


def audit(path):
    """Read back calculated values and count formula errors."""
    wb = load_workbook(path, data_only=True)
    summary, total = {}, 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if isinstance(v, str) and v in ERRORS:
                    total += 1
                    summary.setdefault(v, []).append(f"{ws.title}!{cell.coordinate}")

    wbf = load_workbook(path)
    n_formulas = sum(
        1
        for ws in wbf.worksheets
        for row in ws.iter_rows()
        for c in row
        if isinstance(c.value, str) and c.value.startswith("=")
    )

    print(
        json.dumps(
            {
                "status": "success" if total == 0 else "errors_found",
                "total_formulas": n_formulas,
                "total_errors": total,
                "error_summary": {
                    k: {"count": len(v), "locations": v[:20]} for k, v in summary.items()
                },
            },
            indent=2,
        )
    )
    return 0 if total == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    target = sys.argv[1]
    if not os.path.exists(target):
        print(f"File not found: {target}")
        sys.exit(2)
    t = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    sys.exit(recalc(target, t))
