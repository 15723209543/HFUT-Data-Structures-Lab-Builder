from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from generate_dev_project import build as build_dev_project
from hfut_ds_common import (
    STUDENT_DECL_BEGIN,
    STUDENT_DECL_END,
    STUDENT_IMPL_BEGIN,
    STUDENT_IMPL_END,
    safe_filename,
    strict_gbk_write,
    teacher_prefix_record,
    write_json,
)
from inspect_requirements import inspect


def generic_scaffold(folder: Path) -> None:
    header = f"""#ifndef EXPERIMENT_TASK_H
#define EXPERIMENT_TASK_H

class ExperimentTask {{
public:
    ExperimentTask();
    {STUDENT_DECL_BEGIN}
    {STUDENT_DECL_END}
}};

#endif
"""
    implementation = f"""#include \"ExperimentTask.h\"

ExperimentTask::ExperimentTask() {{
}}

{STUDENT_IMPL_BEGIN}
{STUDENT_IMPL_END}
"""
    main = """#include <iostream>
#include \"ExperimentTask.h\"
using namespace std;

int main() {
    // 仅在此处准备测试数据、创建对象并调用公开成员函数。
    ExperimentTask task;
    return 0;
}
"""
    strict_gbk_write(folder / "ExperimentTask.h", header)
    strict_gbk_write(folder / "ExperimentTask.cpp", implementation)
    strict_gbk_write(folder / "main.cpp", main)


def prepare(requirement: Path, output_dir: Path, problems: int, profile: str) -> dict:
    if problems < 1 or problems > 99:
        raise ValueError("problems must be between 1 and 99")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir = output_dir / ".hfut-ds-work"
    work_dir.mkdir()
    inspection = inspect(requirement)
    selected_profile = inspection.get("suggested_profile") if profile == "auto" else profile
    title = safe_filename(str(inspection.get("title") or requirement.stem))
    if title.lower().endswith(".docx"):
        title = title[:-5]
    report_name = safe_filename(f"{title}-实验报告") + ".docx"
    shutil.copy2(requirement, work_dir / "report-base.docx")
    write_json(work_dir / "requirements.json", inspection)

    skill_dir = Path(__file__).resolve().parent.parent
    starter_root = skill_dir / "assets" / "starters" / str(selected_profile)
    used_starter = starter_root.is_dir()
    teacher_records: list[dict[str, object]] = []
    for index in range(1, problems + 1):
        target = output_dir / f"T{index}"
        source = starter_root / f"T{index}"
        if used_starter and source.is_dir():
            shutil.copytree(source, target)
        else:
            target.mkdir()
            generic_scaffold(target)
        for path in target.iterdir():
            if not path.is_file():
                continue
            record = teacher_prefix_record(path)
            if record:
                record["path"] = str(path.relative_to(output_dir)).replace("\\", "/")
                teacher_records.append(record)
        build_dev_project(target, f"T{index}")

    manifest = {
        "requirement_source": str(requirement.resolve()),
        "requirement_sha256": inspection["sha256"],
        "profile": selected_profile if used_starter else None,
        "problem_count": problems,
        "report_name": report_name,
        "teacher_prefixes": teacher_records,
    }
    write_json(work_dir / "manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare T1...TX folders and a copied report base.")
    parser.add_argument("requirement_docx", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--problems", type=int, required=True)
    parser.add_argument("--profile", default="auto")
    args = parser.parse_args()
    if not args.requirement_docx.is_file() or args.requirement_docx.suffix.lower() != ".docx":
        parser.error("requirement_docx must be an existing DOCX")
    manifest = prepare(args.requirement_docx, args.output_dir, args.problems, args.profile)
    print(f"Prepared {args.output_dir}")
    print(f"Profile: {manifest['profile'] or 'generic'}")
    print(f"Problems: {manifest['problem_count']}")
    print(f"Final report name: {manifest['report_name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
