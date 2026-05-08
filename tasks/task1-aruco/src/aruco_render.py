import json
from pathlib import Path

import cv2
import numpy as np

TASK_ROOT = Path(__file__).resolve().parents[1]

# TODO(student): fill in your camera parameter file from calibrate.py.
# run calibrate.py first and point this path at the generated camera_params.json
# the JSON must contain camera_matrix and dist_coeffs
CAMERA_PARAMS_PATH = TASK_ROOT / "output" / "camera_params.json"

# TODO(student): fill in your own ArUco video path.
# use a video where the marker is clear and not too motion-blurred
# keep the marker dictionary and physical length below consistent with this video
ARUCO_VIDEO_PATH = TASK_ROOT / "data" / "aruco" / "aruco.mp4"

# TODO(student): fill in your own ArUco settings.
# choose the same dictionary that was used to print the marker
# measure the black marker side length in meters and store it in MARKER_LENGTH_METERS
ARUCO_DICTIONARY = "DICT_4X4_50"
MARKER_LENGTH_METERS = 0.05

ARUCO_OUTPUT_VIDEO_PATH = TASK_ROOT / "output" / "aruco_result.mp4"

# TODO(student): use this path if you want to render one of the provided OBJ models.
# start with cube.obj while debugging because its shape makes pose errors obvious
# after the pose is stable, switch to another OBJ model from res/models
MODEL_PATH = TASK_ROOT / "res" / "models" / "cube.obj"
OUTPUT_DIR = TASK_ROOT / "output"


def load_camera_params(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    camera_matrix = np.array(data["camera_matrix"], dtype=np.float32)
    dist_coeffs = np.array(data["dist_coeffs"], dtype=np.float32)
    return camera_matrix, dist_coeffs


def load_obj(model_path):
    """Load the vertices and faces from a small OBJ model."""
    # TODO(student): Parse OBJ vertices and faces.
    # if model_path does not exist:
    #     raise a clear error
    # vertices = []
    # faces = []
    # for each line in the OBJ file:
    #     if line is blank or starts with "#":
    #         continue
    #     if line starts with "v ":
    #         parts = split the line by whitespace
    #         if parts does not contain exactly x, y, and z:
    #             raise a clear error with the OBJ line number
    #         vertex = convert x, y, z to floats
    #         append vertex to vertices
    #     else if line starts with "f ":
    #         parts = split the line and ignore the leading "f"
    #         if the face has fewer than 3 vertices:
    #             raise a clear error
    #         indices = empty list
    #         for each face token:
    #             vertex_text = text before the first slash
    #             obj_index = convert vertex_text to integer
    #             if obj_index is positive:
    #                 python_index = obj_index - 1 because OBJ indices start at 1
    #             else:
    #                 python_index = len(vertices) + obj_index because negative OBJ indices are relative
    #             append python_index to indices
    #         triangulate the polygon with a fan:
    #             for i from 1 to len(indices) - 2:
    #                 append (indices[0], indices[i], indices[i + 1]) to faces
    #     else:
    #         ignore unsupported OBJ records such as vt, vn, and usemtl
    # return vertices, faces
    raise NotImplementedError("load_obj is not implemented")


def get_aruco_dictionary(name):
    if not hasattr(cv2.aruco, name):
        raise ValueError(f"Unknown ArUco dictionary: {name}")
    return cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, name))


def detect_markers(frame, dictionary):
    if hasattr(cv2.aruco, "ArucoDetector"):
        detector = cv2.aruco.ArucoDetector(dictionary)
        corners, ids, _ = detector.detectMarkers(frame)
    else:
        corners, ids, _ = cv2.aruco.detectMarkers(frame, dictionary)
    return corners, ids


def create_marker_object_points(marker_length_meters):
    half = marker_length_meters * 0.5
    return np.array(
        [
            [-half, half, 0.0],
            [half, half, 0.0],
            [half, -half, 0.0],
            [-half, -half, 0.0],
        ],
        dtype=np.float32,
    )


def _is_valid_pose_result(result):
    if result is None:
        return False
    if not isinstance(result, tuple) or len(result) != 2:
        return False
    rvec, tvec = result
    rvec = np.asarray(rvec)
    tvec = np.asarray(tvec)
    return rvec.size == 3 and tvec.size == 3 and np.all(np.isfinite(rvec)) and np.all(np.isfinite(tvec))


def estimate_marker_pose(marker_corners, marker_length_meters, camera_matrix, dist_coeffs):
    # TODO(student): Estimate one marker pose with OpenCV solvePnP.
    # object_points = four 3D marker corners on the marker plane
    # image_points = detected marker corners reshaped to four 2D pixel coordinates
    # call cv2.solvePnP with object_points, image_points, camera_matrix, and dist_coeffs
    # if OpenCV reports failure:
    #     raise a clear error
    # return rvec and tvec
    raise NotImplementedError("estimate_marker_pose is not implemented")


def render_virtual_object(frame, rvec, tvec, camera_matrix, dist_coeffs, vertices, faces):
    # TODO(student): Render the loaded OBJ model on top of the ArUco marker.
    # if vertices or faces are empty:
    #     return frame unchanged
    # vertices_array = convert vertices to a float32 Nx3 array
    # center = average of the model vertices
    # centered_vertices = vertices_array - center
    # size = largest side length of the centered model bounding box
    # if size is too small:
    #     return frame unchanged
    # scale = MARKER_LENGTH_METERS / size
    # model_points = centered_vertices * scale
    # flip the model y/z axes if needed so it appears above the marker plane
    # projected_points = cv2.projectPoints(model_points, rvec, tvec, camera_matrix, dist_coeffs)
    # pixels = round projected_points to integer pixel coordinates
    # for each triangle face:
    #     collect the three projected pixel points
    #     draw the triangle outline on frame
    # return frame
    raise NotImplementedError("render_virtual_object is not implemented")


def process_frame(frame, dictionary, camera_matrix, dist_coeffs, vertices, faces):
    output = frame.copy()
    corners, ids = detect_markers(frame, dictionary)

    if ids is None or len(ids) == 0:
        return output

    cv2.aruco.drawDetectedMarkers(output, corners, ids)

    for marker_corners, _ in zip(corners, ids):
        rvec, tvec = estimate_marker_pose(
            marker_corners,
            MARKER_LENGTH_METERS,
            camera_matrix,
            dist_coeffs,
        )
        render_virtual_object(
            output,
            rvec,
            tvec,
            camera_matrix,
            dist_coeffs,
            vertices,
            faces,
        )

    return output


def run_aruco_render(dictionary, camera_matrix, dist_coeffs, capture, vertices, faces):
    ok, frame = capture.read()
    if not ok:
        raise SystemExit("Cannot read the first frame from the source.")

    height, width = frame.shape[:2]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(ARUCO_OUTPUT_VIDEO_PATH),
        cv2.VideoWriter_fourcc(*"mp4v"),
        30.0,
        (width, height),
    )

    try:
        while ok:
            result = process_frame(frame, dictionary, camera_matrix, dist_coeffs, vertices, faces)
            writer.write(result)
            cv2.imshow("aruco", result)

            if cv2.waitKey(1) & 0xFF == 27:
                break

            ok, frame = capture.read()
    finally:
        writer.release()
        capture.release()
        cv2.destroyAllWindows()

    print(f"Saved video result to: {ARUCO_OUTPUT_VIDEO_PATH}")


def main():
    if not CAMERA_PARAMS_PATH.exists():
        raise SystemExit(f"Camera parameters not found: {CAMERA_PARAMS_PATH}")

    camera_matrix, dist_coeffs = load_camera_params(CAMERA_PARAMS_PATH)
    vertices, faces = load_obj(MODEL_PATH)
    dictionary = get_aruco_dictionary(ARUCO_DICTIONARY)
    capture = cv2.VideoCapture(str(ARUCO_VIDEO_PATH))

    if not capture.isOpened():
        raise SystemExit(f"Cannot open video: {ARUCO_VIDEO_PATH}")

    run_aruco_render(dictionary, camera_matrix, dist_coeffs, capture, vertices, faces)


if __name__ == "__main__":
    main()
