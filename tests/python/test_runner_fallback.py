import numpy as np

from detector import BoundingBox, Detection
from simulator_client.pipeline import FallbackPipeline, PipelineResult
from simulator_client.protocol import AimMessage


def test_pipeline_uses_detection_when_available():
    pipeline = FallbackPipeline(target_depth=8.0)
    image = np.array([
        [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
        [(0, 0, 0), (255, 0, 0), (0, 0, 0)],
        [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
    ], dtype=np.uint8)
    camera_matrix = ((100.0, 0.0, 1.5), (0.0, 100.0, 1.5), (0.0, 0.0, 1.0))

    result = pipeline.process_rgb_image(image, camera_matrix)

    assert isinstance(result, PipelineResult)
    assert isinstance(result.aim.x, float)
    assert isinstance(result.aim.y, float)
    assert isinstance(result.aim.z, float)


def test_pipeline_reports_detection_when_student_detector_returns_detection(monkeypatch):
    def fake_detector(image, threshold):
        return [
            Detection(
                class_id=-1,
                confidence=1.0,
                bbox=BoundingBox(x=1.0, y=1.0, width=1.0, height=1.0),
                corners=((1.0, 1.0), (1.0, 1.0), (1.0, 1.0), (1.0, 1.0)),
                tvec=((0.0,), (0.0,), (8.0,)),
            )
        ]

    monkeypatch.setattr("simulator_client.pipeline.detect_mnist_board", fake_detector)

    pipeline = FallbackPipeline(target_depth=8.0)
    image = np.array([
        [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
        [(0, 0, 0), (255, 0, 0), (0, 0, 0)],
        [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
    ], dtype=np.uint8)
    camera_matrix = ((100.0, 0.0, 1.5), (0.0, 100.0, 1.5), (0.0, 0.0, 1.0))

    result = pipeline.process_rgb_image(image, camera_matrix)

    assert isinstance(result, PipelineResult)
    assert result.used_fallback is False
    assert isinstance(result.aim.x, float)
    assert isinstance(result.aim.z, float)


def test_pipeline_falls_back_to_center_ray_when_detection_missing():
    pipeline = FallbackPipeline(target_depth=8.0)
    image = np.array([[(0, 0, 0), (0, 0, 0)]], dtype=np.uint8)
    camera_matrix = ((100.0, 0.0, 1.0), (0.0, 100.0, 0.5), (0.0, 0.0, 1.0))

    result = pipeline.process_rgb_image(image, camera_matrix)

    assert result.used_fallback is True
    assert isinstance(result.aim.x, float)
    assert isinstance(result.aim.z, float)


def test_pipeline_reports_not_implemented_as_student_fallback(monkeypatch):
    def missing_detector(image, threshold):
        raise NotImplementedError("detect_mnist_board")

    monkeypatch.setattr("simulator_client.pipeline.detect_mnist_board", missing_detector)

    pipeline = FallbackPipeline(target_depth=8.0)
    image = np.array([[(0, 0, 0), (0, 0, 0)]], dtype=np.uint8)
    camera_matrix = ((100.0, 0.0, 1.0), (0.0, 100.0, 0.5), (0.0, 0.0, 1.0))

    result = pipeline.process_rgb_image(image, camera_matrix)

    assert result.used_fallback is True
    assert isinstance(result.aim.x, float)
    assert isinstance(result.aim.z, float)
    assert result.reason == "student function not implemented: detect_mnist_board"
