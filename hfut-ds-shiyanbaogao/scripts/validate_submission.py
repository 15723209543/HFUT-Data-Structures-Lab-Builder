from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

from fill_report import validate_spec
from generate_viva_guide import validate_spec as validate_viva_spec
from hfut_ds_common import FORBIDDEN_MARKS, NS, W_NS, paragraph_text, read_json, strict_gbk_decode
from hfut_ds_common import STUDENT_DECL_BEGIN, STUDENT_DECL_END, STUDENT_IMPL_BEGIN, STUDENT_IMPL_END


TEXT_EXTS = {".cpp", ".c", ".h", ".hpp", ".dev", ".txt", ".btr", ".tre", ".grp"}
COMPILED_EXTS = {".exe", ".o", ".obj", ".layout", ".bak", ".tmp", ".pdb"}
W = f"{{{W_NS}}}"


class Results:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def check_forbidden(text: str, label: str, result: Results) -> None:
    lowered = text.lower()
    for mark in FORBIDDEN_MARKS:
        if mark.lower() in lowered:
            result.error(f"{label}: contains forbidden source mark {mark!r}")
    if re.search(r"\b(?:TODO|TBD)\b|待补充", text, re.IGNORECASE):
        result.error(f"{label}: contains unfinished placeholder")


def parse_dev(path: Path) -> list[str]:
    text = strict_gbk_decode(path)
    return [line.split("=", 1)[1].strip() for line in text.splitlines() if line.startswith("FileName=")][1:]


def validate_projects(root: Path, problems: int, manifest: dict, result: Results) -> None:
    expected = [f"T{index}" for index in range(1, problems + 1)]
    actual = sorted(
        (path.name for path in root.iterdir() if path.is_dir() and re.fullmatch(r"T\d+", path.name)),
        key=lambda value: int(value[1:]),
    )
    if actual != expected:
        result.error(f"project folders must be consecutive {expected}; got {actual}")
    for name in expected:
        folder = root / name
        if not folder.is_dir():
            continue
        devs = list(folder.glob("*.dev"))
        mains = [path for path in folder.iterdir() if path.name.lower() == "main.cpp"]
        if len(devs) != 1:
            result.error(f"{name}: expected exactly one .dev file, got {len(devs)}")
        if len(mains) != 1:
            result.error(f"{name}: expected exactly one main.cpp, got {len(mains)}")
        if not list(folder.glob("*.h")) and not list(folder.glob("*.hpp")):
            result.error(f"{name}: missing header file")
        if len(list(folder.glob("*.cpp"))) < 2:
            result.error(f"{name}: expected main.cpp plus at least one implementation .cpp")
        declaration_regions: list[str] = []
        implementation_regions: list[str] = []
        for path in folder.iterdir():
            if not path.is_file():
                continue
            try:
                path.name.encode("gbk", errors="strict")
            except UnicodeEncodeError:
                result.error(f"{name}: filename cannot be represented in GBK: {path.name}")
            if path.suffix.lower() in COMPILED_EXTS:
                result.error(f"{name}: compiled/temp artifact must not be submitted: {path.name}")
            if path.suffix.lower() in TEXT_EXTS:
                try:
                    text = strict_gbk_decode(path)
                except UnicodeDecodeError as exc:
                    result.error(f"{name}/{path.name}: not strict GBK ({exc})")
                    continue
                check_forbidden(text, f"{name}/{path.name}", result)
                if STUDENT_DECL_BEGIN in text and STUDENT_DECL_END in text:
                    declaration_regions.append(text.split(STUDENT_DECL_BEGIN, 1)[1].split(STUDENT_DECL_END, 1)[0].strip())
                if STUDENT_IMPL_BEGIN in text and STUDENT_IMPL_END in text:
                    implementation_regions.append(text.split(STUDENT_IMPL_BEGIN, 1)[1].split(STUDENT_IMPL_END, 1)[0].strip())
        if not any(declaration_regions):
            result.error(f"{name}: student declaration region is empty")
        if not any(implementation_regions):
            result.error(f"{name}: student implementation region is empty")
        if mains:
            try:
                main_text = strict_gbk_decode(mains[0])
                if re.search(r"\b(?:class|struct)\s+[A-Za-z_]", main_text):
                    result.error(f"{name}/main.cpp: data structure/class definition belongs in a header")
                if re.search(r"\b[A-Za-z_]\w*::[A-Za-z_]\w*\s*\(", main_text):
                    result.error(f"{name}/main.cpp: member function implementation belongs in a .cpp file")
                if not re.search(r"(?:\.|->)\s*[A-Za-z_]\w*\s*\(", main_text):
                    result.error(f"{name}/main.cpp: no object member call found")
            except UnicodeDecodeError:
                pass
        for dev in devs:
            try:
                listed = parse_dev(dev)
            except Exception as exc:
                result.error(f"{name}/{dev.name}: cannot parse project ({exc})")
                continue
            for listed_name in listed:
                if not (folder / listed_name).is_file():
                    result.error(f"{name}/{dev.name}: references missing file {listed_name}")
            actual_project_files = {
                path.name for path in folder.iterdir() if path.is_file() and path.suffix.lower() in TEXT_EXTS - {".dev"}
            }
            if not actual_project_files.issubset(set(listed)):
                missing = sorted(actual_project_files - set(listed))
                result.error(f"{name}/{dev.name}: project omits files {missing}")

    for record in manifest.get("teacher_prefixes", []):
        path = root / str(record.get("path", ""))
        if not path.is_file():
            result.error(f"teacher-prefix file missing: {path}")
            continue
        length = int(record["prefix_length"])
        digest = hashlib.sha256(path.read_bytes()[:length]).hexdigest()
        if digest != record["prefix_sha256"]:
            result.error(f"{path.relative_to(root)}: teacher prefix changed")


def direct_paragraphs(docx: Path) -> list[etree._Element]:
    with zipfile.ZipFile(docx) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
    body = root.find("w:body", NS)
    return [child for child in body if child.tag == W + "p"] if body is not None else []


def validate_viva_pdf(root: Path, problems: int, viva_spec: dict, result: Results) -> None:
    try:
        normalized = validate_viva_spec(viva_spec)
    except Exception as exc:
        result.error(f"viva spec invalid: {exc}")
        return
    if len(normalized.get("problems", [])) != problems:
        result.error("viva spec problem count does not match --problems")
    viva_files = [path for path in root.glob("*验收问答.pdf") if path.is_file()]
    if len(viva_files) != 1:
        result.error(f"expected exactly one viva PDF named *验收问答.pdf, got {len(viva_files)}")
        return
    viva = viva_files[0]
    if viva.stat().st_size < 4096 or not viva.read_bytes().startswith(b"%PDF-"):
        result.error("viva PDF is invalid or unexpectedly small")
        return
    try:
        from pypdf import PdfReader

        reader = PdfReader(viva)
        if len(reader.pages) < 3:
            result.error("viva PDF has too few pages for a comprehensive guide")
        metadata = " ".join(str(value or "") for value in (reader.metadata or {}).values())
        check_forbidden(metadata, f"{viva.name} metadata", result)
    except ImportError:
        result.warning("pypdf unavailable; viva PDF page-count and metadata checks skipped")
    except Exception as exc:
        result.error(f"cannot read viva PDF: {exc}")


def validate_report(root: Path, problems: int, spec: dict, manifest: dict, result: Results) -> None:
    docx_files = [path for path in root.glob("*.docx") if path.is_file()]
    pdf_files = [path for path in root.glob("*.pdf") if path.is_file()]
    report_pdfs = [path for path in pdf_files if "验收问答" not in path.stem]
    if len(docx_files) != 1:
        result.error(f"expected exactly one final DOCX at root, got {len(docx_files)}")
        return
    report = docx_files[0]
    if len(report_pdfs) != 1:
        result.error(f"expected exactly one final report PDF at root, got {len(report_pdfs)}")
    elif report_pdfs[0].stat().st_size < 1024:
        result.error("final PDF is unexpectedly small")
    if len(pdf_files) != 2:
        result.error(f"expected exactly two PDFs (report and viva) at root, got {len(pdf_files)}")
    paragraphs = direct_paragraphs(report)
    texts = [paragraph_text(node) for node in paragraphs]
    combined = "\n".join(texts)
    check_forbidden(combined, report.name, result)
    try:
        alg_index = next(index for index, text in enumerate(texts) if "算法设计与实现描述" in text)
        result_index = next(index for index, text in enumerate(texts) if "运行结果截图及说明" in text)
        reflection_index = next(index for index, text in enumerate(texts) if "总结" in text and "心得" in text and "建议" in text)
    except StopIteration:
        result.error("final DOCX is missing one or more semantic report headings")
        return
    if not (alg_index < result_index < reflection_index):
        result.error("final DOCX semantic report headings are out of order")
    expected_placeholders = 1 + 2 * problems
    actual_placeholders = sum("图片位置" in text for text in texts)
    if actual_placeholders < expected_placeholders:
        result.error(f"final DOCX needs at least {expected_placeholders} image placeholders; got {actual_placeholders}")
    if combined.count("【算法思想】") != problems:
        result.error("algorithm-idea block count does not match problem count")
    if combined.count("【实现代码】") != problems:
        result.error("implementation block count does not match problem count")
    if combined.count("【测试数据】") != problems or combined.count("【结果说明】") != problems:
        result.error("result block count does not match problem count")
    semantic_headings = {alg_index, result_index, reflection_index}
    for index, node in enumerate(paragraphs[alg_index:], alg_index):
        text = texts[index]
        if not text or index in semantic_headings:
            continue
        ppr = node.find("w:pPr", NS)
        ind = node.find("w:pPr/w:ind", NS)
        spacing = node.find("w:pPr/w:spacing", NS)
        runs = node.findall("w:r", NS)
        run = next((item for item in runs if paragraph_text(item)), runs[0] if runs else None)
        fonts = run.find("w:rPr/w:rFonts", NS) if run is not None else None
        size = run.find("w:rPr/w:sz", NS) if run is not None else None
        if ind is None or ind.get(W + "firstLineChars") != "200":
            result.error(f"report paragraph lacks 2-character first-line indent: {text[:35]}")
        if spacing is None or spacing.get(W + "line") != "240":
            result.error(f"report paragraph lacks single line spacing: {text[:35]}")
        if fonts is None or fonts.get(W + "eastAsia") != "宋体":
            result.error(f"report paragraph is not Song font: {text[:35]}")
        if size is None or size.get(W + "val") != "21":
            result.error(f"report paragraph is not 10.5 pt: {text[:35]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an HFUT data-structures experiment submission folder.")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--problems", type=int, required=True)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--viva-spec", type=Path, required=True)
    args = parser.parse_args()
    if not args.output_dir.is_dir():
        parser.error("output_dir must exist")
    work = args.output_dir / ".hfut-ds-work"
    manifest_path = work / "manifest.json"
    if not manifest_path.is_file():
        parser.error("missing .hfut-ds-work/manifest.json")
    manifest = read_json(manifest_path)
    spec = read_json(args.spec)
    if not args.viva_spec.is_file():
        parser.error("--viva-spec must be an existing JSON file")
    viva_spec = read_json(args.viva_spec)
    result = Results()
    try:
        validate_spec(spec)
    except Exception as exc:
        result.error(f"report spec invalid: {exc}")
    if len(spec.get("problems", [])) != args.problems:
        result.error("report spec problem count does not match --problems")
    if int(manifest.get("problem_count", -1)) != args.problems:
        result.error("prepared manifest problem count does not match --problems")
    validate_projects(args.output_dir, args.problems, manifest, result)
    validate_report(args.output_dir, args.problems, spec, manifest, result)
    validate_viva_pdf(args.output_dir, args.problems, viva_spec, result)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.errors:
        print(f"FAILED: {len(result.errors)} error(s)")
        return 1
    print("PASS: submission structure, encoding, report, viva PDF, and privacy/source-label checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
