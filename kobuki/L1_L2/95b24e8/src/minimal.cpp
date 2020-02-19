#include <stdexcept>

void nanosleep(timespec *req, timespec *rem) {
    throw std::runtime_error("function `nanosleep` from <ctime> is deprecated");
}


int main(int argc, char **argv) {
    timespec millisec;
    millisec.tv_sec = 1;
    millisec.tv_nsec = 0;
    nanosleep(&millisec, NULL);
    return 1;
}
