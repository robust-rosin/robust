#include <string>
#include <stdexcept>

/**
 * This is a mock of the ROS API that C++ developers use.
 * It allows for the creation of a mock NodeHandle and parameters.
 * It throws an exception when default values are returned for parameters.
 */

namespace ros {
class NodeHandle {
public:
    NodeHandle() {}
    void setParam(const std::string &key, double d);
    bool param(const std::string &param_name, double &param_val,
        const double &default_val) const;

private:
    std::string param_;
    double value_;
};

void NodeHandle::setParam(const std::string &key, double d) {
    param_ = key;
    value_ = d;
}

bool NodeHandle::param(const std::string &param_name,
        double &param_val, const double &default_val) const {
    if (param_name == param_) {
        param_val = value_;
        return true;
    }
    throw std::runtime_error("param key not found");
    return false;
}
};
