#!/bin/bash
g++ getMesurment.cpp -g -O3 -o run.out 
chown root run.out
chmod u+s run.out

chmod +x main.py

echo 17 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio17/direction
chmod 777 /sys/class/gpio/gpio17/value