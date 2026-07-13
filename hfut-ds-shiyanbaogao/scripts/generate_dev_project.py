from __future__ import annotations

import argparse
from pathlib import Path

from hfut_ds_common import strict_gbk_write


COMPILABLE = {".c", ".cc", ".cpp", ".cxx"}
LINKABLE = COMPILABLE
INCLUDED = COMPILABLE | {".h", ".hpp", ".txt", ".btr", ".tre", ".grp"}


def build(project_dir: Path, name: str) -> Path:
    files = sorted(
        (path for path in project_dir.iterdir() if path.is_file() and path.suffix.lower() in INCLUDED),
        key=lambda path: (path.name.lower() != "main.cpp", path.suffix.lower(), path.name.lower()),
    )
    if not files:
        raise ValueError(f"no project files found in {project_dir}")
    target = project_dir / f"{name}.dev"
    lines = [
        "[Project]",
        f"FileName={target.name}",
        f"Name={name}",
        "Type=1",
        "Ver=2",
        "ObjFiles=",
        "Includes=",
        "Libs=",
        "PrivateResource=",
        "ResourceIncludes=",
        "MakeIncludes=",
        "Compiler=",
        "CppCompiler=",
        "Linker=",
        "IsCpp=1",
        "Icon=",
        "ExeOutput=",
        "ObjectOutput=",
        "LogOutput=",
        "LogOutputEnabled=0",
        "OverrideOutput=0",
        "OverrideOutputName=",
        "HostApplication=",
        "UseCustomMakefile=0",
        "CustomMakefile=",
        "CommandLine=",
        "Folders=",
        "IncludeVersionInfo=0",
        "SupportXPThemes=0",
        "CompilerSet=1",
        "CompilerSettings=0000000000000000001000000",
        f"UnitCount={len(files)}",
        "",
        "[VersionInfo]",
        "Major=1",
        "Minor=0",
        "Release=0",
        "Build=0",
        "LanguageID=2052",
        "CharsetID=936",
        "CompanyName=",
        "FileVersion=",
        "FileDescription=Dev-C++ project",
        "InternalName=",
        "LegalCopyright=",
        "LegalTrademarks=",
        "OriginalFilename=",
        "ProductName=",
        "ProductVersion=",
        "AutoIncBuildNr=0",
        "SyncProduct=1",
        "",
    ]
    for index, path in enumerate(files, 1):
        compile_flag = 1 if path.suffix.lower() in COMPILABLE else 0
        link_flag = 1 if path.suffix.lower() in LINKABLE else 0
        lines.extend(
            [
                f"[Unit{index}]",
                f"FileName={path.name}",
                *( ["CompileCpp=1"] if compile_flag else [] ),
                "Folder=",
                f"Compile={compile_flag}",
                f"Link={link_flag}",
                "Priority=1000",
                "OverrideBuildCmd=0",
                "BuildCmd=",
                "",
            ]
        )
    strict_gbk_write(target, "\n".join(lines))
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a GBK Dev-C++ project file.")
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--name")
    args = parser.parse_args()
    if not args.project_dir.is_dir():
        parser.error("project_dir must exist")
    target = build(args.project_dir, args.name or args.project_dir.name)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
