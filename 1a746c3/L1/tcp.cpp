#include <vector>
#include <cassert>

struct mavlink_status_t
{
  int packet_rx_success_count;
  int packet_rx_drop_count;
  int buffer_overrun;
  int parse_error;

  mavlink_status_t() : mavlink_status_t(0, 0, 0, 0) { }
  mavlink_status_t(int packet_rx_success_count, int packet_rx_drop_count, int buffer_overrun, int parse_error)
    : packet_rx_success_count(packet_rx_success_count),
      packet_rx_drop_count(packet_rx_drop_count),
      buffer_overrun(buffer_overrun),
      parse_error(parse_error) { }
};



int main()
{
  // TODO: allow users to provide stats via the arg. list?
  std::vector<mavlink_status_t> stats_per_client;
  stats_per_client.emplace_back(1, 2, 4, 8);
  stats_per_client.emplace_back(1, 2, 4, 8);
  stats_per_client.emplace_back(0, 0, 0, 0);

  // aggregate the stats for each client in the list
  mavlink_status_t agg;
  for (auto c : stats_per_client) {
    agg.packet_rx_success_count = c.packet_rx_success_count; // should be +=
    agg.packet_rx_drop_count = c.packet_rx_drop_count; // ""
    agg.buffer_overrun = c.buffer_overrun; // ""
    agg.parse_error = c.parse_error; // ""
  }

  assert(agg.packet_rx_success_count == 2);
  assert(agg.packet_rx_drop_count == 4);
  assert(agg.buffer_overrun == 8);
  assert(agg.parse_error == 16);

  return 0;
}
