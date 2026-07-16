from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


EXCLUDED_DIRS = {".hfut-ds-work", "__pycache__", ".git", ".vs", "x64", "Debug", "Release"}
EXCLUDED_EXTS = {".exe", ".o", ".obj", ".layout", ".bak", ".tmp", ".pdb", ".png", ".json"}


def should_include(path: Path, root: Path, output: Path) -> bool:
    if path.resolve() == output.resolve():
        return False
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.suffix.lower() in EXCLUDED_EXTS:
        return False
    return path.is_file()


def package(root: Path, output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"output ZIP already exists: {output}")
    files = [path for path in root.rglob("*") if should_include(path, root, output)]
    if not files:
        raise ValueError("submission folder contains no deliverable files")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files, key=lambda item: str(item.relative_to(root)).lower()):
            arcname = (Path(root.name) / path.relative_to(root)).as_posix()
            archive.write(path, arcname)
    with zipfile.ZipFile(output) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"ZIP CRC check failed at {bad}")
        names = archive.namelist()
        if any(".hfut-ds-work" in name or "__pycache__" in name for name in names):
            raise RuntimeError("internal working files leaked into ZIP")
        if not any(name.lower().endswith(".docx") for name in names):
            raise RuntimeError("ZIP contains no DOCX report")
        pdf_names = [name for name in names if name.lower().endswith(".pdf")]
        viva_names = [name for name in pdf_names if "验收问答" in Path(name).stem]
        report_names = [name for name in pdf_names if "验收问答" not in Path(name).stem]
        if len(report_names) != 1:
            raise RuntimeError("ZIP must contain exactly one PDF report")
        if len(viva_names) != 1:
            raise RuntimeError("ZIP must contain exactly one *验收问答.pdf")
    return len(files)


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a validated submission folder without internal artifacts.")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output_dir.is_dir():
        parser.error("output_dir must exist")
    count = package(args.output_dir, args.output)
    print(f"Packaged {count} files: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
