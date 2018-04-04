#include <cstdio>
#include <cstring>

// The bug is exhibited when running this program for instance with the
// following command line arguments "1 2 3 4 5 6 7 7"

int main(int argc, char ** argv)
{

  if(argc == 10)
  {
    if (strcmp(argv[8], argv[9]) == 0)
    {
      printf("target_frame and source frame are the same (%s, %s) this cannot work", argv[8], argv[9]);
      return 1;
    }

    return 0;

  } else if (argc == 9) {

    if (strcmp(argv[7], argv[8]) == 0)
    {
      printf("target_frame and source frame are the same (%s, %s) this cannot work", argv[8], argv[9]); // <-- ERROR
      return 1;
    }

    return 0;

  } else return -1;

}

