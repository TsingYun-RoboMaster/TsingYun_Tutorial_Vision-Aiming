from __future__ import annotations

import argparse
import ast
from pathlib import Path


DEFAULT_PATHS = (
    Path("tasks/task1-aruco/src"),
    Path("tasks/task2-detector/src"),
    Path("tasks/task3-tracker/src"),
    Path("tasks/task4-ballistic/src"),
)


def iter_source_files(paths: list[Path]):
    self_path = Path(__file__).resolve()
    for path in paths:
        if path.resolve() == self_path:
            continue
        if path.is_file():
            yield path
            continue
        if path.is_dir():
            for source_file in sorted(path.rglob("*.py")):
                if source_file.resolve() != self_path:
                    yield source_file
            yield from sorted(path.rglob("*.cpp"))
            yield from sorted(path.rglob("*.hpp"))


def python_notimplemented_lines(path: Path) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            exc = node.exc
            if isinstance(exc, ast.Call):
                exc = exc.func
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                lines.append(node.lineno)
    return lines


def text_notimplemented_lines(path: Path) -> list[int]:
    lines: list[int] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if "NotImplementedError" in line:
            lines.append(lineno)
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail if submitted task code still contains NotImplementedError stubs.")
    parser.add_argument("paths", nargs="*", type=Path, default=list(DEFAULT_PATHS))
    args = parser.parse_args()

    findings: list[tuple[Path, int]] = []
    for source_file in iter_source_files(args.paths):
        if source_file.suffix == ".py":
            lines = python_notimplemented_lines(source_file)
        else:
            lines = text_notimplemented_lines(source_file)
        findings.extend((source_file, line) for line in lines)

    if findings:
        print("Submission still contains NotImplementedError stubs:")
        for path, line in findings:
            print(f"  {path}:{line}")
        return 1

    print("No NotImplementedError stubs found in task source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
