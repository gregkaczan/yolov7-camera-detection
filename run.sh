#!/bin/bash

python3 detect.py --weights yolov7.pt --conf 0.85 --img-size 640 --view-img --source streams.txt