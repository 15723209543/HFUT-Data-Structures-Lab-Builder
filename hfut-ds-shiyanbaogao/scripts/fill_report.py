from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path

from lxml import etree

from hfut_ds_common import FORBIDDEN_MARKS, NS, W_NS, paragraph_text, read_json


W = f"{{{W_NS}}}"
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"


def as_list(value: object, field: str) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise ValueError(f"{field} must be a string or an array of strings")


def char_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def validate_spec(spec: dict) -> None:
    shared = spec.get("shared_types")
    problems = spec.get("problems")
    reflection = spec.get("reflection")
    if not isinstance(shared, dict) or not isinstance(problems, list) or not problems or not isinstance(reflection, dict):
        raise ValueError("shared_types, non-empty problems, and reflection are required")
    as_list(shared.get("description"), "shared_types.description")
    if "图片位置" not in str(shared.get("screenshot_placeholder", "")):
        raise ValueError("shared_types.screenshot_placeholder must be an explicit 图片位置 placeholder")
    for index, problem in enumerate(problems, 1):
        if not isinstance(problem, dict):
            raise ValueError(f"problems[{index}] must be an object")
        idea = str(problem.get("algorithm_idea", ""))
        if not idea or char_count(idea) > 150:
            raise ValueError(f"problem {index} algorithm_idea must be 1-150 non-whitespace characters")
        if "时间复杂度" not in idea or "空间复杂度" not in idea:
            raise ValueError(f"problem {index} algorithm_idea must state both complexity conclusions")
        steps = problem.get("steps")
        if not isinstance(steps, list) or not (1 <= len(steps) <= 10) or not all(isinstance(item, str) for item in steps):
            raise ValueError(f"problem {index} steps must contain 1-10 strings")
        for step in steps:
            if "\n" in step or "\r" in step or char_count(step) > 50:
                raise ValueError(f"problem {index} has a multiline or overlong step: {step!r}")
        if "图片位置" not in str(problem.get("code_screenshot_placeholder", "")):
            raise ValueError(f"problem {index} needs a code 图片位置 placeholder")
        if "图片位置" not in str(problem.get("result_screenshot_placeholder", "")):
            raise ValueError(f"problem {index} needs a result 图片位置 placeholder")
        if not as_list(problem.get("test_data"), f"problem {index}.test_data"):
            raise ValueError(f"problem {index} test_data cannot be empty")
        if not as_list(problem.get("result_explanation"), f"problem {index}.result_explanation"):
            raise ValueError(f"problem {index} result_explanation cannot be empty")
    summary = as_list(reflection.get("summary"), "reflection.summary")
    experience = as_list(reflection.get("experience"), "reflection.experience")
    suggestion = str(reflection.get("suggestion", ""))
    total = char_count("".join(summary + experience + [suggestion]))
    if total <= 800:
        raise ValueError(f"reflection must exceed 800 non-whitespace characters; got {total}")
    if not suggestion or char_count(suggestion) > 100:
        raise ValueError("reflection.suggestion must contain 1-100 non-whitespace characters")
    serialized = str(spec)
    lower = serialized.lower()
    for mark in FORBIDDEN_MARKS:
        if mark.lower() in lower:
            raise ValueError(f"forbidden source mark in report spec: {mark}")
    if re.search(r"\b(?:TODO|TBD)\b|待补充", serialized, re.IGNORECASE):
        raise ValueError("report spec contains an unfinished placeholder")


def paragraph(text: str) -> etree._Element:
    p = etree.Element(W + "p")
    ppr = etree.SubElement(p, W + "pPr")
    ind = etree.SubElement(ppr, W + "ind")
    ind.set(W + "firstLineChars", "200")
    spacing = etree.SubElement(ppr, W + "spacing")
    spacing.set(W + "before", "0")
    spacing.set(W + "after", "0")
    spacing.set(W + "line", "240")
    spacing.set(W + "lineRule", "auto")
    jc = etree.SubElement(ppr, W + "jc")
    jc.set(W + "val", "both")
    run = etree.SubElement(p, W + "r")
    rpr = etree.SubElement(run, W + "rPr")
    fonts = etree.SubElement(rpr, W + "rFonts")
    for key in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(W + key, "宋体")
    size = etree.SubElement(rpr, W + "sz")
    size.set(W + "val", "21")
    size_cs = etree.SubElement(rpr, W + "szCs")
    size_cs.set(W + "val", "21")
    node = etree.SubElement(run, W + "t")
    if text.startswith(" ") or text.endswith(" "):
        node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    node.text = text
    return p


def build_algorithm(spec: dict) -> list[etree._Element]:
    shared = spec["shared_types"]
    nodes = [
        paragraph(f"（1）【{str(shared.get('title') or '共用数据类型')}】"),
        paragraph(str(shared["screenshot_placeholder"])),
    ]
    nodes.extend(paragraph(item) for item in as_list(shared["description"], "shared_types.description"))
    for index, problem in enumerate(spec["problems"], 1):
        nodes.append(paragraph(f"（{index + 1}）【{str(problem.get('name') or f'题目{index}')}】"))
        nodes.append(paragraph("【算法思想】"))
        nodes.append(paragraph(str(problem["algorithm_idea"])))
        nodes.append(paragraph("【算法步骤】"))
        nodes.extend(paragraph(f"{CIRCLED[step_index]} {step}") for step_index, step in enumerate(problem["steps"]))
        nodes.append(paragraph("【实现代码】"))
        nodes.append(paragraph(str(problem["code_screenshot_placeholder"])))
    return nodes


def build_results(spec: dict) -> list[etree._Element]:
    nodes: list[etree._Element] = []
    for index, problem in enumerate(spec["problems"], 1):
        nodes.append(paragraph(f"（{index}）【{str(problem.get('name') or f'题目{index}')}运行结果】"))
        nodes.append(paragraph("【测试数据】"))
        nodes.extend(paragraph(item) for item in as_list(problem["test_data"], f"problem {index}.test_data"))
        nodes.append(paragraph(str(problem["result_screenshot_placeholder"])))
        nodes.append(paragraph("【结果说明】"))
        nodes.extend(paragraph(item) for item in as_list(problem["result_explanation"], f"problem {index}.result_explanation"))
    return nodes


def build_reflection(spec: dict) -> list[etree._Element]:
    reflection = spec["reflection"]
    nodes = [paragraph("（1）【总结】")]
    nodes.extend(paragraph(item) for item in as_list(reflection["summary"], "reflection.summary"))
    nodes.append(paragraph("（2）【心得】"))
    nodes.extend(paragraph(item) for item in as_list(reflection["experience"], "reflection.experience"))
    nodes.append(paragraph("（3）【建议】"))
    nodes.append(paragraph(str(reflection["suggestion"])))
    return nodes


def find_direct_paragraph(body: etree._Element, predicate) -> etree._Element | None:
    for child in body:
        if child.tag == W + "p" and predicate(paragraph_text(child)):
            return child
    return None


def remove_between(body: etree._Element, left: etree._Element, right: etree._Element) -> None:
    left_index = body.index(left)
    right_index = body.index(right)
    for child in list(body)[left_index + 1 : right_index]:
        body.remove(child)


def insert_before(body: etree._Element, anchor: etree._Element, nodes: list[etree._Element]) -> None:
    for node in nodes:
        body.insert(body.index(anchor), node)


def save_replaced(source: Path, output: Path, document_xml: bytes) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source, "r") as src, zipfile.ZipFile(output, "w") as dst:
        for info in src.infolist():
            data = document_xml if info.filename == "word/document.xml" else src.read(info.filename)
            dst.writestr(info, data)


def fill(source: Path, output: Path, spec: dict) -> None:
    validate_spec(spec)
    if source.resolve() == output.resolve():
        raise ValueError("output must differ from the copied report base")
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    with zipfile.ZipFile(source) as archive:
        xml = archive.read("word/document.xml")
    root = etree.fromstring(xml)
    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    algorithm = find_direct_paragraph(body, lambda text: "算法设计与实现描述" in text)
    results = find_direct_paragraph(body, lambda text: "运行结果截图及说明" in text)
    reflection = find_direct_paragraph(body, lambda text: "总结" in text and "心得" in text and "建议" in text)
    if algorithm is None or results is None or reflection is None:
        raise ValueError("could not locate all three semantic report headings")
    if not (body.index(algorithm) < body.index(results) < body.index(reflection)):
        raise ValueError("semantic report headings are out of order")
    prefix_before = hashlib.sha256(
        b"".join(etree.tostring(child, method="c14n") for child in list(body)[: body.index(algorithm)])
    ).hexdigest()
    remove_between(body, algorithm, results)
    remove_between(body, results, reflection)
    appendix = find_direct_paragraph(body, lambda text: "附录" in text and "提交报告时去掉" in text)
    end_anchor = body.find("w:sectPr", NS)
    if end_anchor is None:
        raise ValueError("report body has no section properties")
    if appendix is not None and body.index(appendix) > body.index(reflection):
        start = body.index(reflection) + 1
        for child in list(body)[start : body.index(end_anchor)]:
            body.remove(child)
    else:
        for child in list(body)[body.index(reflection) + 1 : body.index(end_anchor)]:
            body.remove(child)
    insert_before(body, results, build_algorithm(spec))
    insert_before(body, reflection, build_results(spec))
    insert_before(body, end_anchor, build_reflection(spec))
    prefix_after = hashlib.sha256(
        b"".join(etree.tostring(child, method="c14n") for child in list(body)[: body.index(algorithm)])
    ).hexdigest()
    if prefix_before != prefix_after:
        raise RuntimeError("content before the algorithm section changed unexpectedly")
    document_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
    save_replaced(source, output, document_xml)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fill the final three semantic sections of a copied DOCX report.")
    parser.add_argument("report_base", type=Path)
    parser.add_argument("report_spec", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.report_base.is_file() or args.report_base.suffix.lower() != ".docx":
        parser.error("report_base must be an existing DOCX copy")
    fill(args.report_base, args.output, read_json(args.report_spec))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
