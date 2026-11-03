"""Build source, plugin and standard-skill ZIPs and the universal Markdown file."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def package(root, output):
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError("Choose an output directory outside the source repository")
    subprocess.run([sys.executable, str(root / "tools/build_portable.py"), "--check"], check=True)
    subprocess.run([sys.executable, str(root / "tools/validate.py")], check=True)
    version = json.loads((root / "plugins/xunli-tutor/plugin.json").read_text(encoding="utf-8"))["version"]
    output.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for suffix, source, prefix in (
        ("source", root, "xunli-tutor/"),
        ("plugin", root / "plugins/xunli-tutor", ""),
        ("skill", root / "skills/learn-with-feedback", "learn-with-feedback/"),
    ):
        destination = output / f"xunli-tutor-{version}-{suffix}.zip"
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(source.rglob("*")):
                relative = path.relative_to(source)
                if any(part in {".git", "__pycache__", ".test-tmp", "learning", ".venv", "dist"} for part in relative.parts):
                    continue
                if path.is_symlink():
                    raise ValueError(f"Symlink refused: {relative}")
                if not path.is_file():
                    continue
                if path.name.startswith(".env") or path.suffix in {".zip", ".log", ".pyc"}:
                    raise ValueError(f"Private or generated file refused: {relative}")
                archive.write(path, prefix + relative.as_posix())
        with zipfile.ZipFile(destination) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"ZIP failed integrity check: {destination.name}")
            for name in archive.namelist():
                relative = Path(name)
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Unsafe archive path")
                original = source / name[len(prefix):]
                if archive.read(name) != original.read_bytes():
                    raise ValueError(f"Archive bytes differ: {name}")
        artifacts.append(destination)
    document = output / f"xunli-tutor-{version}-universal.md"
    shutil.copyfile(root / "portable/xunli-tutor.md", document)
    artifacts.append(document)
    sums = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in artifacts)
    (output / f"xunli-tutor-{version}-SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    return artifacts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    for artifact in package(Path(__file__).resolve().parents[1], args.output):
        print(f"{artifact.name}: {artifact.stat().st_size} bytes")
