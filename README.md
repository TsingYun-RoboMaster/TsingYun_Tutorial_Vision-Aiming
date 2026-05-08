# TsingYun Vision Aiming Tutorial

青云战队 2027 赛季视觉组自瞄培训仓库。

## 1. 如何完成作业

1. Fork 本仓库到自己的 GitHub 账号下。
2. Clone 你的 Fork 到本地。
3. 在本地完成作业，实现并测试代码。
4. 提交并推送到你的 Fork。
5. 在 GitHub 上向原仓库发起 Pull Request，等待 review。
6. 如果遇到环境相关问题，请提 Issue 并在群内 @管理员。

## 2. 作业说明

本作业基于一个简化的 Unity 练枪仿真器。你将以 POV 视角射击随机出现并平动的、带 MNIST 数字的目标板。

你需要完成三个任务：

- `tasks/task1-aruco`：相机标定与 ArUco 姿态估计（与最终打靶任务独立）
- `tasks/task2-detector`：目标检测与 PnP
- `tasks/task3-tracker`：OpenCV 相机坐标系下的 EKF 跟踪与固定时延打击点预测（C++）

我们提供 Windows / Linux / macOS 的预编译仿真器可执行文件。
仿真器通过 Unity socket 协议向算法客户端发送图像帧，并接收客户端返回的瞄准指令。
协议说明见：`docs/simulator_protocol.md`。

## 3. 环境

### 3.1 安装工具

三种系统都需要安装 `uv`、`cmake` 和 `ctest`。
`ctest` 是 CMake 自带测试命令，通常安装 CMake 后会一起提供。

#### Windows

推荐使用 PowerShell 或 Windows Terminal：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
winget install --id Kitware.CMake -e
winget install Ninja-build.Ninja
```

安装后重新打开终端，检查命令是否可用：

```powershell
uv --version
cmake --version
ctest --version
```

Windows 上统一使用 `Ninja` 生成器。这样 `pytest` 和 `ctest` 都直接复用同一个单配置构建目录。

#### macOS

推荐先安装 Homebrew，然后安装工具：

```bash
brew install uv cmake
```

检查命令是否可用：

```bash
uv --version
cmake --version
ctest --version
```

#### Ubuntu

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt update
sudo apt install -y cmake build-essential
```

安装后如果当前终端找不到 `uv`，请重新打开终端，或执行：

```bash
source ~/.bashrc
```

检查命令是否可用：

```bash
uv --version
cmake --version
ctest --version
```

### 3.2 Workflow

#### 3.2.1 配环境

先安装 Python 依赖：

```bash
uv sync --extra vision --extra train --extra dev
```

再初始化 C++ 构建目录。

Windows：

```powershell
cmake -S . -B build/hw-ninja -G Ninja -DHW_BUILD_TESTS=ON
cmake --build build/hw-ninja
```

macOS / Linux：

```bash
cmake -S . -B build/hw -DHW_BUILD_TESTS=ON
cmake --build build/hw
```

#### 3.2.2 测试
写完code之后，可以先做一点测试：

```bash
uv run pytest
```

`pytest` 会自动确保 Task 3 的 C++ 目标已构建。
Task 2 的真实 MNIST 训练测试默认跳过；如需显式运行，可使用 `uv run pytest --run-task2-training`。

#### 3.2.3 查看实现效果

先启动对应平台的预编译 Unity 仿真器：

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

然后启动客户端：

```bash
uv run python simulator/runner.py
```

## 4. 作业要求
通过向仓库提交PR的方式完成作业。

1. Pull Request **标题**请使用：`姓名 - 学号`。PR description 请按照我们提供的模板的TODO中的要求写。请注意 Git 提交规范，保持提交记录清晰。
2. **不要上传敏感信息**（如 API 密钥、密码等）。

## 5. 有关 LLM 使用

本作业的基本实现采用代码补全形式，在需要实现的位置提供了较详细伪代码和注释，即使不借助LLM也很容易上手，所以我们不建议用LLM直接生成代码。我们不会做强制的 AI 检测，不过你必须要知道自己在写什么。

<div align="center"><b>👋 欢迎线下线上的交流讨论</b></div>
