import importlib.util
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


calibrate = load_module("task1_calibrate", "tasks/task1-aruco/src/calibrate.py")
aruco_render = load_module("task1_aruco_render", "tasks/task1-aruco/src/aruco_render.py")


def call_or_skip_stub(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except NotImplementedError as exc:
        import pytest

        pytest.skip(f"student stub is not implemented yet: {exc}")


def test_create_board_points_uses_chessboard_row_major_order():
    points = call_or_skip_stub(calibrate.create_board_points, (3, 2), 0.5)

    assert points.shape == (6, 3)
    assert points.dtype == np.float32
    assert points.tolist() == [
        [0.0, 0.0, 0.0],
        [0.5, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.5, 0.0],
        [0.5, 0.5, 0.0],
        [1.0, 0.5, 0.0],
    ]


def test_task1_has_no_zhang_calibration_hook():
    assert not hasattr(calibrate, "calibrate_camera_zhang_optional")


def test_calibrate_camera_uses_opencv_calibrate_camera(monkeypatch):
    expected_matrix = np.array(
        [[700.0, 0.0, 320.0], [0.0, 710.0, 240.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    expected_dist = np.array([[0.1], [0.01], [0.0], [0.0], [0.0]], dtype=np.float64)

    def fake_opencv(object_points, image_points, image_size, camera_matrix, dist_coeffs):
        return 0.25, expected_matrix, expected_dist, [], []

    monkeypatch.setattr(calibrate.cv2, "calibrateCamera", fake_opencv)

    camera_matrix, dist_coeffs = call_or_skip_stub(
        calibrate.calibrate_camera,
        [np.zeros((4, 3), dtype=np.float32)],
        [np.zeros((4, 1, 2), dtype=np.float32)],
        (640, 480),
    )

    assert np.array_equal(camera_matrix, expected_matrix)
    assert np.array_equal(dist_coeffs, expected_dist)


def test_load_obj_parses_vertices_and_faces(tmp_path):
    model_path = tmp_path / "model.obj"
    model_path.write_text(
        "\n".join(
            [
                "# tiny triangle",
                "v 0 0 0",
                "v 1 0 0",
                "v 0 1 0",
                "vt 0 0",
                "vn 0 0 1",
                "f 1/1/1 2/1/1 3/1/1",
            ]
        ),
        encoding="utf-8",
    )

    vertices, faces = call_or_skip_stub(aruco_render.load_obj, model_path)

    assert vertices == [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    assert faces == [(0, 1, 2)]


def test_task1_has_no_self_pnp_hook():
    assert not hasattr(aruco_render, "solve_pnp_optional")


def test_estimate_marker_pose_uses_opencv_solve_pnp(monkeypatch):
    expected_rvec = np.array([[0.0], [0.0], [0.0]], dtype=np.float64)
    expected_tvec = np.array([[0.0], [0.0], [0.5]], dtype=np.float64)

    def fake_opencv(object_points, image_points, camera_matrix, dist_coeffs, flags):
        assert object_points.shape == (4, 3)
        assert image_points.shape == (4, 2)
        assert flags == aruco_render.cv2.SOLVEPNP_IPPE_SQUARE
        return True, expected_rvec, expected_tvec

    monkeypatch.setattr(aruco_render.cv2, "solvePnP", fake_opencv)

    rvec, tvec = call_or_skip_stub(
        aruco_render.estimate_marker_pose,
        np.array([[[10.0, 20.0], [30.0, 20.0], [30.0, 40.0], [10.0, 40.0]]], dtype=np.float32),
        0.05,
        np.eye(3, dtype=np.float64),
        np.zeros((5, 1), dtype=np.float64),
    )

    assert np.array_equal(rvec, expected_rvec)
    assert np.array_equal(tvec, expected_tvec)
