from __future__ import annotations

import argparse
import re
from pathlib import Path

from hfut_ds_common import read_json, redact_pii, strict_gbk_decode, write_json


TEXT_EXTS = {".cpp", ".c", ".h", ".hpp"}
CONTROL_WORDS = {"if", "for", "while", "switch", "return", "sizeof", "catch"}


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def compact(value: object, limit: int = 500) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return redact_pii(text)[:limit]


def read_code(path: Path) -> str:
    try:
        return strict_gbk_decode(path)
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="strict")


def recursive_methods(text: str) -> list[str]:
    found: list[str] = []
    signature = re.compile(
        r"\b([A-Za-z_]\w*)::([A-Za-z_~]\w*)\s*\([^;{}]*\)\s*(?::[^{}]*)?\{",
        re.S,
    )
    for match in signature.finditer(text):
        owner, method = match.group(1), match.group(2)
        if method.startswith("~"):
            continue
        start = text.find("{", match.start(), match.end())
        if start < 0:
            continue
        depth = 0
        end = start
        for end in range(start, len(text)):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    break
        body = text[start + 1 : end]
        if re.search(rf"(?<!::)\b{re.escape(method)}\s*\(", body):
            found.append(f"{owner}::{method}")
    return unique(found)


def code_facts(folder: Path) -> dict[str, object]:
    files = sorted(path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in TEXT_EXTS)
    content: dict[str, str] = {path.name: read_code(path) for path in files}
    joined = "\n".join(content.values())
    main = next((text for name, text in content.items() if name.lower() == "main.cpp"), "")
    classes = unique(re.findall(r"\b(?:class|struct)\s+([A-Za-z_]\w*)", joined))
    definitions = unique(
        f"{owner}::{method}"
        for owner, method in re.findall(r"\b([A-Za-z_]\w*)::([A-Za-z_~]\w*)\s*\(", joined)
    )
    member_calls = unique(re.findall(r"(?:\.|->)\s*([A-Za-z_]\w*)\s*\(", main))
    free_like = unique(
        name
        for name in re.findall(r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{", joined)
        if name not in CONTROL_WORDS
    )
    recursive_candidates = recursive_methods(joined)
    signals = {
        "loop": bool(re.search(r"\b(?:for|while|do)\b", joined)),
        "branch": bool(re.search(r"\b(?:if|switch)\b", joined)),
        "recursion_candidate": bool(recursive_candidates),
        "dynamic_memory": bool(re.search(r"\b(?:new|delete)\b", joined)),
        "pointer_link": bool(re.search(r"->\s*(?:next|prior|lchild|rchild|firstarc|adjvex|child|sibling)\b", joined, re.I)),
        "stack_or_queue": bool(re.search(r"\b(?:stack|queue|push|pop|front|rear|top)\b", joined, re.I)),
        "matrix": bool(re.search(r"\b(?:matrix|arcs?|adjmat|visited)\b|\[[^\]]+\]\s*\[[^\]]+\]", joined, re.I)),
    }
    return {
        "files": [path.name for path in files],
        "classes_or_structs": classes,
        "member_definitions": definitions,
        "main_member_calls": member_calls,
        "other_function_candidates": free_like,
        "recursive_candidates": unique(recursive_candidates),
        "implementation_signals": signals,
    }


def extract(root: Path, spec: dict, requirements: dict | None) -> dict[str, object]:
    problems = spec.get("problems", [])
    folders = sorted(
        (path for path in root.iterdir() if path.is_dir() and re.fullmatch(r"T\d+", path.name)),
        key=lambda path: int(path.name[1:]),
    )
    manifest_path = root / ".hfut-ds-work" / "manifest.json"
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    rows: list[dict[str, object]] = []
    for index, folder in enumerate(folders):
        problem = problems[index] if index < len(problems) and isinstance(problems[index], dict) else {}
        rows.append(
            {
                "task": folder.name,
                "name": compact(problem.get("name") or folder.name, 120),
                "algorithm_idea": compact(problem.get("algorithm_idea"), 300),
                "steps": [compact(item, 160) for item in problem.get("steps", []) if compact(item, 160)],
                "test_data": [compact(item, 300) for item in problem.get("test_data", []) if compact(item, 300)],
                "result_explanation": [
                    compact(item, 300) for item in problem.get("result_explanation", []) if compact(item, 300)
                ],
                "code": code_facts(folder),
            }
        )
    return {
        "experiment_title": compact(spec.get("experiment_title") or manifest.get("profile") or "数据结构实验", 120),
        "profile": compact(manifest.get("profile") or (requirements or {}).get("suggested_profile") or "custom", 80),
        "problem_count": len(rows),
        "requirement_tasks": [
            compact(item, 500) for item in (requirements or {}).get("candidate_tasks_for_review", []) if compact(item, 500)
        ],
        "problems": rows,
        "privacy_note": "证据文件不保存源码正文、姓名、学号、电话、邮箱或绝对路径。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract concise code and task evidence for an oral-lab viva guide.")
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--requirements", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output_dir.is_dir():
        parser.error("output_dir must exist")
    if not args.spec.is_file():
        parser.error("--spec must be an existing report-spec JSON")
    requirements = read_json(args.requirements) if args.requirements and args.requirements.is_file() else None
    evidence = extract(args.output_dir, read_json(args.spec), requirements)
    if not evidence["problems"]:
        parser.error("no T1...TX project folders found")
    write_json(args.output, evidence)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
