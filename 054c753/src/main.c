/**
* main.c
*
* Created on: 23-Oct-2017
*/


/////////////////////////////////////////////////
// Simplified 054c753.bug                      //
/////////////////////////////////////////////////

#include <stdio.h> // standard input / output functions
#include <fcntl.h> // File control definitions
#include <assert.h>


#define TIMEOUT 100


int open_serial_port(void)
{
	int fd; // file description for the serial port
	
	fd = open("/dev/ttyS0",  O_RDWR | O_NOCTTY | O_NDELAY);
	
	if(fd < 0) // if open is unsucessful
    {
      printf("open_port: Unable to open /dev/ttyS0. \n");
    }
	else
    {
      printf("port is open now.\n");
    }
	
	return(fd);
} //end of open_serial_port


int block(int fd, int timeout){

  assert (fd >=0);
  return 0;
}

int main(){
  int fd;
  block(fd,TIMEOUT);
  fd=open_serial_port();



}
