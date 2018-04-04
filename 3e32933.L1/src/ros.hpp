#include <string>
#include <stdexcept>

/**
 * This is a mock of the ROS API that C++ developers use.
 * It allows for the creation of a mock Publisher and Subscriber,
 * and it will throw an error whenever the Publisher and Subscriber
 * topics do not match.
 *
 * For simplicity of implementation, call subscribe prior to advertise.
 */

namespace ros {
typedef std::string Message;

class Publisher {
public:
    Publisher(const bool topic_mismatch);
    void publish(const Message &message);

    bool topic_mismatch_;
};

Publisher::Publisher(const bool topic_mismatch)
    : topic_mismatch_(topic_mismatch) {}

void Publisher::publish(const Message &message) {
    if (topic_mismatch_) {
        throw std::runtime_error("publishing to a topic with no subscribers");
    }
}

class Subscriber {
public:
    Subscriber() {}
};

class NodeHandle {
public:
    NodeHandle() {}
    Publisher advertise(const std::string &topic, unsigned int queue_size, bool latch=false);
    Subscriber subscribe(const std::string &topic, unsigned int queue_size, void(*fp)(Message));

private:
    std::string sub_topic_;
};

Publisher NodeHandle::advertise(const std::string &topic, unsigned int queue_size,
                                bool latch) {
    Publisher pub(topic != sub_topic_);
    return pub;
}

Subscriber NodeHandle::subscribe(const std::string &topic, unsigned int queue_size,
                                 void(*fp)(Message)) {
    sub_topic_ = topic;
    Subscriber sub;
    return sub;
}
};