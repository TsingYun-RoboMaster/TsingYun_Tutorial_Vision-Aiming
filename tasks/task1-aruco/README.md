# Task 1：相机标定与 ArUco 三维渲染

本任务对应真实相机标定与 ArUco AR 投影，不依赖练枪仿真器流程。

理论讲解请看 [THEORY.md](THEORY.md)。

## 1. 环境准备

```bash
uv sync --extra vision --extra dev
```

准备输入数据：

1. 棋盘格标定图：放到 `tasks/task1-aruco/data/calibration/`。
2. ArUco 视频：放到 `tasks/task1-aruco/data/aruco/`（你自己找/打印 marker，并在视频中清晰可见）。

## 2. 需要完成

代码位置：

- `tasks/task1-aruco/src/calibrate.py`
- `tasks/task1-aruco/src/aruco_render.py`

你需要完成的内容：

1. 在 `calibrate.py` 中配置并实现：
- 配置项：`CALIBRATION_IMAGES_DIR`、`CALIBRATION_IMAGE_GLOB`、`PATTERN_SIZE`、`SQUARE_SIZE_METERS`。
- 函数：`create_board_points(...)`、`detect_calibration_points(...)`、`calibrate_camera(...)`。
2. 在 `aruco_render.py` 中配置并实现：
- 配置项：`CAMERA_PARAMS_PATH`、`ARUCO_VIDEO_PATH`、`ARUCO_DICTIONARY`、`MARKER_LENGTH_METERS`、`MODEL_PATH`。
- 函数：`estimate_marker_pose(...)`、`render_virtual_object(...)`。

提示：`res/models/` 是提供的模型资源，可以直接使用。

## 3. 运行与测试

先做单元测试（可先跑，检查接口和基本行为）：

```bash
uv run pytest tests/python/test_task1_aruco.py
```

说明：仓库里的 `pytest` 会在需要时自动构建 Task 3 的 C++ 目标。Windows 上若安装了 `Ninja`，会优先使用 `build/hw-ninja`。

运行标定：

```bash
uv run python tasks/task1-aruco/src/calibrate.py
```

期望输出：`tasks/task1-aruco/output/camera_params.json`

运行 ArUco 渲染：

```bash
uv run python tasks/task1-aruco/src/aruco_render.py
```

期望输出：`tasks/task1-aruco/output/aruco_result.mp4`

## 4. Demo
[demo video](assets/demo.mp4)

## 5. 提交注意

请只提交代码与必要文档，不要提交你自己的标定图片、原始视频和生成视频。
