#!/bin/bash
g++ getMesurment.cpp -Wno-unused-result -g -O3 -o run.out 
chown root run.out
chmod u+s run.out

chmod +x main.py

echo 17 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio17/direction
echo 0 > /sys/class/gpio/gpio17/value
chmod 777 /sys/class/gpio/gpio17/value