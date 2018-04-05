#include <string>
#include <stdexcept>
#include "param_reader.hpp"

/** This is a mock of the ROS API that C++ developers use. */

namespace ros {
class NodeHandle {
public:
    NodeHandle() {}
    void readLaunch(const std::string &filename);
    bool param(const std::string &param_name, double &param_val,
        const double &default_val) const;

private:
    M_param param_;
};

void NodeHandle::readLaunch(const std::string &filename) {
    ParamReader reader;
    M_param *params = reader.parseLaunch(filename.c_str());
    if (!params) {
        throw std::runtime_error("launch file not found");
    }
    param_ = *params;
}

bool NodeHandle::param(const std::string &param_name,
        double &param_val, const double &default_val) const {
    M_param::const_iterator it = param_.find(param_name);
    if (it != param_.end()) {
        param_val = std::atof(it->second.second.c_str());
        return true;
    }
    param_val = default_val;
    return false;
}
};
