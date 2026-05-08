# Task 2 Theory：目标检测、数字分类与 PnP

## 1 bbox检测
bbox是bounding box的简称，指的是目标在图像中的矩形框。`detect_bbox(...)` 的输入是一张图片，输出是一个候选角点序列，每组四个角点对应一个候选目标板。这一步可以使用传统OpenCV处理方法来做：

1. 把输入图片转换成OpenCV的uint8格式数组。
2. 根据颜色阈值把红色边框的像素筛选出来，得到一个二值图像。
3. 对二值图像做轮廓检测，找到所有闭合的轮廓。
4. 遍历每个轮廓，用 `cv2.approxPolyDP` 近似成一个多边形，如果多边形的边数不是4，或者不是凸的，或者面积/长宽比不合理，就丢弃这个轮廓。
5. 对剩下的多边形，按照左上、右上、右下、左下的顺序把四个角点排序好，放到候选角点序列里。

## 2 角点排序
要得到目标的完整姿态，需要知道目标板四个角点，并且知道真实目标板的尺寸。

例如目标板真实宽度为 $w$，高度为 $h$。可以在目标板自己的局部坐标系中定义四个三维角点：

$P_1 = (-\frac{w}{2}, -\frac{h}{2}, 0)$

$P_2 = (\frac{w}{2}, -\frac{h}{2}, 0)$

$P_3 = (\frac{w}{2}, \frac{h}{2}, 0)$

$P_4 = (-\frac{w}{2}, \frac{h}{2}, 0)$

图像中对应四个角点为 $p_1, p_2, p_3, p_4$。`detect_bbox(...)` 只负责找出这些候选角点，返回一个角点序列。它不做数字分类，也不做 PnP。

## 3 数字检测
`crop_bbox(...)` 是 helper，不是 TODO。它接收原图和 `detect_bbox(...)` 返回的角点序列，按每组角点的外接矩形从原图裁出一批候选图像。`detect_mnist_board(...)` 再对这批 crop 做分类和过滤。流程应为：

1. 调用 `detect_bbox(...)` 得到候选角点序列。
2. 调用 `crop_bbox(...)` 从原图裁出候选 crop batch。
3. 对每个 crop 调用 `model.py` 中的推理入口。
4. 在函数内部定义一个置信度阈值，过滤掉低置信度候选。
5. 输出有效 `Detection` 对象序列，此时 `rvec` 和 `tvec` 仍为空。

模型应当输出每一类的概率：

$p = [p_0, p_1, ..., p_9]$

那么预测类别为：

$class\_id = \arg\max_i p_i$

置信度为：

$confidence = \max_i p_i$

训练代码放在 `tasks/task2-detector/src/train.py`。这个脚本应该读取带标签的 MNIST 目标板裁剪图，训练模型，并保存到 `tasks/task2-detector/models/` 之类的位置。运行仿真器或测试时，`detector.py` 只做推理，不重新训练模型。

如果你使用 PyTorch 训练分类器，请安装训练依赖：

```bash
uv sync --extra vision --extra train --extra dev
```

`train.py` 中的 `select_training_device(...)` 应该自动检查加速器：优先使用 CUDA，其次使用 Apple Silicon 的 MPS，最后回退到 CPU。模型、batch 和 loss 计算都应该放到这个函数返回的 device 上。
