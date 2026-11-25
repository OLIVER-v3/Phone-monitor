# PhoneMonitor v0.1
## 1) Virtual monitor (so you can drag windows)
Install Virtual-Display-Driver (github.com/VirtualDrivers/Virtual-Display-Driver), set Win+P = Extend,
set resolution to match phone (e.g. 2400x1080).
## 2) PC
cd server; pip install -r requirements.txt; start_usb.bat   (monitor index 1 = virtual display)
## 3) Phone
Open android/ in Android Studio -> Run. Enable USB debugging, plug cable.
Wi-Fi mode: set host in MainActivity.kt to PC IP, run server.py without adb reverse.

## Build on GitHub
Push to a repo -> Actions tab -> download artifacts:
- PhoneMonitor-apk (app-debug.apk, install on phone)
- PhoneMonitor-server-exe (PhoneMonitorServer.exe, run with: PhoneMonitorServer.exe --monitor 1)
