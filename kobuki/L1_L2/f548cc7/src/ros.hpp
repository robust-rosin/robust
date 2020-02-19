#include<stdexcept>

namespace ros {
class Publisher {
public:
    Publisher() {}

    int getNumSubscribers() {
        return 0;
    }
};
};

namespace ecl {
class MilliSleep {
public:
    MilliSleep() {}

    void operator()(const unsigned long &milliseconds) {
        // this is to mock a Ctrl+C during a sleep
        throw std::runtime_error("Interrupt called during sleep.");
    }
};
};
