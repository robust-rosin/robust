/**
 * In the original source, `param` is used to provide a default value when
 * the parameter is not found. However, the parameter name was incorrect,
 * meaning that the default value would always be used, even when the intended
 * parameter was set.
 */

#include "ros.hpp"

int main(int argc, char **argv) {
    ros::NodeHandle nh;
    nh.readLaunch("src/params.launch");
    double conn_system_time_d;
    nh.param("conn_system_time", conn_system_time_d, 0.0);
    if (conn_system_time_d == 0.0) {
        throw std::runtime_error("param returned the default value");
    }
    return 0;
}
