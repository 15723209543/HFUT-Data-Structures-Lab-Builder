from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from hfut_ds_common import detect_profile, docx_body_paragraphs, redact_pii, sha256_file


def locate(rows: list[dict[str, object]], keyword: str) -> int | None:
    for row in rows:
        if keyword in str(row["text"]):
            return int(row["body_index"])
    return None


def candidate_tasks(rows: list[dict[str, object]]) -> list[str]:
    start = locate(rows, "实验任务")
    end_candidates = [
        locate(rows, "算法设计与实现描述"),
        locate(rows, "运行结果截图及说明"),
    ]
    ends = [value for value in end_candidates if value is not None]
    end = min(ends) if ends else 10**9
    candidates: list[str] = []
    for row in rows:
        index = int(row["body_index"])
        text = str(row["text"])
        style = str(row["style"])
        if not text or (start is not None and index <= start) or index >= end:
            continue
        looks_numbered = bool(re.match(r"^(?:[（(]?\d+[）).、]|<\d+>)", text))
        looks_list = "List" in style and len(text) >= 12
        if looks_numbered or looks_list:
            if any(word in text for word in ("实验测试数据", "第一组", "第二组", "第三组")):
                continue
            candidates.append(redact_pii(text[:500]))
    return candidates


def inspect(path: Path) -> dict:
    rows = docx_body_paragraphs(path)
    all_text = "\n".join(str(row["text"]) for row in rows)
    profile, default_count, evidence = detect_profile(all_text)
    first_text = next((str(row["text"]) for row in rows if str(row["text"])), path.stem)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        media = [name for name in names if name.startswith("word/media/")]
        embeddings = [name for name in names if name.startswith("word/embeddings/")]
    headings = {
        "algorithm_design": locate(rows, "算法设计与实现描述"),
        "results": locate(rows, "运行结果截图及说明"),
        "reflection": next(
            (
                int(row["body_index"])
                for row in rows
                if "总结" in str(row["text"]) and "心得" in str(row["text"]) and "建议" in str(row["text"])
            ),
            None,
        ),
    }
    warnings: list[str] = []
    if any(value is None for value in headings.values()):
        warnings.append("未完整定位报告后三个语义章节，填充前必须人工检查。")
    if profile is None:
        warnings.append("未唯一匹配内置 starter profile；不要自动套用教师代码。")
    return {
        "source": str(path.resolve()),
        "sha256": sha256_file(path),
        "title": redact_pii(first_text),
        "paragraph_count": len(rows),
        "headings": headings,
        "suggested_profile": profile,
        "profile_evidence": evidence,
        "default_problem_count": default_count,
        "candidate_tasks_for_review": candidate_tasks(rows),
        "media_count": len(media),
        "embedded_objects": embeddings,
        "has_removable_appendix": "提交报告时去掉" in all_text and "附录" in all_text,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect an HFUT data-structures requirement DOCX.")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.docx.is_file() or args.docx.suffix.lower() != ".docx":
        parser.error("docx must be an existing .docx file")
    result = inspect(args.docx)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
