"""pytest bootstrap — runs before tmp_path_factory resolves basetemp.

Windows hosts with a non-ASCII username produce a non-ASCII temp dir
(`pytest-of-<user>`), which breaks `git -C` invocations inside tests
(issue #24). Redirect tempdir to the 8.3 short path, falling back to
%SystemDrive%\\Temp when short names are unavailable.
"""
import os
import sys
import tempfile


def _ascii_tempdir(path: str) -> str | None:
    try:
        path.encode("ascii")
        return path
    except UnicodeEncodeError:
        pass
    if sys.platform != "win32":
        return None
    try:
        import ctypes

        buf = ctypes.create_unicode_buffer(260)
        if ctypes.windll.kernel32.GetShortPathNameW(path, buf, 260):
            buf.value.encode("ascii")
            return buf.value
    except Exception:
        pass
    fallback = os.path.join(os.environ.get("SystemDrive", "C:") + os.sep, "Temp")
    try:
        fallback.encode("ascii")
        os.makedirs(fallback, exist_ok=True)
        return fallback
    except Exception:
        return None


_fixed = _ascii_tempdir(tempfile.gettempdir())
if _fixed and _fixed != tempfile.gettempdir():
    tempfile.tempdir = _fixed
