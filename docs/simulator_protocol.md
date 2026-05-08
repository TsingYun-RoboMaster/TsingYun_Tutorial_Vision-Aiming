# Unity 仿真器 Socket 协议

规定培训仓库当前使用的 Unity 仿真器通信协议。

## 连接

- Host: `127.0.0.1`
- Port: `50000`
- Transport: TCP
- Framing: 每条 JSON 消息占一行，以 `\n` 结尾
- Encoding: UTF-8

客户端先连接 Unity 仿真器，再发送 `start` 消息。Unity 返回 `config` 消息告知本局参数，然后开始推送 `frame` 消息，客户端对每帧返回 `aim` 消息。游戏结束后 Unity 发送 `end` 消息。

## 消息

### `start`

方向：客户端到 Unity。

```json
{
  "type": "start",
  "seed": 12345,
  "latency": 0.05,
  "cameraMatrix": [
    960.0, 0.0, 640.0,
    0.0, 960.0, 360.0,
    0.0, 0.0, 1.0
  ]
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 固定为 `start` |
| `seed` | int | 随机种子，用于复现同一局目标生成 |
| `cameraMatrix` | number[9] | 相机内参矩阵，按行展开 |

### `config`

方向：Unity 到客户端。Unity 收到 `start` 后立即发送，之后才开始推送 `frame`。

```json
{
  "type": "config",
  "boardWidth": 0.4,
  "boardHeight": 0.2
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 固定为 `config` |
| `boardWidth` | number | 目标板物理宽度，单位米 |
| `boardHeight` | number | 目标板物理高度，单位米 |

### `frame`

方向：Unity 到客户端。

```json
{
  "type": "frame",
  "frameId": 1,
  "timestamp": 1.234,
  "imageBase64": "..."
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 固定为 `frame` |
| `frameId` | int | 帧编号 |
| `timestamp` | number | 帧时间戳，单位秒，以游戏开始时刻为零点 |
| `imageBase64` | string | 当前画面 JPEG 图片字节的 base64 编码 |

### `aim`

方向：客户端到 Unity。

```json
{
  "type": "aim",
  "x": 0.0,
  "y": 0.0,
  "z": 10.0,
  "detections": [
    {
      "classId": 3,
      "confidence": 0.95,
      "bbox": { "x": 120.0, "y": 78.0, "width": 112.0, "height": 92.0 },
      "corners": [[125.0, 83.0], [225.0, 83.0], [225.0, 163.0], [125.0, 163.0]],
      "position": { "x": -4.5, "y": -1.0, "z": 31.2 }
    }
  ]
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 固定为 `aim` |
| `x` | number | 目标点在相机坐标系下的 X（右为正，单位米），同时也是准星位置 |
| `y` | number | 目标点在相机坐标系下的 Y（下为正，单位米），同时也是准星位置 |
| `z` | number | 目标点在相机坐标系下的 Z（前为正，单位米），同时也是准星位置 |
| `detections` | array | （可选）当前帧所有目标检测结果，用于 Unity 端可视化调试 |
| `detections[].classId` | int | MNIST 数字类别 0-9，-1 表示未知 |
| `detections[].confidence` | number | 分类置信度 0-1 |
| `detections[].bbox` | object | 图像坐标系下的轴对齐包围框 `{x, y, width, height}`，单位像素 |
| `detections[].corners` | number[4][2] | 目标板四角点，顺序 LU, RU, RD, LD，单位像素 |
| `detections[].position` | object | 目标板在相机坐标系下的三维位置 `{x, y, z}`，单位米 |

坐标系约定：客户端直接输出相机坐标系三维点 `(x, y, z)`。Unity 端负责将该点转换到世界坐标并执行射击。

### `end`

方向：Unity 到客户端。

```json
{
  "type": "end",
  "score": 10,
  "accuracy": 0.5,
  "average_to_center_distance": 12.3
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | string | 固定为 `end` |
| `score` | number | 最终得分 |
| `accuracy` | number | 命中率 |
| `average_to_center_distance` | number | 平均中心距离，越小越好 |

