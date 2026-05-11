# Task 2：Detector

本任务实现识别目标板、数字分类与 PnP 位姿估计。

理论讲解请看 [THEORY.md](THEORY.md)。

## 1. 环境准备

基础依赖：

```bash
uv sync --extra vision --extra train --extra dev
```

下载 MNIST 并训练分类器：

```bash
uv run python tasks/task2-detector/src/train.py --download-mnist
uv run python tasks/task2-detector/src/train.py
```

在开始编码之前，请按以下步骤操作：

启动对应平台的预编译 Unity 仿真器：

- Windows: `simulator/Windows/AutoAim.exe`
- Linux: `simulator/Linux/AutoAim.x86_64`
- macOS: `simulator/MacOS.app`

启动方式：

- Windows：双击 `AutoAim.exe`
- macOS：
  ```bash
  chmod +x simulator/MacOS.app/Contents/MacOS/AutoAim
  open simulator/MacOS.app
  ```
- Linux：
  ```bash
  chmod +x simulator/Linux/AutoAim.x86_64
  ./simulator/Linux/AutoAim.x86_64
  ```

运行启动脚本。

```bash
uv run python simulator/runner.py
```

尽管无法正确瞄准，您可以看到这个任务需要识别的目标的大致形态特征，便于了解代码各部分的作用。

## 2. 需要完成

代码位置：

- `tasks/task2-detector/src/detector.py`
- `tasks/task2-detector/src/model.py`
- `tasks/task2-detector/src/train.py`

必须完成（检测主流程）：

1. `detector.py`
- `order_corners(...)`
- `detect_bbox(...)`
- `detect_mnist_board(...)`
- `solve_pnp(...)`

2. `model.py`
- `preprocess_mnist_crop(...)`
- `load_mnist_model(...)`
- `predict_mnist_digit(...)`
- `classify_mnist_digit(...)`

训练：

1. `train.py`
- `select_training_device(...)`
- `train_mnist_classifier(...)`

要求：

- `Detection.corners` 顺序固定为 `LU, RU, RD, LD`。
- `class_id` 在 `[0, 9]`，`confidence` 在 `[0, 1]`。
- `solve_pnp` 需填充 `rvec/tvec`。

## 3. 测试与运行

运行 Task 2 测试：

```bash
uv run pytest tests/python/test_task2_detector.py
uv run pytest tests/python/test_task2_mnist_model.py
```

说明：

- `test_task2_detector.py` 会在 `tasks/task2-detector/test-results/` 输出可视化图，便于排查检测问题。
