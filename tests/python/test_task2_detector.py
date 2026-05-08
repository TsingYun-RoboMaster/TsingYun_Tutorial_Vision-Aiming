from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pytest

from detector import Detection, detect_mnist_board


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK2_ROOT = REPO_ROOT / "tasks" / "task2-detector"
RESULTS_DIR = TASK2_ROOT / "test-results"
SCREENSHOT_SIZE = (360, 640)
DETECTION_THRESHOLD = 200


def _as_image_like(frame_rgb: np.ndarray) -> np.ndarray:
    return frame_rgb


def _load_mnist_digit(digit: int) -> np.ndarray:
    digit_dir = REPO_ROOT / "simulator" / "MNIST" / str(digit)
    image_path = sorted(digit_dir.glob("*.png"))[0]
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise AssertionError(f"Cannot read MNIST asset: {image_path}")
    return image


def _make_game_screenshot(digit: int, bbox: tuple[int, int, int, int]) -> np.ndarray:
    frame = np.full((*SCREENSHOT_SIZE, 3), (24, 28, 34), dtype=np.uint8)
    x, y, width, height = bbox

    cv2.rectangle(frame, (x, y), (x + width - 1, y + height - 1), (245, 38, 38), thickness=-1)
    cv2.rectangle(frame, (x + 8, y + 8), (x + width - 9, y + height - 9), (18, 18, 18), thickness=-1)

    digit_image = _load_mnist_digit(digit)
    digit_size = min(width, height) - 34
    digit_image = cv2.resize(digit_image, (digit_size, digit_size), interpolation=cv2.INTER_AREA)
    digit_rgb = cv2.cvtColor(digit_image, cv2.COLOR_GRAY2RGB)

    top = y + (height - digit_size) // 2
    left = x + (width - digit_size) // 2
    mask = digit_image > 8
    frame[top : top + digit_size, left : left + digit_size][mask] = digit_rgb[mask]
    return frame


def _take_game_screenshots() -> list[np.ndarray]:
    return [
        _make_game_screenshot(digit=3, bbox=(120, 78, 112, 92)),
        _make_game_screenshot(digit=7, bbox=(340, 164, 128, 104)),
        _make_game_screenshot(digit=1, bbox=(238, 106, 96, 116)),
    ]


def _result_path() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        path = RESULTS_DIR / f"{timestamp}.png"
        if not path.exists():
            return path


def _draw_detections(frame_rgb: np.ndarray, detections: list[Detection], threshold: int, status: str | None = None) -> np.ndarray:
    output = frame_rgb.copy()
    header = f"threshold={threshold} detections={len(detections)}"
    cv2.putText(output, header, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    if status:
        cv2.putText(output, status, (12, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 220, 80), 2, cv2.LINE_AA)

    for index, detection in enumerate(detections):
        x0 = int(round(detection.bbox.x))
        y0 = int(round(detection.bbox.y))
        x1 = int(round(detection.bbox.x + detection.bbox.width - 1))
        y1 = int(round(detection.bbox.y + detection.bbox.height - 1))

        cv2.rectangle(output, (x0, y0), (x1, y1), (58, 235, 86), 2)
        corner_points = np.array(detection.corners, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(output, [corner_points], isClosed=True, color=(72, 196, 255), thickness=2)

        label = (
            f"#{index} class={detection.class_id} "
            f"conf={detection.confidence:.2f} threshold={threshold} "
            f"bbox=({x0},{y0},{x1 - x0 + 1},{y1 - y0 + 1})"
        )
        cv2.putText(output, label, (x0, max(18, y0 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 2, cv2.LINE_AA)

    return output


def test_task2_detector_writes_timestamped_visual_results():
    screenshots = _take_game_screenshots()
    written_paths: list[Path] = []
    all_detections: list[Detection] = []
    not_implemented_reason: str | None = None

    for screenshot in screenshots:
        try:
            detections = detect_mnist_board(_as_image_like(screenshot), threshold=DETECTION_THRESHOLD)
        except NotImplementedError as exc:
            detections = []
            not_implemented_reason = f"student TODO not implemented: {exc}"

        all_detections.extend(detections)
        overlay = _draw_detections(screenshot, detections, DETECTION_THRESHOLD, status=not_implemented_reason)
        output_path = _result_path()
        ok = cv2.imwrite(str(output_path), cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        assert ok, f"failed to write detector visualization: {output_path}"
        written_paths.append(output_path)

    assert len(written_paths) == len(screenshots)
    assert len({path.name for path in written_paths}) == len(written_paths)
    assert all(path.exists() for path in written_paths)

    if not_implemented_reason:
        pytest.skip(not_implemented_reason)

    assert all_detections, f"detector produced no detections; visual results are in {RESULTS_DIR}"
