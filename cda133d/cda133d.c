#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

void socket_send_int(int x) {
  printf("%d", x);
}

int get_flag(int x) { 
  assert (x<32); // (3) ERROR
  return rand()%2;
}

void send_joint_state() {
  socket_send_int(pow(2,0)*get_flag(0) +
		  pow(2,1)*get_flag(1) + 
		  pow(2,2)*get_flag(2) +
		  pow(2,3)*get_flag(3) +
		  /* ...and so on until 30 */
		  pow(2,31)*get_flag(31) +
		  pow(2,32)*get_flag(32)); // (2)
}

int main() {
  send_joint_state(); // (1) START
}
