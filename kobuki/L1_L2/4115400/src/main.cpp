#include <string>
#include <stdexcept>

#define IMU_NAME "kobuki::imu"

namespace sensors {
class Sensor {};

std::string last_name;

Sensor *get_sensor(const std::string &name) {
    if (name == last_name) {
        throw std::runtime_error("requesting a sensor already in use");
    }
    last_name = name;
    Sensor *pointer = new Sensor();
    return pointer;
}
};

int main(int argc, char **argv) {
    sensors::Sensor *imu_for_robot1 = sensors::get_sensor(IMU_NAME);
    sensors::Sensor *imu_for_robot2 = sensors::get_sensor(IMU_NAME);
    return 1;
}
