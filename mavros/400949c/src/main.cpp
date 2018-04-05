#include <string>
#include <thread>

namespace utils {
void set_thread_name(std::thread &thd, const std::string &name) {
    thd.joinable(); // something just to access the given reference
}
};

int main(int argc, char **argv) {
    std::thread t([&] () {
        utils::set_thread_name(t, "MAVConnSerial%d");
        // this `t` is local and should not be accessed by the other thread
    });
    return 1;
}
