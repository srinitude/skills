"""Discover owned code by known extension or an explicit script interpreter."""
import re
import shlex
from pathlib import Path

from skill_package import owned_files, real_path

JS = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"}
DATA = {".json", ".toml", ".yaml", ".yml"}
SHELL = {".sh", ".bash"}
KNOWN = JS | DATA | SHELL | {
    ".py", ".rs", ".go", ".rb", ".php", ".lua", ".swift", ".kt", ".kts",
    ".java", ".c", ".h", ".cc", ".cpp", ".hpp", ".cxx", ".cs", ".fs", ".fsx",
    ".scala", ".clj", ".cljs", ".dart", ".ex", ".exs", ".erl", ".hs", ".pl",
    ".pm", ".ps1", ".cmd", ".bat", ".f90", ".jl", ".r", ".html", ".css",
    ".vue", ".svelte", ".sql", ".tf", ".hcl", ".pkl", ".usage", ".zsh",
}


def language(path):
    suffix = path.suffix.lower()
    if suffix in KNOWN:
        return suffix
    with path.open("rb") as stream:
        header = stream.readline(4096)
    if not header.startswith(b"#!"):
        return None
    words = shlex.split(header[2:].decode("utf-8"))
    if not words:
        return ".unknown-script"
    if Path(words[0]).name == "env":
        words = words[1:]
        if words and words[0] == "-S":
            words = words[1:]
    command = Path(words[0]).name if words else ""
    if re.fullmatch(r"python(?:\d+(?:\.\d+)*)?", command):
        return ".py"
    if command in {"sh", "bash"}:
        return ".sh"
    return ".unknown-script"


def collect(value):
    path = Path(value)
    if path.is_symlink():
        raise ValueError("selected code path is a symlink")
    if path.is_file():
        return [path]
    root = real_path(path)
    if not root.is_dir():
        raise FileNotFoundError(value)
    return sorted(item for item in owned_files(root) if language(item) is not None)
