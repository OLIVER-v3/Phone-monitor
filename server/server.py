# PhoneMonitor server (Windows). pip install -r requirements.txt
# Run:  python server.py --monitor 2 --fps 60 --quality 70
import socket, struct, threading, argparse, time, ctypes
import dxcam, cv2
from screeninfo import get_monitors

p = argparse.ArgumentParser()
p.add_argument("--monitor", type=int, default=1, help="monitor index (0=main, 1=second/virtual)")
p.add_argument("--fps", type=int, default=60)
p.add_argument("--quality", type=int, default=70)
p.add_argument("--scale", type=float, default=1.0)
p.add_argument("--port", type=int, default=5555)
a = p.parse_args()

ctypes.windll.user32.SetProcessDPIAware()
mon = get_monitors()[a.monitor]
MX, MY, MW, MH = mon.x, mon.y, mon.width, mon.height
print(f"Monitor {a.monitor}: {MW}x{MH} at ({MX},{MY})")

user32 = ctypes.windll.user32
def move(nx, ny): user32.SetCursorPos(int(MX + nx * MW), int(MY + ny * MH))
def mouse(flag): user32.mouse_event(flag, 0, 0, 0, 0)
DOWN, UP = 0x0002, 0x0004

def recv_touch(conn):
    # packet: 1 byte action (0 down,1 move,2 up) + float x + float y (0..1)
    buf = b""
    while True:
        d = conn.recv(1024)
        if not d: break
        buf += d
        while len(buf) >= 9:
            act, x, y = struct.unpack("!Bff", buf[:9]); buf = buf[9:]
            move(x, y)
            if act == 0: mouse(DOWN)
            elif act == 2: mouse(UP)

srv = socket.socket(); srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", a.port)); srv.listen(1)
print("Waiting for phone... (USB: adb reverse tcp:%d tcp:%d)" % (a.port, a.port))
while True:
    conn, _ = srv.accept(); conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print("Phone connected")
    threading.Thread(target=recv_touch, args=(conn,), daemon=True).start()
    cam = dxcam.create(output_idx=a.monitor, output_color="BGR")
    cam.start(target_fps=a.fps)
    try:
        while True:
            f = cam.get_latest_frame()
            if a.scale != 1.0: f = cv2.resize(f, None, fx=a.scale, fy=a.scale)
            ok, j = cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, a.quality])
            conn.sendall(struct.pack("!I", len(j)) + j.tobytes())
    except Exception as e:
        print("Disconnected:", e)
    finally:
        cam.stop(); del cam; conn.close()
