#include <vector>

#define MAVLINK_COMM_NUM_BUFFERS 4

/** Note the bug: the loop should use `<` instead of `<=`. */

namespace MAVConnInterface {
int new_channel(std::vector<int> &allocated_channels) {
    for (int chan = 0; chan <= MAVLINK_COMM_NUM_BUFFERS; chan++) {
        if (allocated_channels.at(chan) == 0) {
            allocated_channels[chan]++;
            return chan;
        }
    }
    return -1;
}
};

int main(int argc, char **argv) {
    std::vector<int> allocated_channels(MAVLINK_COMM_NUM_BUFFERS);
    for (int i = 0; i < allocated_channels.size(); ++i)
        allocated_channels[i] = 1;
    
// ---- Buggy code
    int chan = MAVConnInterface::new_channel(allocated_channels);
// -----------------

    return chan >= MAVLINK_COMM_NUM_BUFFERS;
}
