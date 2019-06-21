/*  ********************************************* 
 *  Helmholtz Cage Magnetometer Sketch
 *  
 *  Based on SparkFun_MAG3110_Basic.ino
 *  Originally created by George B. for SparkFun Electronics
 *  on Sep 22, 2016
 *  
 *  Original Code License:
 *  This code is beerware; if you see me (or any other SparkFun employee) at the
 *  local, and you've found our code helpful, please buy us a round!
 *  Distributed as-is; no warranty is given.
 *  *********************************************/

#include <SparkFun_MAG3110.h>

MAG3110 mag = MAG3110(); //Instantiate MAG3110

void setup() {
  Serial.begin(9600);

  mag.initialize(); //Initializes the mag sensor
  mag.start();      //Puts the sensor in active mode
}

void loop() {

  int x, y, z;
  float xg, yg, zg;
  //Only read data when it's ready
  if(mag.dataReady()) {
    //Read the data
    mag.readMag(&x, &y, &z);

    //Convert to gauss
    xg = 0.001*x;
    yg = 0.001*y;
    zg = 0.001*z;   
  
    Serial.print("X: ");
    Serial.print(xg);
    Serial.print(", Y: ");
    Serial.print(yg);
    Serial.print(", Z: ");
    Serial.println(zg);
  
    Serial.println("--------");
  }
}
