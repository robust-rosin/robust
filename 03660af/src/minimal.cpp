// uses C++11

#include <chrono>
#include <atomic>
#include <thread>

/**
 * The original code does not use any kind of counter to determine
 * how many writers have access to the shared resource.
 * It is just a helper mechanism for this simplified version to be able
 * to report an error under the right circumstances.
 */

std::atomic_int writers;

void foo(int ms) {
    while (writers++ == 0) {
        // using sleep to mock a write to a serial port
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
        writers--;
    }
    throw std::runtime_error("concurrent access to resource without synchronization");
}

int main(int argc, char ** argv) {
    writers = 0;
    std::thread t1 (foo, 15);
    std::thread t2 (foo, 42);
    t1.join();
    t2.join();
    return 1;
}
