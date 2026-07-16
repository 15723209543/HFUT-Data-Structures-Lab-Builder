from __future__ import annotations

import argparse
from pathlib import Path

from hfut_ds_common import strict_gbk_write


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a UTF-8 text file as strict GBK with CRLF.")
    parser.add_argument("utf8_input", type=Path)
    parser.add_argument("gbk_output", type=Path)
    args = parser.parse_args()
    text = args.utf8_input.read_text(encoding="utf-8")
    strict_gbk_write(args.gbk_output, text, crlf=True)
    print(args.gbk_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
