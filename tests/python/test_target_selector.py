from __future__ import annotations

import pytest

from detector import BoundingBox, Detection
from simulator_client.target_selector import TargetSelector


def _detection(class_id: int, confidence: float) -> Detection:
    return Detection(
        class_id=class_id,
        confidence=confidence,
        bbox=BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0),
        corners=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)),
    )


class TestTargetSelector:
    def test_new_selector_is_not_tracking(self):
        selector = TargetSelector()
        assert not selector.is_tracking
        assert selector.tracking_digit is None

    def test_empty_detections_returns_none(self):
        selector = TargetSelector()
        assert selector.select([]) is None

    def test_first_detection_acquires_largest_digit_above_threshold(self):
        selector = TargetSelector()
        d0 = _detection(3, 0.8)
        d1 = _detection(7, 0.95)
        d2 = _detection(1, 0.6)
        d3 = _detection(9, 0.7)

        result = selector.select([d0, d1, d2, d3])
        assert result is d3
        assert selector.is_tracking
        assert selector.tracking_digit == 9

    def test_locks_onto_acquired_digit(self):
        selector = TargetSelector()
        # Largest digit (5) is acquired, then we lock onto 5
        selector.select([_detection(3, 0.9), _detection(5, 0.7)])

        d3_new = _detection(3, 0.6)
        d5_new = _detection(5, 0.95)
        result = selector.select([d3_new, d5_new])

        assert result is d5_new
        assert selector.tracking_digit == 5

    def test_returns_none_on_mismatch_but_keeps_lock(self):
        selector = TargetSelector(lost_threshold=3)
        selector.select([_detection(4, 0.9)])

        result = selector.select([_detection(7, 0.99)])
        assert result is None
        assert selector.is_tracking
        assert selector.tracking_digit == 4

    def test_releases_lock_after_threshold_misses(self):
        selector = TargetSelector(lost_threshold=2)
        selector.select([_detection(4, 0.9)])

        selector.select([_detection(9, 0.9)])
        selector.select([_detection(9, 0.9)])
        selector.select([_detection(9, 0.9)])

        assert not selector.is_tracking

    def test_reacquires_after_release(self):
        selector = TargetSelector(lost_threshold=1)
        selector.select([_detection(4, 0.9)])
        selector.select([])
        selector.select([])

        result = selector.select([_detection(2, 0.8)])
        assert result is not None
        assert result.class_id == 2
        assert selector.tracking_digit == 2

    def test_picks_highest_confidence_among_same_digit(self):
        selector = TargetSelector()
        selector.select([_detection(5, 0.7)])

        best = _detection(5, 0.99)
        ok = _detection(5, 0.6)
        result = selector.select([ok, best])
        assert result is best

    def test_tie_on_digit_breaks_by_confidence(self):
        selector = TargetSelector()
        d0 = _detection(8, 0.7)
        d1 = _detection(8, 0.95)

        result = selector.select([d0, d1])
        assert result is d1
        assert selector.tracking_digit == 8

    def test_ignores_unknown_when_known_above_threshold_exists(self):
        selector = TargetSelector()
        unknown = _detection(-1, 0.99)
        known = _detection(3, 0.5)

        result = selector.select([unknown, known])
        assert result is known
        assert selector.tracking_digit == 3

    def test_returns_none_when_no_known_digits(self):
        selector = TargetSelector()
        d0 = _detection(-1, 0.7)
        d1 = _detection(-1, 0.9)

        result = selector.select([d0, d1])
        assert result is None
        assert selector.tracking_digit is None

    def test_returns_none_when_no_detection_above_threshold(self):
        selector = TargetSelector(min_confidence=0.8)
        d0 = _detection(9, 0.79)
        d1 = _detection(8, 0.5)

        result = selector.select([d0, d1])
        assert result is None
        assert not selector.is_tracking

    def test_reset_clears_state(self):
        selector = TargetSelector()
        selector.select([_detection(6, 0.9)])

        selector.reset()

        assert not selector.is_tracking
        assert selector.tracking_digit is None
