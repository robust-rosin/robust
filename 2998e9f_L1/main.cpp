#include <iostream>
#include <string>

// From https://github.com/Dronecode/sitl_gazebo/blob/master/include/mavlink/v1.0/common/mavlink_msg_statustext.h
typedef struct
{
 uint8_t severity; /*< Severity of status. Relies on the definitions within RFC-5424. See enum MAV_SEVERITY.*/
 char text[50]; /*< Status text message, without null termination character*/
} mavlink_statustext_t;


int main ()
{

  mavlink_statustext_t textm;
  strcpy(textm.text, "hello ROS");
  std::string text(textm.text, sizeof(textm.text));


  // demo:
  //   std::cout<<text<< ","<< strnlen(textm.text, sizeof(textm.text)) << std::endl;

  return 0;
}
