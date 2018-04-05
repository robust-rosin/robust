#include "ros.hpp"

/**
 * The following macros are mocking <arg> and <remap> tags in a launch file.
 * The intent is to mimic a missing remapping on the subscriber when
 * the "depth_registration" option is set to true (which alters the topic
 * on which image depth data is published).
 */

#define DEPTH_REGISTRATION true
#define DEPTH_TOPIC "/camera/depth/image_raw"
#define DEPTH_REG_TOPIC "/camera/depth_registered/image_raw"

void callback(ros::Message m) {}

int main(int argc, char ** argv) {
    std::string topic = DEPTH_REGISTRATION ? DEPTH_REG_TOPIC : DEPTH_TOPIC;
    ros::NodeHandle n;
    ros::Subscriber sub = n.subscribe(DEPTH_TOPIC, 10, callback);
    ros::Publisher pub = n.advertise(topic, 10);

    pub.publish("image data");
    return 1;
}
