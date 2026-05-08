import importlib
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

import model


def call_or_skip_stub(function, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except NotImplementedError as exc:
        pytest.skip(f"student stub is not implemented yet: {exc}")


def test_model_classifier_default_raises_not_implemented():
    digit, confidence = call_or_skip_stub(model.classify_mnist_digit, [[(255, 255, 255)]])
    assert 0 <= digit <= 9
    assert 0.0 <= confidence <= 1.0


def test_detector_uses_model_classifier_for_mnist_inference():
    detector = importlib.import_module("detector")

    assert detector.classify_mnist_digit is model.classify_mnist_digit
    assert not hasattr(detector, "train_mnist_classifier")


def test_training_script_exists_separately_from_detector():
    train_path = Path("tasks/task2-detector/src/train.py")

    assert train_path.exists()


@pytest.mark.task2_training
def test_train_module_exposes_training_entrypoint(tmp_path):
    spec = importlib.util.spec_from_file_location("task2_train", "tasks/task2-detector/src/train.py")
    train = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(train)

    dataset_dir = tmp_path / "data"
    output_path = tmp_path / "model.npz"
    output = call_or_skip_stub(train.train_mnist_classifier, dataset_dir, output_path)
    assert output == output_path


def test_mnist_classifier_scaffold_inherits_nn_module(monkeypatch):
    class FakeModule:
        def __call__(self, inputs):
            return self.forward(inputs)

    class FakeLayer(FakeModule):
        def __init__(self, *args, **kwargs):
            pass

        def forward(self, inputs):
            return inputs

    class FakeSequential(FakeLayer):
        def __init__(self, *layers):
            self.layers = layers

        def forward(self, inputs):
            output = inputs
            for layer in self.layers:
                output = layer(output)
            return output

    class FakeLinear(FakeLayer):
        def __init__(self, in_features, out_features):
            self.out_features = out_features

        def forward(self, inputs):
            batch_size = len(inputs)
            return [[0.0] * self.out_features for _ in range(batch_size)]

    fake_nn = SimpleNamespace(
        Module=FakeModule,
        Sequential=FakeSequential,
        Flatten=FakeLayer,
        Linear=FakeLinear,
        ReLU=FakeLayer,
    )
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(nn=fake_nn))
    monkeypatch.setitem(sys.modules, "torch.nn", fake_nn)

    train = load_train_module()
    classifier = train.MNISTClassifier()

    assert train.nn is fake_nn
    assert isinstance(classifier, fake_nn.Module)
    assert classifier([[1.0], [2.0], [3.0]]) == [[0.0] * 10, [0.0] * 10, [0.0] * 10]


def test_download_mnist_dataset_downloads_train_and_test_splits(monkeypatch, tmp_path):
    calls = []

    class FakeMNIST:
        def __init__(self, root, train, download):
            calls.append((Path(root), train, download))

    fake_torchvision = SimpleNamespace(datasets=SimpleNamespace(MNIST=FakeMNIST))
    monkeypatch.setitem(sys.modules, "torchvision", fake_torchvision)

    train = load_train_module()

    dataset_path = train.download_mnist_dataset(tmp_path)

    assert dataset_path == tmp_path / "MNIST"
    assert calls == [
        (tmp_path, True, True),
        (tmp_path, False, True),
    ]


def test_download_mnist_cli_does_not_run_training(monkeypatch):
    train = load_train_module()
    downloaded = []

    def fake_download(data_dir):
        downloaded.append(data_dir)
        return data_dir / "MNIST"

    def fail_training(dataset_dir, output_path):
        raise AssertionError("download-only command should not run training")

    monkeypatch.setattr(train, "download_mnist_dataset", fake_download)
    monkeypatch.setattr(train, "train_mnist_classifier", fail_training)
    monkeypatch.setattr(sys, "argv", ["train.py", "--download-mnist"])

    train.main()

    assert downloaded == [train.DEFAULT_MNIST_DATA_DIR]


class _FakeAccelerator:
    def __init__(self, available):
        self._available = available

    def is_available(self):
        return self._available


def load_train_module():
    spec = importlib.util.spec_from_file_location("task2_train", "tasks/task2-detector/src/train.py")
    train = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(train)
    return train


def test_select_training_device_prefers_cuda_over_mps():
    train = load_train_module()
    fake_torch = SimpleNamespace(
        cuda=_FakeAccelerator(True),
        backends=SimpleNamespace(mps=_FakeAccelerator(True)),
    )

    assert call_or_skip_stub(train.select_training_device, fake_torch) == "cuda"


def test_select_training_device_uses_mps_when_cuda_is_unavailable():
    train = load_train_module()
    fake_torch = SimpleNamespace(
        cuda=_FakeAccelerator(False),
        backends=SimpleNamespace(mps=_FakeAccelerator(True)),
    )

    assert call_or_skip_stub(train.select_training_device, fake_torch) == "mps"


def test_select_training_device_falls_back_to_cpu():
    train = load_train_module()
    fake_torch = SimpleNamespace(
        cuda=_FakeAccelerator(False),
        backends=SimpleNamespace(mps=_FakeAccelerator(False)),
    )

    assert call_or_skip_stub(train.select_training_device, fake_torch) == "cpu"
