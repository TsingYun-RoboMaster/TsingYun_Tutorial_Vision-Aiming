from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_DIR = REPO_ROOT / "build" / "hw"
WINDOWS_NINJA_BUILD_DIR = REPO_ROOT / "build" / "hw-ninja"


def _read_generator(cache_path: Path) -> str | None:
    if not cache_path.exists():
        return None

    for line in cache_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("CMAKE_GENERATOR:INTERNAL="):
            return line.split("=", 1)[1].strip()
    return None


def _cmake_configure(build_dir: Path, extra_args: list[str]) -> None:
    subprocess.run(
        [
            "cmake",
            "-S",
            str(REPO_ROOT),
            "-B",
            str(build_dir),
            "-DHW_BUILD_TESTS=ON",
            *extra_args,
        ],
        check=True,
        cwd=REPO_ROOT,
    )


def _cmake_build(build_dir: Path, config: str | None = None) -> None:
    command = ["cmake", "--build", str(build_dir)]
    if config is not None:
        command.extend(["--config", config])

    subprocess.run(command, check=True, cwd=REPO_ROOT)


def _ensure_windows_ninja_build() -> None:
    if shutil.which("ninja") is None:
        raise FileNotFoundError("ninja was not found on PATH")

    cache_path = WINDOWS_NINJA_BUILD_DIR / "CMakeCache.txt"
    if _read_generator(cache_path) != "Ninja":
        _cmake_configure(WINDOWS_NINJA_BUILD_DIR, ["-G", "Ninja"])

    _cmake_build(WINDOWS_NINJA_BUILD_DIR)
    os.environ["TSINGYUN_HW_BUILD_DIR"] = str(WINDOWS_NINJA_BUILD_DIR)


def _ensure_default_build() -> None:
    cache_path = DEFAULT_BUILD_DIR / "CMakeCache.txt"
    generator = _read_generator(cache_path)

    if generator is None:
        _cmake_configure(DEFAULT_BUILD_DIR, [])
        generator = _read_generator(cache_path)

    config = "Debug" if generator and "Visual Studio" in generator else None
    _cmake_build(DEFAULT_BUILD_DIR, config=config)
    os.environ["TSINGYUN_HW_BUILD_DIR"] = str(DEFAULT_BUILD_DIR)


def pytest_sessionstart(session) -> None:
    if sys.platform == "win32":
        _ensure_windows_ninja_build()
        return

    _ensure_default_build()


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--run-task2-training",
        action="store_true",
        default=False,
        help="Run slow Task 2 MNIST training tests.",
    )


def pytest_configure(config) -> None:
    config.addinivalue_line(
        "markers",
        "task2_training: marks tests that run real Task 2 MNIST training",
    )


def pytest_collection_modifyitems(config, items) -> None:
    if config.getoption("--run-task2-training"):
        return

    skip_training = pytest.mark.skip(reason="use --run-task2-training to run real Task 2 training tests")
    for item in items:
        if "task2_training" in item.keywords:
            item.add_marker(skip_training)
