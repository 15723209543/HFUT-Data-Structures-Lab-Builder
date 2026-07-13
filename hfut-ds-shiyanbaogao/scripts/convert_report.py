from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def convert_with_word(source: Path, output: Path) -> tuple[bool, str]:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell or os.name != "nt":
        return False, "PowerShell/Windows unavailable"
    script = (
        "$ErrorActionPreference='Stop'; "
        "$word=$null; $doc=$null; "
        "try { "
        "$word=New-Object -ComObject Word.Application; $word.Visible=$false; $word.DisplayAlerts=0; "
        f"$doc=$word.Documents.Open({ps_quote(str(source.resolve()))},$false,$true); "
        f"$doc.ExportAsFixedFormat({ps_quote(str(output.resolve()))},17); "
        "} finally { if($doc -ne $null){$doc.Close($false)}; if($word -ne $null){$word.Quit()} }"
    )
    result = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True,
        text=True,
        timeout=180,
    )
    return output.is_file() and output.stat().st_size > 0, (result.stderr or result.stdout).strip()


def find_soffice() -> str | None:
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    candidates = [
        Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
        Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
    ]
    return str(next((path for path in candidates if path.is_file()), "")) or None


def convert_with_libreoffice(source: Path, output: Path) -> tuple[bool, str]:
    soffice = find_soffice()
    if not soffice:
        return False, "LibreOffice unavailable"
    with tempfile.TemporaryDirectory(prefix="hfut-ds-lo-") as temp:
        temp_dir = Path(temp)
        out_dir = temp_dir / "out"
        profile = temp_dir / "profile"
        out_dir.mkdir()
        profile.mkdir()
        profile_uri = profile.resolve().as_uri()
        result = subprocess.run(
            [
                soffice,
                "--headless",
                f"-env:UserInstallation={profile_uri}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(out_dir),
                str(source.resolve()),
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        generated = out_dir / f"{source.stem}.pdf"
        if generated.is_file() and generated.stat().st_size > 0:
            shutil.copy2(generated, output)
            return True, (result.stderr or result.stdout).strip()
        return False, (result.stderr or result.stdout).strip()


def render_pdf(pdf: Path, render_dir: Path) -> int:
    if render_dir.exists() and any(render_dir.iterdir()):
        raise FileExistsError(f"render directory is not empty: {render_dir}")
    render_dir.mkdir(parents=True, exist_ok=True)
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm:
        dependency_root = Path(pdftoppm).resolve().parents[2]
        bundled = dependency_root / "native" / "poppler" / "Library" / "bin" / "pdftoppm.exe"
        if bundled.is_file():
            pdftoppm = str(bundled)
    if pdftoppm:
        prefix = render_dir / "page"
        command = [pdftoppm, "-png", "-r", "144", str(pdf.resolve()), str(prefix.resolve())]
        if os.name == "nt" and pdftoppm.lower().endswith((".cmd", ".bat")):
            command = [os.environ.get("COMSPEC", "cmd.exe"), "/c", *command]
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)
        pages = sorted(render_dir.glob("page-*.png"))
        if result.returncode == 0 and pages:
            for index, path in enumerate(pages, 1):
                target = render_dir / f"page-{index:03d}.png"
                if path != target:
                    path.replace(target)
            return len(pages)
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("Neither pdftoppm nor PyMuPDF could render PDF pages") from exc
    document = fitz.open(pdf)
    try:
        for index, page in enumerate(document, 1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            pixmap.save(render_dir / f"page-{index:03d}.png")
        return document.page_count
    finally:
        document.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a final DOCX to PDF and optionally render all PDF pages.")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output-pdf", type=Path, required=True)
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args()
    if not args.docx.is_file() or args.docx.suffix.lower() != ".docx":
        parser.error("docx must be an existing DOCX")
    if args.output_pdf.exists():
        parser.error("output PDF already exists")
    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
    ok, detail = convert_with_word(args.docx, args.output_pdf)
    method = "Microsoft Word"
    if not ok:
        ok, detail_lo = convert_with_libreoffice(args.docx, args.output_pdf)
        detail = f"Word: {detail}; LibreOffice: {detail_lo}"
        method = "LibreOffice"
    if not ok:
        raise RuntimeError(f"DOCX-to-PDF conversion failed. {detail}")
    print(f"Converted with {method}: {args.output_pdf}")
    if args.render_dir:
        pages = render_pdf(args.output_pdf, args.render_dir)
        print(f"Rendered {pages} pages to {args.render_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
