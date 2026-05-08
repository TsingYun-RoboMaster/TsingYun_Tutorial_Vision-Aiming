# Task 3：OpenCV 坐标系下的 EKF 预测打击点

本任务对应自瞄系统中的跟踪与预测模块。

目标：在 **OpenCV 相机坐标系**（X 右、Y 下、Z 前）中，基于检测结果做 EKF，输出固定时间后的预测打击点 `(x, y, z)`，直接作为协议 `aim` 发送给仿真器。

理论讲解请看 [THEORY.md](THEORY.md)。

## 1. 环境准备

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

## 2. 需要完成

代码位置：

- `tasks/task3-tracker/include/kalman_tracker.hpp`
- `tasks/task3-tracker/src/kalman_tracker.cpp`

必须完成函数：

1. `KalmanTracker::AxisFilter::predict(...)`
2. `KalmanTracker::AxisFilter::update(...)`
3. `KalmanTracker::update(...)`
4. `KalmanTracker::predict(...)`

实现要求：

1. 输入：每帧检测到的三维点（OpenCV 相机坐标系）和 `dt`。
2. 滤波：使用 EKF/线性 Kalman 思路估计当前状态（位置+速度）。
3. 预测：给定固定预测时间 `t_hit`，输出未来打击点位置。
4. 输出：预测点 `(x, y, z)`，供上层直接发送为 `aim`。

## 3. 测试

Windows：

```powershell
ctest --test-dir build/hw-ninja --output-on-failure
```

macOS / Linux：

```bash
ctest --test-dir build/hw --output-on-failure
```

## 4. 调参和优化

如果你的代码已经实现完毕，以下是你可以改动的调参方向：

- `simulator_client/pipeline.py`中`KalmanFilter`类的初始化参数中，有`process_noise`和`measurement_noise`，分别对应理论中提到的`Q`和`R`，你可以调整它们来测试效果。我们预设的参数不一定适合你的代码，调整参数对最终表现会有可观的影响

```python
# TODO: fine-tune your arguments here
self.tracker = KalmanTracker(process_noise=1.0, measurement_noise=0.5)
```

- `simulator_client/target_selector`中的多目标选择逻辑。模拟器是通过击中的数字和击中点到目标中心的距离来评分。一个视野里可能出现多个目标。当前的选板逻辑是选择数字最大的目标，如果相同就选择confidence较大的，即当前代码第54行：

```python
best = max(candidates, key=lambda d: (d.class_id, d.confidence))
```

这样的好处是可以优先打数字大的目标，坏处是可能会导致目标频繁切换，kf拟合不上，你可以探索更优的选板逻辑。例如，在已经锁定目标后，综合考虑切换目标的代价（滤波器拟合不足）和收益（数字更大）

- `simulator_client/pipeline.py`第94行的滤波器reset逻辑。当前滤波器在连续丢失目标后会自动触发reset，但是在目标切换时不会主动reset。切换目标reset的好处是可以快速切换位置，而不会因为滤波器平滑更新而浪费射击时间

**我们保证同一时间内不会出现相同数字的目标，可以通过数字id判断是否reset。但如果频繁识别错数字，实现reset可能会导致频繁重置产生负面影响**

- 在实现完Kalman Filter后，你甚至可以选择其他算法，比如将三维运动作为一个整体向量考虑，甚至更换Filter。如果你在实现中更换了Filter，请至少保证Kalman Filter的实现是正确的，在下面加一个Filter，并且在PR中说明你更换了什么算法，为什么更换，以及更换后效果的变化。记得在`pipeline.py`的初始化里边替换你的新Filter。

## 5. 结语
目前你已经实现了最基本的Detector和Tracker，但是一个完整的自瞄流程不可或缺的就是弹道解算，如果有余力，你可以提前了解以下在自瞄中必须掌握的内容，本次作业不做要求：

1. [tf坐标转换](https://docs.ros.org/en/foxy/Concepts/About-Tf2.html)
2. 无空气阻力的轨迹预测和弹道解算（抛物线模型）
3. MPC（Model Predictive Control）路径规划在自瞄中的应用
