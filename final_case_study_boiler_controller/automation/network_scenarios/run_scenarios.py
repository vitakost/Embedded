import os
import sys
import threading
import time
from datetime import datetime

import serial

PORT = os.getenv("DEVICE_PORT", "rfc2217://localhost:4000")
RUN = sys.argv[1] if len(sys.argv) > 1 else "1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence")


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


class Monitor:
    def __init__(self, port):
        self.ser = serial.serial_for_url(port, baudrate=115200, timeout=0.05)
        self.lock = threading.Lock()
        self.log = None
        self.stop = False
        self.buf = b""
        self.t = threading.Thread(target=self._reader, daemon=True)
        self.t.start()

    def _write(self, line):
        with self.lock:
            if self.log:
                self.log.write(line + "\n")
                self.log.flush()

    def _reader(self):
        while not self.stop:
            data = self.ser.read(512)
            if not data:
                continue
            self.buf += data
            while b"\n" in self.buf:
                line, self.buf = self.buf.split(b"\n", 1)
                text = line.decode(errors="replace").rstrip("\r")
                if text:
                    self._write(f"{ts()} < {text}")

    def open(self, name):
        with self.lock:
            if self.log:
                self.log.close()
            self.log = open(os.path.join(OUT, f"run{RUN}_{name}.log"), "w", encoding="utf-8")

    def cmd(self, command, wait=1.0):
        self._write(f"{ts()} > {command}")
        self.ser.write((command + "\n").encode())
        self.ser.flush()
        time.sleep(wait)

    def close(self):
        time.sleep(0.5)
        self.stop = True
        self.t.join()
        with self.lock:
            if self.log:
                self.log.close()
                self.log = None
        self.ser.close()


def settle(m):
    m.cmd("NET UP", 6)
    m.cmd("RESET STATS", 1)


def scenario_a(m):
    m.open("A_connection_loss")
    settle(m)
    m.cmd("STATUS")
    m.cmd("NET DOWN", 15)
    m.cmd("STATUS")
    m.cmd("NET UP", 6)
    m.cmd("STATUS")


def scenario_buffer(m, name, n):
    m.open(name)
    settle(m)
    m.cmd("STATUS")
    m.cmd("NET DOWN", 1.5)
    for _ in range(n):
        m.cmd("SEND", 0.8)
    m.cmd("BUFFER")
    m.cmd("STATUS")
    m.cmd("NET UP", 8)
    m.cmd("STATUS")
    m.cmd("BUFFER")


def scenario_reconnect20(m):
    m.open("E_reconnect_x20")
    settle(m)
    m.cmd("STATUS")
    for _ in range(20):
        m.cmd("NET DOWN", 3)
        m.cmd("NET UP", 4)
        m.cmd("STATUS")


def scenario_d(m):
    m.open("D_stress_memory")
    settle(m)
    m.cmd("STATUS")
    for _ in range(10):
        m.cmd("STRESS 100", 6)
        m.cmd("STATUS")
    m.cmd("RESET STATS")
    m.cmd("STATUS")


def scenario_send_heap(m):
    m.open("F_send_heap")
    settle(m)
    m.cmd("STATUS")
    for _ in range(20):
        m.cmd("SEND", 0.6)
    m.cmd("STATUS")
    m.cmd("NET DOWN", 1.5)
    m.cmd("STRESS 20", 4)
    m.cmd("BUFFER")
    m.cmd("STATUS")
    m.cmd("NET UP", 8)
    m.cmd("STATUS")


def main():
    os.makedirs(OUT, exist_ok=True)
    m = Monitor(PORT)
    time.sleep(0.5)
    steps = [
        ("A", scenario_a),
        ("B", lambda m: scenario_buffer(m, "B_offline_buffer_5", 5)),
        ("C8", lambda m: scenario_buffer(m, "C_boundary_8", 8)),
        ("C9", lambda m: scenario_buffer(m, "C_boundary_9", 9)),
        ("C12", lambda m: scenario_buffer(m, "C_overflow_12", 12)),
        ("E", scenario_reconnect20),
        ("D", scenario_d),
        ("F", scenario_send_heap),
    ]
    only = sys.argv[2:] if len(sys.argv) > 2 else None
    try:
        for key, fn in steps:
            if only and key not in only:
                continue
            print(f"run {RUN}: scenario {key} ...", flush=True)
            fn(m)
    finally:
        m.close()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
