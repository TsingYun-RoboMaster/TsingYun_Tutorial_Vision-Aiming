"""Typed helpers for the Unity simulator line-delimited JSON protocol."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, TextIO


Matrix3x3 = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]


@dataclass(frozen=True)
class StartMessage:
    seed: int
    latency: float
    camera_matrix: Matrix3x3


@dataclass(frozen=True)
class ConfigMessage:
    board_width: float
    board_height: float


@dataclass(frozen=True)
class FrameMessage:
    frame_id: int
    timestamp: float
    image_bytes: bytes


@dataclass(frozen=True)
class AimMessage:
    x: float
    y: float
    z: float
    detections: list[dict[str, Any]] | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": "aim", "x": self.x, "y": self.y, "z": self.z}
        if self.detections is not None:
            payload["detections"] = self.detections
        return payload


@dataclass(frozen=True)
class EndMessage:
    score: float
    accuracy: float
    average_to_center_distance: float


SimulatorMessage = StartMessage | ConfigMessage | FrameMessage | AimMessage | EndMessage


def _matrix_from_flat(values: list[Any]) -> Matrix3x3:
    if len(values) != 9:
        raise ValueError(f"cameraMatrix must contain 9 values, got {len(values)}")
    nums = tuple(float(value) for value in values)
    return (
        (nums[0], nums[1], nums[2]),
        (nums[3], nums[4], nums[5]),
        (nums[6], nums[7], nums[8]),
    )


def flatten_matrix(matrix: Matrix3x3) -> list[float]:
    return [value for row in matrix for value in row]


def start_payload(seed: int, latency: float, camera_matrix: Matrix3x3) -> dict[str, Any]:
    return {
        "type": "start",
        "seed": int(seed),
        "latency": float(latency),
        "cameraMatrix": flatten_matrix(camera_matrix),
    }


def parse_message(payload: dict[str, Any]) -> SimulatorMessage:
    message_type = payload.get("type")
    if message_type == "start":
        return StartMessage(
            seed=int(payload["seed"]),
            latency=float(payload["latency"]),
            camera_matrix=_matrix_from_flat(list(payload["cameraMatrix"])),
        )
    if message_type == "config":
        return ConfigMessage(
            board_width=float(payload["boardWidth"]),
            board_height=float(payload["boardHeight"]),
        )
    if message_type == "frame":
        return FrameMessage(
            frame_id=int(payload["frameId"]),
            timestamp=float(payload["timestamp"]),
            image_bytes=base64.b64decode(str(payload["imageBase64"])),
        )
    if message_type == "aim":
        return AimMessage(x=float(payload["x"]), y=float(payload["y"]), z=float(payload["z"]))
    if message_type == "end":
        return EndMessage(
            score=float(payload["score"]),
            accuracy=float(payload["accuracy"]),
            average_to_center_distance=float(payload["average_to_center_distance"]),
        )
    raise ValueError(f"Unsupported message type: {message_type!r}")


def read_message(sock_file: TextIO) -> SimulatorMessage | None:
    line = sock_file.readline()
    if not line:
        return None
    return parse_message(json.loads(line))


def write_payload(sock_file: TextIO, payload: dict[str, Any]) -> None:
    sock_file.write(json.dumps(payload) + "\n")
    sock_file.flush()
