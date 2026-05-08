"""MNIST digit model scaffold for Task 2.

Detector code should call the inference function in this module. Training code
lives in train.py so detector.py stays focused on board detection, corner
geometry, and PnP.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np

RgbPixel = tuple[int, int, int]
ImageLike = np.ndarray

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "mnist_classifier.npz"


def preprocess_mnist_crop(board_crop: ImageLike) -> np.ndarray:
    # TODO(student): Convert a detected board crop into classifier input.
    # if board_crop is empty:
    #     raise a clear error
    # grayscale = zero array with crop height and width
    # for each pixel in board_crop:
    #     grayscale[y][x] = weighted RGB intensity or max channel intensity
    # resize grayscale to 28x28 using your chosen image library
    # normalize values to [0, 1]
    # reshape to the input shape expected by your classifier
    # return normalized input array
    raise NotImplementedError("preprocess_mnist_crop is not implemented")


def load_mnist_model(model_path: Path = DEFAULT_MODEL_PATH) -> object:
    # TODO(student): Load your trained MNIST classifier from disk.
    # if model_path does not exist:
    #     raise a clear error
    # read model weights or serialized estimator from model_path
    # validate that the model can output 10 class scores
    # return the loaded model object
    raise NotImplementedError("load_mnist_model is not implemented")


def predict_mnist_digit(model: object, model_input: np.ndarray) -> tuple[int, float]:
    # TODO(student): Run classifier inference and convert scores to digit/confidence.
    # scores = model.forward(model_input) or equivalent
    # if scores does not contain 10 values:
    #     raise a clear error
    # probabilities = softmax(scores) if the model returns logits
    # digit = argmax(probabilities)
    # confidence = probabilities[digit]
    # return digit, confidence
    raise NotImplementedError("predict_mnist_digit is not implemented")


def classify_mnist_digit(board_crop: ImageLike, model_path: Path = DEFAULT_MODEL_PATH) -> tuple[int, float]:
    # TODO(student): Classify the MNIST digit shown on one detected board crop.
    # model_input = preprocess_mnist_crop(board_crop)
    # model = load_mnist_model(model_path)
    # digit, confidence = predict_mnist_digit(model, model_input)
    # if digit is outside [0, 9]:
    #     raise a clear error
    # if confidence is outside [0, 1]:
    #     raise a clear error
    # return digit, confidence
    raise NotImplementedError("classify_mnist_digit is not implemented")
