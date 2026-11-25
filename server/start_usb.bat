@echo off
adb reverse tcp:5555 tcp:5555
python server.py --monitor 1 --fps 60 --quality 70
