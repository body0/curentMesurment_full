#!/bin/bash
g++ getMesurment.cpp -g -O3 -o run.out 
chown root run.out
chmod u+s run.out