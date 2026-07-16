from __future__ import annotations

import argparse
from pathlib import Path

from hfut_ds_common import (
    STUDENT_DECL_BEGIN,
    STUDENT_DECL_END,
    STUDENT_IMPL_BEGIN,
    STUDENT_IMPL_END,
)


def patch_bytes(target: Path, begin: str, end: str, content: str) -> None:
    data = target.read_bytes()
    begin_bytes = begin.encode("gbk")
    end_bytes = end.encode("gbk")
    start = data.find(begin_bytes)
    if start < 0:
        raise ValueError(f"begin marker not found in {target}: {begin}")
    finish = data.find(end_bytes, start + len(begin_bytes))
    if finish < 0:
        raise ValueError(f"end marker not found in {target}: {end}")
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    replacement = begin_bytes + b"\r\n"
    if normalized:
        replacement += normalized.replace("\n", "\r\n").encode("gbk", errors="strict") + b"\r\n"
    replacement += end_bytes
    target.write_bytes(data[:start] + replacement + data[finish + len(end_bytes) :])


def main() -> int:
    parser = argparse.ArgumentParser(description="Replace a student region in a GBK starter without touching its teacher prefix.")
    parser.add_argument("target", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--declarations", type=Path, help="UTF-8 file containing class declarations")
    group.add_argument("--implementation", type=Path, help="UTF-8 file containing C++ implementation")
    args = parser.parse_args()
    source = args.declarations or args.implementation
    content = source.read_text(encoding="utf-8")
    if args.declarations:
        patch_bytes(args.target, STUDENT_DECL_BEGIN, STUDENT_DECL_END, content)
    else:
        patch_bytes(args.target, STUDENT_IMPL_BEGIN, STUDENT_IMPL_END, content)
    print(args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
