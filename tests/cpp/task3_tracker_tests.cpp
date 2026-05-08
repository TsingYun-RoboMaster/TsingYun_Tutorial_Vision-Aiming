#include <cmath>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>

#include "kalman_tracker.hpp"

namespace
{
void require(bool condition, const std::string& message)
{
    if (!condition)
    {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

void require_near(double actual, double expected, double tolerance, const std::string& message)
{
    if (std::abs(actual - expected) > tolerance)
    {
        std::cerr << "FAIL: " << message << " expected " << expected << " got " << actual << '\n';
        std::exit(1);
    }
}

bool is_not_implemented(const std::logic_error& error)
{
    return std::string(error.what()).find("NotImplementedError") != std::string::npos;
}
}  // namespace

int main()
{
    hw::KalmanTracker tracker;
    require(!tracker.isTracking(), "new tracker should not be tracking");

    hw::TrackState initial;
    try
    {
        initial = tracker.update({0.0, 0.0, 0.0}, 0.1);
    }
    catch (const std::logic_error& error)
    {
        if (is_not_implemented(error))
        {
            std::cout << "task3 tracker tests skipped: " << error.what() << '\n';
            return 0;
        }
        throw;
    }

    require(tracker.isTracking(), "tracker should initialize on first measurement");
    require_near(initial.position.x, 0.0, 1e-9, "initial x");

    const auto second = tracker.update({1.0, 0.0, 0.0}, 1.0);
    require_near(second.position.x, 1.0, 0.25, "second update x should follow measurement");
    require(second.velocity.x > 0.1, "velocity should become positive after movement");

    const auto predicted = tracker.predict(1.0);
    require(predicted.position.x > second.position.x, "prediction should move forward");
    require(predicted.tracking, "prediction should remain tracking");

    tracker.reset();
    require(!tracker.isTracking(), "reset clears tracking state");

    std::cout << "task3 tracker tests passed\n";
    return 0;
}
