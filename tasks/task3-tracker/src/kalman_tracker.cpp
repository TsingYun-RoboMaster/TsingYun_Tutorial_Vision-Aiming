#include "kalman_tracker.hpp"

#include <stdexcept>

namespace hw
{
    KalmanTracker::KalmanTracker() = default;

    bool KalmanTracker::isTracking() const
    {
        return tracking_;
    }

    void KalmanTracker::reset()
    {
        tracking_ = false;
        x_ = AxisFilter{};
        y_ = AxisFilter{};
        z_ = AxisFilter{};
    }

    void KalmanTracker::AxisFilter::reset(double measured_position)
    {
        position = measured_position;
        velocity = 0.0;
        p00 = 1.0;
        p01 = 0.0;
        p10 = 0.0;
        p11 = 1.0;
    }

    void KalmanTracker::AxisFilter::predict(double dt, double process_noise)
    {
        // TODO(student): Implement the constant-velocity Kalman predict step.
        // dt = max(dt, 0)
        // position = position + velocity * dt
        // F = [[1, dt],
        //      [0, 1]]
        // Q = process_noise * [[dt^4 / 4, dt^3 / 2],
        //                      [dt^3 / 2, dt^2]]
        // P = F * P * F^T + Q
        // store the updated position, velocity, and covariance
        throw std::logic_error("NotImplementedError: KalmanTracker::AxisFilter::predict");
    }

    void KalmanTracker::AxisFilter::update(double measured_position, double measurement_noise)
    {
        // TODO(student): Implement the 1D position measurement update step.
        // residual = measured_position - position
        // H = [1, 0]
        // S = H * P * H^T + measurement_noise
        // if S is not positive:
        //     return without updating
        // K = P * H^T / S
        // position = position + K[0] * residual
        // velocity = velocity + K[1] * residual
        // P = (I - K * H) * P
        throw std::logic_error("NotImplementedError: KalmanTracker::AxisFilter::update");
    }

    TrackState KalmanTracker::update(const Vec3 &measurement, double dt)
    {
        // TODO(student): Update tracker state from one measured 3D point.
        // if tracker is not initialized:
        //     initialize x, y, z filters with measurement components
        //     set all velocities to zero
        //     mark tracker as active
        //     return current state
        // predict each axis filter using dt
        // update each axis filter with its measured coordinate
        // return position, velocity, and tracking flag
        throw std::logic_error("NotImplementedError: KalmanTracker::update");
    }

    TrackState KalmanTracker::predict(double dt)
    {
        // TODO(student): Predict target state when a detection is missing.
        // if tracker is not active:
        //     return a non-tracking state
        // predict x, y, z filters with dt
        // return predicted position and velocity
        throw std::logic_error("NotImplementedError: KalmanTracker::predict");
    }

    TrackState KalmanTracker::stateFromFilters() const
    {
        return {
            true,
            {x_.position, y_.position, z_.position},
            {x_.velocity, y_.velocity, z_.velocity},
        };
    }
} // namespace hw
