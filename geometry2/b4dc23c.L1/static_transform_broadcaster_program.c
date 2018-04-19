#include <stdio.h>
#include <string.h>

// The bug is exhibited when running this program for instance with the
// following command line arguments "1 2 3 4 5 6 7 8"

int main(int argc, char ** argv)
{

  if (argc == 9) { 

    printf("target_frame and source frame are the same (%s, %s) this cannot work", argv[8], argv[9]);
    return 1;

  } 

  return 0;

}

