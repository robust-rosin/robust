/**
 * This is a simplification of part 1 of the reported bug.
 * When Ctrl+C was pressed to issue graceful termination, the
 * program crashed if it was waiting for another node to be present.
 * It did not have the proper exception handler for sleep interruptions.
 */

#include "ros.hpp"

int main(int argc, char **argv) {
    ros::Publisher enable_publisher;
    ecl::MilliSleep millisleep;
    bool connected = false;
    while (!connected) {
        if (enable_publisher.getNumSubscribers() > 0) {
            connected = true;
        } else {
            // ROS_WARN KeyOp: could not connect, trying again after 500ms...
            millisleep(500);
        }
    }
    return 1;
}
